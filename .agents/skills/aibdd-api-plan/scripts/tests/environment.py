"""Behave hooks for aibdd-api-plan script BDD suite."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude/skills/aibdd-core/scripts").is_dir():
            return parent
    raise RuntimeError("repo root not found for aibdd-api-plan tests")


def before_scenario(context, scenario):
    repo_root = _repo_root()
    context.repo_root = repo_root
    context.tmp_root = repo_root / ".tmp" / "aibdd-api-plan-tests" / uuid.uuid4().hex
    context.tmp_root.mkdir(parents=True, exist_ok=True)
    context.contracts_dir = context.tmp_root
    context.last_result = None
    context.last_json = None


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
