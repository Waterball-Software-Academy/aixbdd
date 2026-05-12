#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import read_args, resolve_arg_path, specs_root


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: resolve_plan_paths.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    keys = [
        "PLAN_SPEC",
        "PLAN_REPORTS_DIR",
        "TRUTH_BOUNDARY_ROOT",
        "TRUTH_BOUNDARY_PACKAGES_DIR",
        "TRUTH_FUNCTION_PACKAGE",
        "FEATURE_SPECS_DIR",
        "ACTIVITIES_DIR",
        "BOUNDARY_PACKAGE_DSL",
        "BOUNDARY_SHARED_DSL",
        "TEST_STRATEGY_FILE",
        "PLAN_IMPLEMENTATION_DIR",
    ]
    resolved = {key.lower(): str(resolve_arg_path(args_path, args, key) or "") for key in keys}
    plan_spec = resolve_arg_path(args_path, args, "PLAN_SPEC")
    current_plan_package = plan_spec.parent if plan_spec else None
    payload = {
        "ok": True,
        "arguments_path": str(args_path),
        "specs_root": str(specs_root(args_path, args)),
        "current_plan_package": str(current_plan_package or ""),
        "truth_function_package": resolved["truth_function_package"],
        "features_dir": resolved["feature_specs_dir"],
        "activities_dir": resolved["activities_dir"],
        **resolved,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
