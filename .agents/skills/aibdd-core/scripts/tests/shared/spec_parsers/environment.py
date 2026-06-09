"""Behave hooks for the shared.spec_parsers BDD suite."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# Bootstrap: put tests/ (the dir holding _support/) on sys.path, then delegate
# the lib/scripts path injection to the shared helper.
_tests_root = next(p for p in Path(__file__).resolve().parents if (p / "_support").is_dir())
if str(_tests_root) not in sys.path:
    sys.path.insert(0, str(_tests_root))

from _support.paths import setup_sys_path  # noqa: E402

setup_sys_path()


def before_scenario(context, scenario):
    context.tmp_root = Path(tempfile.mkdtemp(prefix="spec_parsers_test_"))
    context.files = {}
    context.last_file_path = None
    context.read_content = None


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
