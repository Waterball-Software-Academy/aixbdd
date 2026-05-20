"""Behave hooks for dsl_cli BDD suite.

Inserts the parent of the dsl_cli package (scripts/) into sys.path so step
modules can do `from dsl_cli.spec_parsers.openapi import OpenAPISpecParser`.

before_scenario:
    create context.tmp_root tempdir, init context.files alias map.

after_scenario:
    delete context.tmp_root.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_PACKAGE_PARENT = _TESTS_DIR.parent.parent  # .../aibdd-core/scripts
if str(_PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_PARENT))


def before_scenario(context, scenario):
    context.tmp_root = Path(tempfile.mkdtemp(prefix="dsl_cli_test_"))
    context.files = {}
    context.last_file_path = None
    context.read_content = None


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
