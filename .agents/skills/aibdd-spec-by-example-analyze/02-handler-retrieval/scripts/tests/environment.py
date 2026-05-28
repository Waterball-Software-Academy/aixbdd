"""Behave hooks for handler-candidate BDD suite."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _TESTS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def before_scenario(context, scenario):
    context.tmp_root = Path(tempfile.mkdtemp(prefix="handler_candidates_test_"))
    context.files = {}
    context.last_file_path = None
    context.last_result = None
    context.last_json = None
    context.last_questions = []


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
