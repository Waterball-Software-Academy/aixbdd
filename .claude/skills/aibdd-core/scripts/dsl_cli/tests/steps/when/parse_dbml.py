"""When step for DBMLSpecParser; mirrors parse_spec.py's chdir pattern."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from dsl_cli.spec_parsers.dbml import DBMLSpecParser


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


@when("DBMLSpecParser parses the last file")
def step_parse_dbml(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = DBMLSpecParser().parse(rel)
