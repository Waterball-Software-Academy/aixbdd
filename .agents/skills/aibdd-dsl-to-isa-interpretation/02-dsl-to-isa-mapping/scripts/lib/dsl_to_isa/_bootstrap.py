"""Reach into aibdd-core for the shared modules the translator reuses.

The DSL→ISA translator lives in this skill, but it does not duplicate the
shared infra it depends on — `shared.dsl_yaml` (round-trip YAML + brace fix)
and `shared.spec_parsers.*` (the Spec Parser). Those stay in aibdd-core as the
single SSOT. This bootstrap mirrors the aibdd-spec-by-example-analyze
reach-into-core idiom: walk parents for `.claude/skills/aibdd-core`, then put
that skill's `scripts/` + `scripts/lib` on `sys.path` so `import shared.*`
resolves.

`dsl_to_isa/__init__.py` calls `ensure_core_on_path()` on package import, so
every consumer (CLI subprocess, behave step modules) gets `shared.*` wired
before any submodule's top-level imports run.
"""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root_from_module(*, start: Path | None = None) -> Path:
    """Locate the repo root that exposes `.claude/skills/aibdd-core`."""
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    raise FileNotFoundError(
        "cannot locate repo root containing .claude/skills/aibdd-core"
    )


def ensure_core_on_path(*, start: Path | None = None) -> Path:
    """Inject aibdd-core `scripts/lib` + `scripts/` onto sys.path; return scripts dir."""
    repo_root = repo_root_from_module(start=start)
    core_scripts = repo_root / ".claude" / "skills" / "aibdd-core" / "scripts"
    core_lib = core_scripts / "lib"
    for path in (core_lib, core_scripts):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
    return core_scripts
