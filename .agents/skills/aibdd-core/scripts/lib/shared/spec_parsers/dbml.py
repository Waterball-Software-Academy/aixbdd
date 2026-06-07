"""DBML (`*.dbml`) spec parser.

Scope:
  - `Table <name> { ... }` blocks → `TablePart`
  - `Ref: a.b > c.d` and inline `[ref: > c.d]` → `RefPart`

Other DBML constructs (Enum, Project, indexes) are ignored.

Each Table becomes a `TablePart`. Per column we extract:
  - name, type
  - is_pk        — has `pk` token in the option list
  - nullable     — false iff `[not null]` or `[pk ...]` appears (pk implies not null)
  - has_default  — has `default: ...` in the option list

target_part_path:
  - Table:   `<spec_file>#<table>`
  - Column:  `<spec_file>#<table>.<column>`
"""

from __future__ import annotations

import re
from pathlib import Path

from shared.spec_parts import Column, RefPart, TablePart, Part, PartKind
from shared.spec_parsers.base import SpecParser

# Capture `Table <name> { <body> }`. DOTALL so `.` matches newlines inside body.
_TABLE_RE = re.compile(
    r"Table\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>[^{}]*)\}",
    re.DOTALL,
)

# A column line: `<name> <type> [<options>]?`. Options chunk may contain backticks
# (for `default: \`now()\``) so we match it as anything-but-newline.
_COLUMN_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+"
    r"(?P<type>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*\[(?P<options>[^\n\]]*)\])?\s*$"
)

_TOP_LEVEL_REF_RE = re.compile(
    r"^\s*Ref\s*:\s*"
    r"(?P<from_table>[A-Za-z_][A-Za-z0-9_]*)\."
    r"(?P<from_column>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"(?P<operator>>|-)\s*"
    r"(?P<to_table>[A-Za-z_][A-Za-z0-9_]*)\."
    r"(?P<to_column>[A-Za-z_][A-Za-z0-9_]*)\s*$",
    re.MULTILINE,
)

_INLINE_REF_RE = re.compile(
    r"ref:\s*(?P<operator>>|-)\s*"
    r"(?P<to_table>[A-Za-z_][A-Za-z0-9_]*)\."
    r"(?P<to_column>[A-Za-z_][A-Za-z0-9_]*)"
)


def _parse_options(options_chunk: str | None) -> tuple[bool, bool, bool, str | None, bool]:
    """Return (is_pk, has_explicit_not_null, has_default, default_value, has_increment)."""
    if not options_chunk:
        return False, False, False, None, False
    tokens = [tok.strip() for tok in options_chunk.split(",")]
    is_pk = any(tok == "pk" or tok.startswith("pk ") for tok in tokens)
    has_not_null = any(tok == "not null" for tok in tokens)
    has_increment = any(tok == "increment" for tok in tokens)
    default_value = _extract_default_value(tokens)
    return is_pk, has_not_null, default_value is not None, default_value, has_increment


def _extract_default_value(tokens: list[str]) -> str | None:
    for tok in tokens:
        if tok.startswith("default:"):
            raw = tok[len("default:"):].strip()
            if (raw.startswith("'") and raw.endswith("'")) or (
                raw.startswith("`") and raw.endswith("`")
            ):
                return raw[1:-1]
            return raw
    return None


class DBMLSpecParser(SpecParser):
    def parse(self, path: Path) -> list[Part]:
        text = path.read_text()
        spec_label = path.as_posix()
        parts: list[Part] = []
        seen_ref_targets: set[str] = set()
        for table_match in _TABLE_RE.finditer(text):
            table_name = table_match.group("name")
            body = table_match.group("body")
            columns = tuple(_parse_columns(body, spec_label, table_name))
            not_null = tuple(c for c in columns if not c.nullable)
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
            for ref_part in _parse_inline_refs(body, path, spec_label, table_name):
                if ref_part.target_part_path in seen_ref_targets:
                    continue
                seen_ref_targets.add(ref_part.target_part_path)
                parts.append(ref_part)
        for ref_part in _parse_top_level_refs(text, path, spec_label):
            if ref_part.target_part_path in seen_ref_targets:
                continue
            seen_ref_targets.add(ref_part.target_part_path)
            parts.append(ref_part)
        return parts


def _parse_columns(body: str, spec_label: str, table_name: str):
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        m = _COLUMN_RE.match(line)
        if not m:
            continue
        col_name = m.group("name")
        col_type = m.group("type")
        is_pk, has_not_null, has_default, default_value, has_increment = _parse_options(m.group("options"))
        nullable = not (has_not_null or is_pk)
        yield Column(
            name=col_name,
            type=col_type,
            nullable=nullable,
            is_pk=is_pk,
            has_default=has_default,
            default_value=default_value,
            has_increment=has_increment,
            target_part_path=f"{spec_label}#{table_name}.{col_name}",
        )


def _parse_top_level_refs(text: str, spec_file: Path, spec_label: str):
    for match in _TOP_LEVEL_REF_RE.finditer(text):
        yield _build_ref_part(
            spec_file=spec_file,
            spec_label=spec_label,
            from_table=match.group("from_table"),
            from_column=match.group("from_column"),
            operator=match.group("operator"),
            to_table=match.group("to_table"),
            to_column=match.group("to_column"),
        )


def _parse_inline_refs(body: str, spec_file: Path, spec_label: str, table_name: str):
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        match = _COLUMN_RE.match(line)
        if not match:
            continue
        options = match.group("options")
        if not options:
            continue
        ref_match = _INLINE_REF_RE.search(options)
        if not ref_match:
            continue
        yield _build_ref_part(
            spec_file=spec_file,
            spec_label=spec_label,
            from_table=table_name,
            from_column=match.group("name"),
            operator=ref_match.group("operator"),
            to_table=ref_match.group("to_table"),
            to_column=ref_match.group("to_column"),
        )


def _build_ref_part(
    *,
    spec_file: Path,
    spec_label: str,
    from_table: str,
    from_column: str,
    operator: str,
    to_table: str,
    to_column: str,
):
    return RefPart(
        kind=PartKind.ref,
        spec_file=spec_file,
        target_part_path=(
            f"{spec_label}#ref:{from_table}.{from_column}{operator}{to_table}.{to_column}"
        ),
        from_table=from_table,
        from_column=from_column,
        to_table=to_table,
        to_column=to_column,
        operator=operator,
        from_target_part_path=f"{spec_label}#{from_table}.{from_column}",
        to_target_part_path=f"{spec_label}#{to_table}.{to_column}",
    )
