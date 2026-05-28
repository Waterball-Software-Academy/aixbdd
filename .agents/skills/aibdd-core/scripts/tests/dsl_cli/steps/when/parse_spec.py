"""When steps that invoke a spec_parser on context.last_file_path.

The step chdirs into context.tmp_root for the duration of the call so the
parser sees the spec_file as a project-relative path (matching the format
used in target_part_path values).
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from dsl_cli.spec_parsers.openapi import OpenAPISpecParser


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


@when("OpenAPISpecParser parses the last file")
def step_parse_openapi(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.parts = OpenAPISpecParser().parse(rel)


@when("OpenAPISpecParser parses the last file and captures the exception")
def step_parse_openapi_capture(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        try:
            OpenAPISpecParser().parse(rel)
        except Exception as exc:
            context.captured_exception = exc
            return
    context.captured_exception = None
