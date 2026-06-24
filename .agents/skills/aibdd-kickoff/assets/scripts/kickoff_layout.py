#!/usr/bin/env python3
"""
/aibdd-kickoff layout copier (pure file copy + isa seed).

Copies the invariant template tree (assets/templates/shared/) to the target
boundary codebase root, copies the invariant arguments.yml from the aibdd-core
SSOT (references/ssot/arguments.yml) into the target .aibdd/, then materializes
specs/isa.yml from the active boundary preset's isa-template.yml.

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
  {"ok": true, "boundary_codebase_root": "...", "isa_path": "..."}.
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
ARGUMENTS_SSOT = SKILLS_DIR / "aibdd-core" / "references" / "ssot" / "arguments.yml"
SPECS_ROOT_DIR = "specs"

STACK_BOUNDARY_ASSET_DIR: dict[str, str] = {
    "python_e2e": "web-service",
    "java_e2e": "web-service",
    "nextjs_playwright": "web-frontend",
}


def materialize_isa(dst: Path, stack: str) -> Path:
    boundary_asset_dir = STACK_BOUNDARY_ASSET_DIR.get(stack)
    if boundary_asset_dir is None:
        raise ValueError(f"unsupported stack for isa seed: {stack}")

    template_path = (
        BOUNDARIES_ROOT
        / boundary_asset_dir
        / "isa-template.yml"
    )
    if not template_path.is_file():
        raise FileNotFoundError(f"isa template not found: {template_path}")

    content = template_path.read_text()

    isa_path = dst / SPECS_ROOT_DIR / "isa.yml"
    isa_path.parent.mkdir(parents=True, exist_ok=True)
    isa_path.write_text(content)
    return isa_path


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

    if not ARGUMENTS_SSOT.is_file():
        raise FileNotFoundError(f"arguments SSOT not found: {ARGUMENTS_SSOT}")
    arguments_path = dst / ".aibdd" / "arguments.yml"
    arguments_path.parent.mkdir(parents=True, exist_ok=True)
    arguments_path.write_text(ARGUMENTS_SSOT.read_text())

    seed_gitkeep = project_root / ".gitkeep"
    if seed_gitkeep.exists():
        seed_gitkeep.unlink()

    isa_path = materialize_isa(dst, stack)

    print(
        json.dumps(
            {
                "ok": True,
                "boundary_codebase_root": str(dst),
                "isa_path": str(isa_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
