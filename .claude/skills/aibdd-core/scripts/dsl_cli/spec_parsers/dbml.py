"""DBML (`*.dbml`) spec parser.

Scope: only `Table <name> { ... }` blocks. Other DBML constructs (Ref, Enum,
Project, indexes) are ignored — they don't drive part-derived DSL today.

Each Table becomes a `DbmlTablePart`. Per column we extract:
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

from dsl_cli.models import Column, DbmlTablePart, PartKind
from dsl_cli.spec_parsers.base import SpecParser

# Capture `Table <name> { <body> }`. DOTALL so `.` matches newlines inside body.
_TABLE_RE = re.compile(
    r"Table\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>[^{}]*)\}",
    re.DOTALL,
)

# A column line: `<name> <type> [<options>]?`. Options chunk may contain backticks
# (for `default: \`now()\``) so we match it as anything-but-newline.
_COLUMN_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+"
    r"(?P<type>[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?)"
    r"(?:\s*\[(?P<options>[^\n\]]*)\])?\s*$"
)


def _parse_options(options_chunk: str | None) -> tuple[bool, bool, bool]:
    """Return (is_pk, has_explicit_not_null, has_default)."""
    if not options_chunk:
        return False, False, False
    tokens = [tok.strip() for tok in options_chunk.split(",")]
    is_pk = any(tok == "pk" or tok.startswith("pk ") for tok in tokens)
    has_not_null = any(tok == "not null" for tok in tokens)
    has_default = any(tok.startswith("default:") for tok in tokens)
    return is_pk, has_not_null, has_default


class DBMLSpecParser(SpecParser):
    def parse(self, path: Path) -> list[DbmlTablePart]:
        text = path.read_text()
        spec_label = path.as_posix()
        parts: list[DbmlTablePart] = []
        for table_match in _TABLE_RE.finditer(text):
            table_name = table_match.group("name")
            body = table_match.group("body")
            columns = tuple(_parse_columns(body, spec_label, table_name))
            not_null = tuple(c for c in columns if not c.nullable)
            parts.append(
                DbmlTablePart(
                    kind=PartKind.dbml_table,
                    spec_file=path,
                    target_part_path=f"{spec_label}#{table_name}",
                    table_name=table_name,
                    columns=columns,
                    not_null_columns=not_null,
                )
            )
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
        is_pk, has_not_null, has_default = _parse_options(m.group("options"))
        nullable = not (has_not_null or is_pk)
        yield Column(
            name=col_name,
            type=col_type,
            nullable=nullable,
            is_pk=is_pk,
            has_default=has_default,
            target_part_path=f"{spec_label}#{table_name}.{col_name}",
        )
