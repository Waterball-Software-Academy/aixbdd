"""Shared DDL parsing helpers for SQL-dialect spec parsers.

Internal — do not import from outside ``shared.spec_parsers``.

The MySQL / Postgres / MSSQL parsers all emit the same `TablePart` /
`RefPart` shape; only the per-dialect column-attribute detectors differ.
This module centralises CREATE TABLE block extraction, constraint parsing
(PRIMARY KEY / FOREIGN KEY), and the per-column line walk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from shared.spec_parts import Column, RefPart, PartKind, TablePart, Part

# ---------------------------------------------------------------------------
# Identifier quoting — MySQL `name`, MSSQL [name], ANSI/PG "name"
# ---------------------------------------------------------------------------

_QO = r"[`\"\[]?"  # optional opening quote
_QC = r"[`\"\]]?"  # optional closing quote
_IDENT_QUOTES = "`[]\""

# schema/db/owner prefix (`public.`, `[dbo].`, `db.schema.`) — strip to bare name,
# matching DBML / unqualified DDL output so part_to_dsl.py needs no change.
_SCHEMA_PREFIX = rf"(?:{_QO}\w+{_QC}\s*\.\s*)*"


def _strip_ident(name: str) -> str:
    return name.strip().strip(_IDENT_QUOTES)


# ---------------------------------------------------------------------------
# CREATE TABLE block extraction (paren-depth aware)
# ---------------------------------------------------------------------------

_CREATE_TABLE_RE = re.compile(
    rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{_SCHEMA_PREFIX}{_QO}(?P<name>\w+){_QC}\s*\(",
    re.IGNORECASE,
)


def extract_table_blocks(text: str) -> list[tuple[str, str]]:
    """Return [(table_name, body_text), ...] by tracking paren depth.

    Inner parens like `IDENTITY(1,1)` or `VARCHAR(255)` are handled correctly.
    """
    results: list[tuple[str, str]] = []
    for match in _CREATE_TABLE_RE.finditer(text):
        name = match.group("name")
        start = match.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            ch = text[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        body = text[start : i - 1]
        results.append((name, body))
    return results


# ---------------------------------------------------------------------------
# Body line walk
# ---------------------------------------------------------------------------

_CONSTRAINT_FIRST_WORDS = frozenset(
    {"PRIMARY", "FOREIGN", "CONSTRAINT", "UNIQUE", "CHECK", "INDEX", "KEY"}
)


def body_lines(body: str) -> list[str]:
    """Return non-empty, comma-stripped lines from a CREATE TABLE body."""
    out: list[str] = []
    for raw in body.splitlines():
        stripped = raw.strip().rstrip(",").rstrip()
        if stripped:
            out.append(stripped)
    return out


def is_constraint_line(line: str) -> bool:
    tokens = line.split(maxsplit=1)
    if not tokens:
        return False
    return tokens[0].upper() in _CONSTRAINT_FIRST_WORDS


# ---------------------------------------------------------------------------
# PRIMARY KEY constraint extraction
# ---------------------------------------------------------------------------

_PK_RE = re.compile(
    r"(?:CONSTRAINT\s+\w+\s+)?PRIMARY\s+KEY\s*\(([^)]+)\)",
    re.IGNORECASE,
)


def parse_pk_col_names(body: str) -> frozenset[str]:
    """Column names listed in any table-level PRIMARY KEY constraint."""
    cols: set[str] = set()
    for line in body_lines(body):
        if not is_constraint_line(line):
            continue
        match = _PK_RE.search(line)
        if not match:
            continue
        for col in match.group(1).split(","):
            cols.add(_strip_ident(col))
    return frozenset(cols)


# ---------------------------------------------------------------------------
# FOREIGN KEY constraint extraction
# ---------------------------------------------------------------------------

_FK_RE = re.compile(
    rf"(?:CONSTRAINT\s+{_QO}\w+{_QC}\s+)?FOREIGN\s+KEY\s*\(([^)]+)\)\s*"
    rf"REFERENCES\s+{_SCHEMA_PREFIX}{_QO}(\w+){_QC}\s*\(([^)]+)\)",
    re.IGNORECASE,
)

_INLINE_REF_RE = re.compile(
    rf"REFERENCES\s+{_SCHEMA_PREFIX}{_QO}(?P<to_table>\w+){_QC}\s*\({_QO}(?P<to_col>\w+){_QC}\)",
    re.IGNORECASE,
)


def parse_fk_ref_parts(
    body: str,
    table_name: str,
    spec_file: Path,
    spec_label: str,
) -> list[RefPart]:
    """Extract table-level `FOREIGN KEY ... REFERENCES ...` clauses."""
    parts: list[RefPart] = []
    for line in body_lines(body):
        if not is_constraint_line(line):
            continue
        match = _FK_RE.search(line)
        if not match:
            continue
        from_col = _strip_ident(match.group(1).split(",")[0])
        to_table = match.group(2)
        to_col = _strip_ident(match.group(3).split(",")[0])
        parts.append(
            _build_ref(spec_file, spec_label, table_name, from_col, to_table, to_col)
        )
    return parts


def parse_inline_ref_parts(
    body: str,
    table_name: str,
    spec_file: Path,
    spec_label: str,
) -> list[RefPart]:
    """Extract column-level inline `REFERENCES table(col)` clauses (PG style)."""
    parts: list[RefPart] = []
    for line in body_lines(body):
        if is_constraint_line(line):
            continue
        col_match = re.match(rf"^{_QO}(\w+){_QC}", line)
        ref_match = _INLINE_REF_RE.search(line)
        if not col_match or not ref_match:
            continue
        from_col = col_match.group(1)
        to_table = ref_match.group("to_table")
        to_col = ref_match.group("to_col")
        parts.append(
            _build_ref(spec_file, spec_label, table_name, from_col, to_table, to_col)
        )
    return parts


def _build_ref(
    spec_file: Path,
    spec_label: str,
    from_table: str,
    from_col: str,
    to_table: str,
    to_col: str,
) -> RefPart:
    return RefPart(
        kind=PartKind.ref,
        spec_file=spec_file,
        target_part_path=f"{spec_label}#ref:{from_table}.{from_col}>{to_table}.{to_col}",
        from_table=from_table,
        from_column=from_col,
        to_table=to_table,
        to_column=to_col,
        operator=">",
        from_target_part_path=f"{spec_label}#{from_table}.{from_col}",
        to_target_part_path=f"{spec_label}#{to_table}.{to_col}",
    )


# ---------------------------------------------------------------------------
# Column parsing
# ---------------------------------------------------------------------------

_COL_LINE_RE = re.compile(
    rf"^{_QO}(?P<name>\w+){_QC}\s+"
    r"(?P<type>[A-Za-z_][A-Za-z0-9_]*)(?:\([^)]*\))?\s*"
    r"(?P<attrs>.*?)\s*$",
    re.IGNORECASE,
)

_NOT_NULL_RE = re.compile(r"\bNOT\s+NULL\b", re.IGNORECASE)
_INLINE_PK_RE = re.compile(r"\bPRIMARY\s+KEY\b", re.IGNORECASE)
_DEFAULT_RE = re.compile(r"\bDEFAULT\b", re.IGNORECASE)

_DEFAULT_VALUE_RE = re.compile(
    r"\bDEFAULT\s+("
    r"'(?:[^'\\]|\\.)*'"
    r'|"(?:[^"\\]|\\.)*"'
    r"|[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)"
    r"|[A-Za-z_][A-Za-z0-9_]*"
    r"|-?\d+(?:\.\d+)?"
    r")",
    re.IGNORECASE,
)


def _extract_default_value(attrs: str) -> str | None:
    """Return the literal/identifier/expression following `DEFAULT`, or None."""
    match = _DEFAULT_VALUE_RE.search(attrs)
    if not match:
        return None
    raw = match.group(1).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    return raw


def parse_columns(
    body: str,
    spec_label: str,
    table_name: str,
    pk_col_names: frozenset[str],
    detect_increment: Callable[[str, str], bool],
) -> tuple[tuple[Column, ...], tuple[Column, ...]]:
    """Return `(all_columns, not_null_columns)` for one CREATE TABLE body.

    `detect_increment(type_base_upper, attrs_upper)` returns True when the
    column is auto-incrementing per the dialect's rules.
    """
    columns: list[Column] = []
    for line in body_lines(body):
        if is_constraint_line(line):
            continue
        match = _COL_LINE_RE.match(line)
        if not match:
            continue
        col_name = match.group("name")
        type_base = match.group("type").upper()
        attrs = match.group("attrs")
        attrs_upper = attrs.upper()

        has_not_null = bool(_NOT_NULL_RE.search(attrs_upper))
        inline_pk = bool(_INLINE_PK_RE.search(attrs_upper))
        has_default = bool(_DEFAULT_RE.search(attrs_upper))
        default_value = _extract_default_value(attrs) if has_default else None
        is_pk = inline_pk or col_name in pk_col_names
        nullable = not (has_not_null or is_pk)
        has_increment = detect_increment(type_base, attrs_upper)

        columns.append(
            Column(
                name=col_name,
                type=type_base,
                nullable=nullable,
                is_pk=is_pk,
                has_default=has_default,
                default_value=default_value,
                has_increment=has_increment,
                target_part_path=f"{spec_label}#{table_name}.{col_name}",
            )
        )

    not_null = tuple(c for c in columns if not c.nullable)
    return tuple(columns), not_null


# ---------------------------------------------------------------------------
# Dialect-driven parse loop
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DDLDialect:

    detect_increment: Callable[[str, str], bool]
    inline_refs: bool = False


def parse_ddl(path: Path, dialect: DDLDialect) -> list[Part]:
    text = path.read_text()
    spec_label = path.as_posix()
    parts: list[Part] = []
    seen_refs: set[str] = set()
    for table_name, body in extract_table_blocks(text):
        pk_cols = parse_pk_col_names(body)
        columns, not_null = parse_columns(
            body, spec_label, table_name, pk_cols, dialect.detect_increment
        )
        parts.append(
            TablePart(
                kind=PartKind.table,
                spec_file=path,
                target_part_path=f"{spec_label}#{table_name}",
                table_name=table_name,
                columns=columns,
                not_null_columns=not_null,
            )
        )
        refs = parse_fk_ref_parts(body, table_name, path, spec_label)
        if dialect.inline_refs:
            refs = refs + parse_inline_ref_parts(body, table_name, path, spec_label)
        for ref in refs:
            if ref.target_part_path in seen_refs:
                continue
            seen_refs.add(ref.target_part_path)
            parts.append(ref)
    return parts
