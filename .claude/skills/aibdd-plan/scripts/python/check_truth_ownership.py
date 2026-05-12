#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _common import emit, read_args, resolve_arg_path, violation


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_truth_ownership.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    violations = []

    truth_root = resolve_arg_path(args_path, args, "TRUTH_BOUNDARY_ROOT")
    truth_pkg = resolve_arg_path(args_path, args, "TRUTH_FUNCTION_PACKAGE")
    plan_spec = resolve_arg_path(args_path, args, "PLAN_SPEC")
    contracts = resolve_arg_path(args_path, args, "CONTRACTS_DIR")
    data = resolve_arg_path(args_path, args, "DATA_DIR")
    strategy = resolve_arg_path(args_path, args, "TEST_STRATEGY_FILE")
    local_dsl = resolve_arg_path(args_path, args, "BOUNDARY_PACKAGE_DSL")
    shared_dsl = resolve_arg_path(args_path, args, "BOUNDARY_SHARED_DSL")

    owned = [p for p in [contracts, data, strategy, local_dsl, shared_dsl] if p is not None]
    for path in owned:
        if truth_root and truth_root not in path.parents and path != truth_root:
            violations.append(violation("TRUTH_OUTSIDE_BOUNDARY_ROOT", str(args_path), f"{path} is outside {truth_root}"))

    if truth_pkg and local_dsl and truth_pkg not in local_dsl.parents:
        violations.append(violation("LOCAL_DSL_OUTSIDE_FUNCTION_PACKAGE", str(args_path), f"{local_dsl} is outside {truth_pkg}"))

    if plan_spec:
        plan_root = plan_spec.parent
        for path in owned:
            if plan_root in path.parents or path == plan_root:
                violations.append(violation("SHADOW_TRUTH_IN_PLAN_PACKAGE", str(args_path), f"{path} is inside plan package"))

    return emit(not violations, "truth ownership check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
