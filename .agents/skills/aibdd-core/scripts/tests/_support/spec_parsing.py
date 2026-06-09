"""Shared step: drive a spec parser over the last temp file → context.parts.

Cross-suite plumbing. The spec_parsers suite exercises this as the system
under test; dsl_cli uses it to build parts as a fixture for preset-template
tests (reflecting lib dsl_cli's dependency on shared.spec_parsers). Only the
parsers actually shared across suites live here (DBML, OpenAPI); dialect SQL
parses and the failure-capture variants stay in the spec_parsers suite.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from shared.spec_parsers.dbml import DBMLSpecParser
from shared.spec_parsers.openapi import OpenAPISpecParser


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


@when("OpenAPISpecParser parses the last file")
def step_parse_openapi(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = OpenAPISpecParser().parse(rel)
