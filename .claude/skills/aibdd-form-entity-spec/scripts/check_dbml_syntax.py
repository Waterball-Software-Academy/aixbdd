#!/usr/bin/env python3
"""
DBML 結構機械驗證 — aibdd-entity-analysis Step 5a 機械層 check。

驗證項：
  1. Table / Enum 名稱唯一
  2. 每個 Ref 雙端 (table.column) 的 table 存在於本檔
  3. 每個 Column type 為 enum 名時，該 enum 已宣告
  4. 無 physical leak 關鍵字（index / btree / partition / sharding / shard / fillfactor）

輸入：dbml 檔路徑（單一）
輸出：JSON {ok, summary, violations[]}（exit 0 = ok=true, exit 1 = ok=false）
"""

import json
import re
import sys
from pathlib import Path

PHYSICAL_LEAK_KEYWORDS = [
    r"\bindexes?\b",
    r"\bbtree\b",
    r"\bpartition\b",
    r"\bsharding\b",
    r"\bshard_key\b",
    r"\bfillfactor\b",
    r"\btablespace\b",
]

TABLE_RE = re.compile(r"^\s*Table\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", re.MULTILINE)
ENUM_RE = re.compile(r"^\s*Enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", re.MULTILINE)
REF_RE = re.compile(
    r"^\s*Ref\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*[->]\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)


def strip_block_comments(src: str) -> str:
    return re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)


def strip_line_comments(src: str) -> str:
    return re.sub(r"//[^\n]*", "", src)


def find_columns_with_enum_type(src: str, enum_names: set[str]) -> list[tuple[str, str, str]]:
    """掃描 Table 區塊內的 column type。回傳 [(table_name, col_name, type_token)]"""
    out: list[tuple[str, str, str]] = []
    table_blocks = re.findall(
        r"Table\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}", src, re.DOTALL
    )
    col_re = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE
    )
    for tname, body in table_blocks:
        for col_match in col_re.finditer(body):
            col_name = col_match.group(1)
            col_type = col_match.group(2)
            if col_name.lower() in {"note", "indexes"}:
                continue
            if col_type in enum_names or col_type.endswith("_status") or col_type.endswith("_kind"):
                out.append((tname, col_name, col_type))
    return out


def main(path_str: str) -> int:
    path = Path(path_str)
    if not path.exists():
        print(json.dumps({
            "ok": False,
            "summary": f"file not found: {path_str}",
            "violations": [{"check": "FILE_EXISTS", "detail": str(path)}],
        }, ensure_ascii=False, indent=2))
        return 1

    raw = path.read_text(encoding="utf-8")
    src = strip_block_comments(raw)
    src_no_line_comments = strip_line_comments(src)

    violations: list[dict] = []

    tables = TABLE_RE.findall(src_no_line_comments)
    enums = ENUM_RE.findall(src_no_line_comments)

    seen_t: set[str] = set()
    for t in tables:
        if t in seen_t:
            violations.append({"check": "TABLE_UNIQUE", "detail": f"duplicate Table: {t}"})
        seen_t.add(t)

    seen_e: set[str] = set()
    for e in enums:
        if e in seen_e:
            violations.append({"check": "ENUM_UNIQUE", "detail": f"duplicate Enum: {e}"})
        seen_e.add(e)

    table_set = set(tables)
    for ref in REF_RE.finditer(src_no_line_comments):
        a_t, a_c, b_t, b_c = ref.groups()
        if a_t not in table_set:
            violations.append({
                "check": "REF_TABLE_EXISTS",
                "detail": f"Ref source table missing: {a_t} (in {a_t}.{a_c} -> {b_t}.{b_c})",
            })
        if b_t not in table_set:
            violations.append({
                "check": "REF_TABLE_EXISTS",
                "detail": f"Ref target table missing: {b_t} (in {a_t}.{a_c} -> {b_t}.{b_c})",
            })

    enum_set = set(enums)
    for tname, col, ttype in find_columns_with_enum_type(src_no_line_comments, enum_set):
        looks_like_enum_type = ttype not in {
            "integer", "varchar", "text", "boolean", "decimal", "date", "timestamp",
            "int", "bigint", "smallint", "json", "jsonb", "uuid",
        }
        if looks_like_enum_type and ttype not in enum_set:
            violations.append({
                "check": "ENUM_DECLARED",
                "detail": f"column {tname}.{col} uses undeclared enum type: {ttype}",
            })

    for kw_re in PHYSICAL_LEAK_KEYWORDS:
        for m in re.finditer(kw_re, src_no_line_comments, re.IGNORECASE):
            line_no = src_no_line_comments[: m.start()].count("\n") + 1
            violations.append({
                "check": "NO_PHYSICAL_LEAK",
                "detail": f"physical-leak keyword '{m.group(0)}' at line ~{line_no}",
            })

    ok = len(violations) == 0
    print(json.dumps({
        "ok": ok,
        "summary": {
            "file": str(path),
            "tables": len(tables),
            "enums": len(enums),
            "refs_checked": len(list(REF_RE.finditer(src_no_line_comments))),
            "violations_count": len(violations),
        },
        "violations": violations,
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check_dbml_syntax.py <path-to-logical.dbml>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
