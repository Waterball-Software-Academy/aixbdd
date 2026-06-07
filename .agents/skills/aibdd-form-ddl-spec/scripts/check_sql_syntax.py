#!/usr/bin/env python3
"""SQL DDL 機械驗證 — aibdd-form-ddl-spec §3 SOP Step 9 機械層 check。

Dialect 由 `<path>` 副檔名 SSOT：
  - `.mysql.sql` → MySQL
  - `.pg.sql`    → PostgreSQL
  - `.mssql.sql` → MSSQL

驗證項：
  1. 副檔名為三者之一
  2. Table 名稱唯一
  3. 每個 FOREIGN KEY 雙端 (table.column) 的 table 存在於本檔
  4. 未使用其他方言獨有語法（dialect drift）：
     - MySQL  : 不得出現 `SERIAL` / `BIGSERIAL` / `IDENTITY(` / `GETDATE(`
     - PG     : 不得出現 `AUTO_INCREMENT` / `IDENTITY(` / `GETDATE(` / `NVARCHAR`
     - MSSQL  : 不得出現 `AUTO_INCREMENT` / `SERIAL` / `BIGSERIAL` / `NOW(`

輸入：DDL 檔路徑（單一）
輸出：JSON {ok, summary, violations[]}（exit 0 = ok=true, exit 1 = ok=false）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# --- regex constants --------------------------------------------------------

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?P<name>\w+)\s*\(",
    re.IGNORECASE,
)
_FK_RE = re.compile(
    r"(?:CONSTRAINT\s+\w+\s+)?FOREIGN\s+KEY\s*\(([^)]+)\)\s*"
    r"REFERENCES\s+(\w+)\s*\(([^)]+)\)",
    re.IGNORECASE,
)
_INLINE_REF_RE = re.compile(
    r"REFERENCES\s+(\w+)\s*\(\w+\)",
    re.IGNORECASE,
)

# Dialect drift keywords. Each entry: pattern → human label.
_DRIFT_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "mysql": [
        (r"\bSERIAL\b", "SERIAL (PG only)"),
        (r"\bBIGSERIAL\b", "BIGSERIAL (PG only)"),
        (r"\bIDENTITY\s*\(", "IDENTITY(...) (MSSQL only)"),
        (r"\bGETDATE\s*\(", "GETDATE() (MSSQL only)"),
    ],
    "pg": [
        (r"\bAUTO_INCREMENT\b", "AUTO_INCREMENT (MySQL only)"),
        (r"\bIDENTITY\s*\(", "IDENTITY(...) (MSSQL only)"),
        (r"\bGETDATE\s*\(", "GETDATE() (MSSQL only)"),
        (r"\bNVARCHAR\b", "NVARCHAR (MSSQL only — use VARCHAR/TEXT)"),
    ],
    "mssql": [
        (r"\bAUTO_INCREMENT\b", "AUTO_INCREMENT (MySQL only)"),
        (r"\bSERIAL\b", "SERIAL (PG only)"),
        (r"\bBIGSERIAL\b", "BIGSERIAL (PG only)"),
        (r"\bNOW\s*\(", "NOW() (MySQL/PG only — use GETDATE())"),
    ],
}

_DIALECT_SUFFIXES = {
    ".mysql.sql": "mysql",
    ".pg.sql": "pg",
    ".mssql.sql": "mssql",
}


# --- helpers ----------------------------------------------------------------


def _resolve_dialect(path: Path) -> str | None:
    name = path.name.lower()
    for suffix, dialect in _DIALECT_SUFFIXES.items():
        if name.endswith(suffix):
            return dialect
    return None


def _strip_block_comments(src: str) -> str:
    return re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)


def _strip_line_comments(src: str) -> str:
    return re.sub(r"--[^\n]*", "", src)


def _extract_table_names(text: str) -> list[str]:
    return [m.group("name") for m in _CREATE_TABLE_RE.finditer(text)]


def _extract_fk_targets(text: str) -> list[tuple[str, str]]:
    """Return [(from_col_or_None, to_table), ...] for both table-level and inline FKs.

    The from-side `from_col` is informational only; table existence is what we check.
    """
    targets: list[tuple[str, str]] = []
    for m in _FK_RE.finditer(text):
        targets.append((m.group(1).strip(), m.group(2)))
    # Inline `REFERENCES other(col)` not already covered by _FK_RE
    seen_spans = {(m.start(), m.end()) for m in _FK_RE.finditer(text)}
    for m in _INLINE_REF_RE.finditer(text):
        if any(start <= m.start() < end for start, end in seen_spans):
            continue
        targets.append(("", m.group(1)))
    return targets


# --- main -------------------------------------------------------------------


def main(path_str: str) -> int:
    path = Path(path_str)
    violations: list[dict] = []

    if not path.exists():
        print(
            json.dumps(
                {
                    "ok": False,
                    "summary": f"file not found: {path_str}",
                    "violations": [{"check": "FILE_EXISTS", "detail": str(path)}],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    dialect = _resolve_dialect(path)
    if dialect is None:
        violations.append(
            {
                "check": "DIALECT_SUFFIX",
                "detail": (
                    f"unsupported suffix on {path.name!r}; "
                    f"expected one of: {', '.join(_DIALECT_SUFFIXES)}"
                ),
            }
        )

    raw = path.read_text(encoding="utf-8")
    src = _strip_line_comments(_strip_block_comments(raw))

    # 1. Unique table names
    tables = _extract_table_names(src)
    seen: set[str] = set()
    for t in tables:
        if t in seen:
            violations.append(
                {"check": "TABLE_UNIQUE", "detail": f"duplicate Table: {t}"}
            )
        seen.add(t)

    table_set = set(tables)

    # 2. FK targets exist within this file
    for from_col, to_table in _extract_fk_targets(src):
        if to_table not in table_set:
            violations.append(
                {
                    "check": "FK_TABLE_EXISTS",
                    "detail": (
                        f"FOREIGN KEY references missing table {to_table!r} "
                        f"(from_col={from_col!r})"
                    ),
                }
            )

    # 3. Dialect drift
    if dialect is not None:
        for pattern, label in _DRIFT_PATTERNS[dialect]:
            for m in re.finditer(pattern, src, re.IGNORECASE):
                line_no = src[: m.start()].count("\n") + 1
                violations.append(
                    {
                        "check": "DIALECT_DRIFT",
                        "detail": (
                            f"dialect={dialect} contains {label}: "
                            f"{m.group(0)!r} at line ~{line_no}"
                        ),
                    }
                )

    ok = len(violations) == 0
    print(
        json.dumps(
            {
                "ok": ok,
                "summary": {
                    "file": str(path),
                    "dialect": dialect,
                    "tables": len(tables),
                    "fk_count": len(_extract_fk_targets(src)),
                    "violations_count": len(violations),
                },
                "violations": violations,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "usage: check_sql_syntax.py <path-to-*.{mysql,pg,mssql}.sql>",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
