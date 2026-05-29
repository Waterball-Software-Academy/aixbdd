"""Behave hooks for aibdd-tasks script BDD suite."""

from __future__ import annotations

import shutil
import sys
import uuid
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _TESTS_DIR.parent
_PYTHON_DIR = _SCRIPTS_DIR / "python"
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude/skills/aibdd-core/scripts").is_dir():
            return parent
    raise RuntimeError("repo root not found for aibdd-tasks tests")


def before_scenario(context, scenario):
    repo_root = _repo_root()
    context.repo_root = repo_root
    context.tmp_root = repo_root / ".tmp" / "aibdd-tasks-tests" / uuid.uuid4().hex
    context.tmp_root.mkdir(parents=True, exist_ok=True)
    context.project_root = context.tmp_root
    context.args_path = context.project_root / ".aibdd" / "arguments.yml"
    context.last_result = None
    context.last_json = None


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
