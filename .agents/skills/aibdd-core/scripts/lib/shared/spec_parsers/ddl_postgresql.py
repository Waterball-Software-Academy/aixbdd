"""PostgreSQL DDL (`*.pg.sql`) spec parser.

Produces the same `TablePart` / `RefPart` shape as the DBML parser so
downstream preset plugins (`part_to_dsl.py`) need no changes.

Scope:
  - `CREATE TABLE <name> ( ... );` blocks → `TablePart`
  - Table-level `FOREIGN KEY (col) REFERENCES other(col)` → `RefPart`
  - Inline `col TYPE ... REFERENCES other(col)` → `RefPart`

Column attribute detection (PG-specific):
  - `NOT NULL` / inline `PRIMARY KEY` → standard
  - Type `SERIAL` / `BIGSERIAL` / `SMALLSERIAL` → has_increment=true
  - `GENERATED [ALWAYS|BY DEFAULT] AS IDENTITY` → has_increment=true
"""

from __future__ import annotations

import re
from pathlib import Path

from shared.spec_parsers._sql_ddl import DDLDialect, parse_ddl
from shared.spec_parsers.base import SpecParser
from shared.spec_parts import Part

_SERIAL_TYPES = frozenset({"SERIAL", "BIGSERIAL", "SMALLSERIAL"})
_GENERATED_IDENTITY_RE = re.compile(
    r"GENERATED\s+(?:ALWAYS|BY\s+DEFAULT)\s+AS\s+IDENTITY",
    re.IGNORECASE,
)


def _detect_increment(type_base: str, attrs_upper: str) -> bool:
    if type_base in _SERIAL_TYPES:
        return True
    return bool(_GENERATED_IDENTITY_RE.search(attrs_upper))


_DIALECT = DDLDialect(detect_increment=_detect_increment, inline_refs=True)


class PostgresSpecParser(SpecParser):
    def parse(self, path: Path) -> list[Part]:
        return parse_ddl(path, _DIALECT)
