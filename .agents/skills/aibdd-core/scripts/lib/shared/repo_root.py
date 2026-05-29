"""Locate the skill submodule root that contains `.claude/skills/aibdd-core`."""

from __future__ import annotations

from pathlib import Path


def repo_root_from_module(*, start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    raise FileNotFoundError("cannot locate repo root containing .claude/skills/aibdd-core")
