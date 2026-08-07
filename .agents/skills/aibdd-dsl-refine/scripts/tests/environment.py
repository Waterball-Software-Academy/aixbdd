"""behave hooks for build_worklist BDD suite。"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent


def before_scenario(context, scenario):
    context.tests_dir = _TESTS_DIR
    context.scripts_dir = _TESTS_DIR.parent
    context.fixtures_dir = _TESTS_DIR / "fixtures"
    context.tmp_dir = Path(tempfile.mkdtemp(prefix="dsl-refine-worklist-"))
    context.result = None
    context.worklist = None


def after_scenario(context, scenario):
    tmp = getattr(context, "tmp_dir", None)
    if tmp and tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
