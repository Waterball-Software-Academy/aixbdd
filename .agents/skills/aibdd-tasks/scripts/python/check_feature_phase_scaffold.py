#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, emit, load_tasks_context, violation


def main() -> int:
    parser = argparse.ArgumentParser(description="Check feature phase scaffold shape")
    add_tasks_cli_arguments(parser)
    args = parser.parse_args()
    violations: list[dict[str, object]] = []

    try:
        ctx = load_tasks_context(args)
    except SystemExit as exc:
        violations.append(violation("TASKS_CONTEXT_INVALID", str(args.arguments_yml), str(exc)))
        return emit(False, "feature phase scaffold check", violations)

    script_path = Path(__file__).resolve().parent / "build_feature_phase_scaffold.py"
    cmd = [
        sys.executable,
        str(script_path),
        str(args.arguments_yml.resolve()),
    ]
    if args.plan_package:
        cmd.extend(["--plan-package", args.plan_package])
    if args.feature_paths:
        cmd.extend(["--feature-paths", args.feature_paths])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        violations.append(
            violation(
                "SCAFFOLD_BUILD_FAILED",
                str(script_path),
                proc.stdout.strip() or proc.stderr.strip() or "build_feature_phase_scaffold failed",
            )
        )
        return emit(False, "feature phase scaffold check", violations)

    payload = json.loads(proc.stdout)
    if not payload.get("ok"):
        violations.append(violation("SCAFFOLD_NOT_OK", str(script_path), "scaffold payload ok=false"))
        return emit(False, "feature phase scaffold check", violations)

    expected_paths: list[str] = ctx["ordered_feature_paths"]
    feature_phases = payload.get("feature_phases", [])
    if len(feature_phases) != len(expected_paths):
        violations.append(
            violation(
                "SCAFFOLD_FEATURE_COUNT_MISMATCH",
                str(script_path),
                f"expected {len(expected_paths)} scaffold feature phases, got {len(feature_phases)}",
            )
        )

    if payload.get("infra_phase", {}).get("phase_number") != 1:
        violations.append(violation("SCAFFOLD_INFRA_PHASE_INVALID", str(script_path), "infra phase must be phase 1"))
    if payload.get("infra_phase", {}).get("title") != "Infra setup":
        violations.append(violation("SCAFFOLD_INFRA_TITLE_INVALID", str(script_path), "infra phase title must be `Infra setup`"))

    expected_integration = len(feature_phases) + 2
    if payload.get("integration_phase", {}).get("phase_number") != expected_integration:
        violations.append(
            violation(
                "SCAFFOLD_INTEGRATION_PHASE_INVALID",
                str(script_path),
                f"integration phase number must be {expected_integration}",
            )
        )
    if payload.get("integration_phase", {}).get("title") != "Integration":
        violations.append(
            violation("SCAFFOLD_INTEGRATION_TITLE_INVALID", str(script_path), "integration phase title must be `Integration`")
        )

    for idx, item in enumerate(feature_phases, start=2):
        if item.get("phase_number") != idx:
            violations.append(
                violation(
                    "SCAFFOLD_PHASE_NUMBERING_INVALID",
                    str(script_path),
                    f"feature phase numbering must be sequential: expected {idx}, got {item.get('phase_number')}",
                )
            )
        if item.get("section_titles") != ["RED", "GREEN", "Refactor"]:
            violations.append(
                violation(
                    "SCAFFOLD_SECTION_TITLES_INVALID",
                    str(script_path),
                    f"feature phase `{item.get('feature_path')}` must expose RED/GREEN/Refactor slots",
                )
            )
        if idx - 2 < len(expected_paths) and item.get("feature_path") != expected_paths[idx - 2]:
            violations.append(
                violation(
                    "SCAFFOLD_FEATURE_ORDER_INVALID",
                    str(script_path),
                    f"expected feature `{expected_paths[idx - 2]}`, got `{item.get('feature_path')}`",
                )
            )

    return emit(not violations, "feature phase scaffold check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
