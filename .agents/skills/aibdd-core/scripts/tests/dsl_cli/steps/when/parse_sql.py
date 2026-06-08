"""When steps for SQL-dialect spec parsers (MySQL / Postgres / MSSQL).

Mirrors ``parse_dbml.py``'s chdir pattern so emitted parts use spec-relative
paths (e.g. ``data/domain.mysql.sql#users``).
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from shared.spec_parsers.ddl_mssql import MSSQLSpecParser
from shared.spec_parsers.ddl_mysql import MySQLSpecParser
from shared.spec_parsers.ddl_postgresql import PostgresSpecParser


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


@when("MySQLSpecParser parses the last file")
def step_parse_mysql(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = MySQLSpecParser().parse(rel)


@when("PostgresSpecParser parses the last file")
def step_parse_pg(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = PostgresSpecParser().parse(rel)


@when("MSSQLSpecParser parses the last file")
def step_parse_mssql(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = MSSQLSpecParser().parse(rel)
