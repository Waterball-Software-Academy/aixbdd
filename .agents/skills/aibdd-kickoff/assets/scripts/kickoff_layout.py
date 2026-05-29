#!/usr/bin/env python3
"""
/aibdd-kickoff layout copier (pure file copy + shared DSL seed).

Copies the invariant template tree (assets/templates/shared/) to the target
boundary codebase root, then materializes specs/shared/dsl.yml from the active
boundary preset's shared-dsl-template.yml.

Per-stack tail appending and placeholder substitution for other kickoff
artifacts are handled by 02-execute-layout/SOP.md as post-copy LLM Edit ops.

Usage:
  python3 kickoff_layout.py --decisions-file <path.json>

decisions.json shape:
  {
    "project_root": "/abs/path",
    "boundary_codebase_subdir": "" | "backend" | ...,
    "stack": "python_e2e" | "java_e2e" | "nextjs_playwright"
  }

Other fields (tlb_id / project_spec_language / ...) are read by the SOP,
not by this script.

Emits JSON to stdout:
  {"ok": true, "boundary_codebase_root": "...", "shared_dsl_path": "..."}.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SHARED_DIR = SCRIPT_DIR.parent / "templates" / "shared"
SKILLS_DIR = SCRIPT_DIR.parent.parent.parent
BOUNDARIES_ROOT = SKILLS_DIR / "aibdd-core" / "assets" / "boundaries"
SPECS_ROOT_DIR = "specs"

STACK_BOUNDARY_ASSET_DIR: dict[str, str] = {
    "python_e2e": "web-service",
    "java_e2e": "web-service",
    "nextjs_playwright": "web-frontend",
}


def materialize_shared_dsl(dst: Path, stack: str) -> Path:
    boundary_asset_dir = STACK_BOUNDARY_ASSET_DIR.get(stack)
    if boundary_asset_dir is None:
        raise ValueError(f"unsupported stack for shared DSL seed: {stack}")

    template_path = (
        BOUNDARIES_ROOT
        / boundary_asset_dir
        / "shared-dsl-template.yml"
    )
    if not template_path.is_file():
        raise FileNotFoundError(f"shared DSL template not found: {template_path}")

    content = template_path.read_text()

    shared_dsl_path = dst / SPECS_ROOT_DIR / "shared" / "dsl.yml"
    shared_dsl_path.parent.mkdir(parents=True, exist_ok=True)
    shared_dsl_path.write_text(content)
    return shared_dsl_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions-file", required=True)
    args = parser.parse_args()

    decisions = json.loads(Path(args.decisions_file).read_text())
    project_root = Path(decisions["project_root"])
    subdir = decisions.get("boundary_codebase_subdir", "")
    stack = decisions.get("stack")
    if not stack:
        raise SystemExit("decisions.json must include stack")

    dst = project_root / subdir if subdir else project_root

    shutil.copytree(SHARED_DIR, dst, dirs_exist_ok=True)

    seed_gitkeep = project_root / ".gitkeep"
    if seed_gitkeep.exists():
        seed_gitkeep.unlink()

    shared_dsl_path = materialize_shared_dsl(dst, stack)

    print(
        json.dumps(
            {
                "ok": True,
                "boundary_codebase_root": str(dst),
                "shared_dsl_path": str(shared_dsl_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
