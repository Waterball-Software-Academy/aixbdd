#!/usr/bin/env python3
"""Late-bind TRUTH_FUNCTION_PACKAGE + derived dirs into .aibdd/arguments.yml.

Kickoff deliberately omits `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR`; Discovery must
persist the mapping after sourcing selects NN-功能模組描述 slug。

Also creates `{slug}/activities|features|test-plan` plus placeholder `dsl.yml`.

Warning: Rewrites arguments.yml via `yaml.safe_dump`; inline comments/key order
are NOT preserved。

Usage:
  python3 bind_truth_function_package.py <AIBDD_ARGUMENTS_PATH> <PACKAGE_SLUG>

Example:
  python3 bind_truth_function_package.py ./.aibdd/arguments.yml 01-order-checkout
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from kickoff_path_resolve import load_resolved_kickoff_state  # noqa: E402

PLACEHOLDER_DSL = (
    "# Local DSL registry (YAML).\n"
    "# Owner: /aibdd-discovery placeholder + /aibdd-plan for semantic entries.\n"
    "# Kickoff-safe empty skeleton — parse as YAML with key `entries`.\n"
    "entries: []\n"
)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    args_path = Path(sys.argv[1]).resolve()
    slug = sys.argv[2].strip().strip("/\\")
    if not slug or ".." in slug:
        print("INVALID_PACKAGE_SLUG", file=sys.stderr)
        return 2

    if not args_path.is_file():
        print(f"arguments.yml not found: {args_path}", file=sys.stderr)
        return 1

    workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)

    pkgs_rel = resolved.get("TRUTH_BOUNDARY_PACKAGES_DIR")
    if not isinstance(pkgs_rel, str) or not pkgs_rel.strip():
        print("TRUTH_BOUNDARY_PACKAGES_DIR missing after resolve", file=sys.stderr)
        return 1

    packages_abs = (workspace_root / pkgs_rel.replace("\\", "/")).resolve()
    package_abs = (packages_abs / slug).resolve()
    try:
        package_abs.relative_to(packages_abs)
    except ValueError:
        print("PACKAGE_SLUG escapes packages root", file=sys.stderr)
        return 1

    raw = yaml.safe_load(args_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        print("arguments.yml must be mapping", file=sys.stderr)
        return 1

    merged = dict(raw)
    merged["TRUTH_FUNCTION_PACKAGE"] = f"${{TRUTH_BOUNDARY_PACKAGES_DIR}}/{slug}"
    merged["FEATURE_SPECS_DIR"] = "${TRUTH_FUNCTION_PACKAGE}/features"
    merged["ACTIVITIES_DIR"] = "${TRUTH_FUNCTION_PACKAGE}/activities"
    merged["TRUTH_TEST_PLAN_DIR"] = "${TRUTH_FUNCTION_PACKAGE}/test-plan"
    merged["BOUNDARY_PACKAGE_DSL"] = "${TRUTH_FUNCTION_PACKAGE}/dsl.yml"

    args_path.write_text(
        yaml.safe_dump(
            merged,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )

    for sub in ("activities", "features", "test-plan"):
        (package_abs / sub).mkdir(parents=True, exist_ok=True)
    dsl_file = package_abs / "dsl.yml"
    if not dsl_file.exists():
        dsl_file.write_text(PLACEHOLDER_DSL, encoding="utf-8")

    print(f"bound package {slug} under {packages_abs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
