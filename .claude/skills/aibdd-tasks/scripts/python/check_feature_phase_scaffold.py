#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _common import emit, extract_impacted_feature_paths, read_args, resolve_arg_path, violation


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_feature_phase_scaffold.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    plan_md = resolve_arg_path(args_path, args, "PLAN_MD")
    feature_dir = resolve_arg_path(args_path, args, "FEATURE_SPECS_DIR")
    violations: list[dict[str, object]] = []

    if plan_md is None or feature_dir is None:
        violations.append(violation("MISSING_REQUIRED_PATH", str(args_path), "PLAN_MD or FEATURE_SPECS_DIR missing"))
        return emit(False, "feature phase scaffold check", violations)

    script_path = Path(__file__).resolve().parent / "build_feature_phase_scaffold.py"
    proc = subprocess.run(
        [sys.executable, str(script_path), str(args_path)],
        capture_output=True,
        text=True,
        check=False,
    )
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

    impacted = extract_impacted_feature_paths(plan_md.read_text(encoding="utf-8"))
    feature_phases = payload.get("feature_phases", [])
    if len(feature_phases) != len(impacted):
        violations.append(
            violation(
                "SCAFFOLD_FEATURE_COUNT_MISMATCH",
                str(script_path),
                f"expected {len(impacted)} scaffold feature phases, got {len(feature_phases)}",
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
        if idx - 2 < len(impacted) and item.get("feature_path") != impacted[idx - 2]:
            violations.append(
                violation(
                    "SCAFFOLD_FEATURE_ORDER_INVALID",
                    str(script_path),
                    f"expected impacted feature `{impacted[idx - 2]}`, got `{item.get('feature_path')}`",
                )
            )

    return emit(not violations, "feature phase scaffold check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
