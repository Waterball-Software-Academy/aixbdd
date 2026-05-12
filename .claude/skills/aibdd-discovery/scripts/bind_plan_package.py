#!/usr/bin/env python3
"""Late-bind CURRENT_PLAN_PACKAGE into .aibdd/arguments.yml.

Each new-discovery (non-reconcile) round of /aibdd-discovery should DERIVE its
own plan package slug and call this script to:
  1. CREATE specs/<slug>/ (and reports/) directory
  2. Rewrite arguments.yml#CURRENT_PLAN_PACKAGE = ${SPECS_ROOT_DIR}/<slug>

Reconcile rounds MUST NOT call this script; they sustain whatever
CURRENT_PLAN_PACKAGE the parent Discovery already set.

Warning: rewrites arguments.yml via yaml.safe_dump; inline comments / key order
are NOT preserved.

Usage:
  python3 bind_plan_package.py <AIBDD_ARGUMENTS_PATH> <PLAN_PACKAGE_SLUG>

Example:
  python3 bind_plan_package.py ./.aibdd/arguments.yml 002-玩家上線下線心跳離房
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from kickoff_path_resolve import load_resolved_kickoff_state  # noqa: E402


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    args_path = Path(sys.argv[1]).resolve()
    slug = sys.argv[2].strip().strip("/\\")
    if not slug or ".." in slug:
        print("INVALID_PLAN_PACKAGE_SLUG", file=sys.stderr)
        return 2

    if not args_path.is_file():
        print(f"arguments.yml not found: {args_path}", file=sys.stderr)
        return 1

    workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)

    specs_root_rel = resolved.get("SPECS_ROOT_DIR")
    if not isinstance(specs_root_rel, str) or not specs_root_rel.strip():
        print("SPECS_ROOT_DIR missing after resolve", file=sys.stderr)
        return 1

    specs_root_abs = (workspace_root / specs_root_rel.replace("\\", "/")).resolve()
    package_abs = (specs_root_abs / slug).resolve()
    try:
        package_abs.relative_to(specs_root_abs)
    except ValueError:
        print("PLAN_PACKAGE_SLUG escapes specs root", file=sys.stderr)
        return 1

    raw = yaml.safe_load(args_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        print("arguments.yml must be mapping", file=sys.stderr)
        return 1

    merged = dict(raw)
    merged["CURRENT_PLAN_PACKAGE"] = f"${{SPECS_ROOT_DIR}}/{slug}"

    args_path.write_text(
        yaml.safe_dump(
            merged,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )

    package_abs.mkdir(parents=True, exist_ok=True)
    (package_abs / "reports").mkdir(parents=True, exist_ok=True)

    print(f"bound plan package {slug} under {specs_root_abs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
