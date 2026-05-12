#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _common import emit, read_args, resolve_arg_path, violation


REQUIRED = [
    "PLAN_SPEC",
    "PLAN_REPORTS_DIR",
    "TRUTH_BOUNDARY_ROOT",
    "TRUTH_FUNCTION_PACKAGE",
    "BOUNDARY_PACKAGE_DSL",
    "BOUNDARY_SHARED_DSL",
    "TEST_STRATEGY_FILE",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_plan_phase.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    violations = []

    for key in REQUIRED:
        if not args.get(key):
            violations.append(violation("MISSING_ARGUMENT_KEY", str(args_path), f"missing {key}"))

    plan_spec = resolve_arg_path(args_path, args, "PLAN_SPEC")
    truth_pkg = resolve_arg_path(args_path, args, "TRUTH_FUNCTION_PACKAGE")
    if plan_spec and truth_pkg and truth_pkg in plan_spec.parents:
        violations.append(violation("PLAN_TRUTH_OVERLAP", str(args_path), "PLAN_SPEC is inside TRUTH_FUNCTION_PACKAGE"))
    if plan_spec and truth_pkg and plan_spec.parent == truth_pkg:
        violations.append(violation("PLAN_TRUTH_OVERLAP", str(args_path), "plan package equals function package"))

    old_keys = [k for k in ("FEATURE_DIR", "DATA_MODEL", "QUICKSTART") if k in args]
    for key in old_keys:
        violations.append(violation("LEGACY_SPECKIT_KEY", str(args_path), f"legacy key should not drive /aibdd-plan: {key}"))

    for key in ("BOUNDARY_PACKAGE_DSL", "BOUNDARY_SHARED_DSL"):
        val = str(args.get(key, "")).strip()
        if val and (val.endswith(".md") or "/dsl.md" in val.replace("\\", "/").lower()):
            violations.append(violation("DSL_PATH_LEGACY_MD", str(args_path), f"{key} must use dsl.yml-only path, got {val}"))

    return emit(not violations, "plan/truth path phase check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
