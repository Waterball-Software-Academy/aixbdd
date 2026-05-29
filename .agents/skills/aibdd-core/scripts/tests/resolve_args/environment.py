"""Behave hooks for resolve-args BDD suite."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _TESTS_DIR.parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for path in (_LIB_DIR, _SCRIPTS_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def before_scenario(context, scenario):
    context.tmp_root = Path(tempfile.mkdtemp(prefix="resolve_args_test_"))
    context.project_a = context.tmp_root / "project-a"
    context.project_b = context.tmp_root / "project-b"
    context.project_a.mkdir(parents=True, exist_ok=True)
    context.project_b.mkdir(parents=True, exist_ok=True)
    context.last_result = None
    context.active_project = context.tmp_root


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
