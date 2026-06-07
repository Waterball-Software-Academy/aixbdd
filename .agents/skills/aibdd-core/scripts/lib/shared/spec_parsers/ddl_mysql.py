"""MySQL DDL (`*.mysql.sql`) spec parser.

Produces the same `TablePart` / `RefPart` shape as the DBML parser so
downstream preset plugins (`part_to_dsl.py`) need no changes.

Scope:
  - `CREATE TABLE <name> ( ... );` blocks → `TablePart`
  - Table-level `FOREIGN KEY (col) REFERENCES other(col)` → `RefPart`
  - Optional `CONSTRAINT <name>` prefix on PK / FK clauses

Column attribute detection:
  - `NOT NULL`        → nullable=false
  - `PRIMARY KEY (..)` (table-level)  → is_pk on listed cols
  - `AUTO_INCREMENT`  → has_increment=true
  - `DEFAULT ...`     → has_default=true
"""

from __future__ import annotations

from pathlib import Path

from shared.spec_parsers._sql_ddl import DDLDialect, parse_ddl
from shared.spec_parsers.base import SpecParser
from shared.spec_parts import Part


def _detect_increment(type_base: str, attrs_upper: str) -> bool:
    return "AUTO_INCREMENT" in attrs_upper


_DIALECT = DDLDialect(detect_increment=_detect_increment)


class MySQLSpecParser(SpecParser):
    def parse(self, path: Path) -> list[Part]:
        return parse_ddl(path, _DIALECT)
