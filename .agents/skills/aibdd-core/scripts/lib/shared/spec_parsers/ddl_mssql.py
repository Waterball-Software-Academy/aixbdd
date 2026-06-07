"""Microsoft SQL Server DDL (`*.mssql.sql`) spec parser.

Produces the same `TablePart` / `RefPart` shape as the DBML parser so
downstream preset plugins (`part_to_dsl.py`) need no changes.

Scope:
  - `CREATE TABLE <name> ( ... );` blocks → `TablePart`
  - Table-level `FOREIGN KEY (col) REFERENCES other(col)` → `RefPart`
  - `CONSTRAINT FK_xxx FOREIGN KEY (...) REFERENCES ...` → `RefPart`

Column attribute detection (MSSQL-specific):
  - `NOT NULL` → standard
  - `IDENTITY(seed,increment)` or bare `IDENTITY` → has_increment=true
  - `CONSTRAINT PK_xxx PRIMARY KEY (cols)` → is_pk on listed cols
"""

from __future__ import annotations

import re
from pathlib import Path

from shared.spec_parsers._sql_ddl import DDLDialect, parse_ddl
from shared.spec_parsers.base import SpecParser
from shared.spec_parts import Part

_IDENTITY_RE = re.compile(r"\bIDENTITY\b", re.IGNORECASE)


def _detect_increment(type_base: str, attrs_upper: str) -> bool:
    return bool(_IDENTITY_RE.search(attrs_upper))


_DIALECT = DDLDialect(detect_increment=_detect_increment)


class MSSQLSpecParser(SpecParser):
    def parse(self, path: Path) -> list[Part]:
        return parse_ddl(path, _DIALECT)
