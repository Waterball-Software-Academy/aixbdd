#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import read_args, resolve_arg_path


def main() -> int:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: resolve_tasks_paths.py <arguments.yml> [tasks_md_basename]", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    tasks_basename = Path(sys.argv[2]).name if len(sys.argv) == 3 else "tasks.md"
    args = read_args(args_path)

    plan_md = resolve_arg_path(args_path, args, "PLAN_MD")
    current_plan_package = plan_md.parent if plan_md else None
    payload = {
        "ok": True,
        "arguments_path": str(args_path),
        "current_plan_package": str(current_plan_package or ""),
        "plan_md": str(plan_md or ""),
        "research_md": str((current_plan_package / "research.md") if current_plan_package else ""),
        "plan_internal_structure": str(resolve_arg_path(args_path, args, "PLAN_INTERNAL_STRUCTURE") or ""),
        "feature_specs_dir": str(resolve_arg_path(args_path, args, "FEATURE_SPECS_DIR") or ""),
        "truth_boundary_root": str(resolve_arg_path(args_path, args, "TRUTH_BOUNDARY_ROOT") or ""),
        "boundary_map": str((resolve_arg_path(args_path, args, "TRUTH_BOUNDARY_ROOT") or Path(".")) / "boundary-map.yml"),
        "tasks_md": str((current_plan_package / tasks_basename) if current_plan_package else ""),
        "project_spec_language": args.get("PROJECT_SPEC_LANGUAGE", ""),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
