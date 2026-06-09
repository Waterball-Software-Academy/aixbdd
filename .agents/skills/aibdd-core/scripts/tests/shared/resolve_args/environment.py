"""Behave hooks for resolve-args BDD suite."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_tests_root = next(p for p in Path(__file__).resolve().parents if (p / "_support").is_dir())
if str(_tests_root) not in sys.path:
    sys.path.insert(0, str(_tests_root))

from _support.paths import setup_sys_path  # noqa: E402

setup_sys_path()


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
