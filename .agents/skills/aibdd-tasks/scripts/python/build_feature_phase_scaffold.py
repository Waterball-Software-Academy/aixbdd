#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, feature_title, load_tasks_context


def display_label(feature_path: Path) -> str:
    text = feature_path.read_text(encoding="utf-8") if feature_path.exists() else ""
    title = feature_title(text)
    return title or feature_path.stem


def main() -> int:
    parser = argparse.ArgumentParser(description="Build feature phase scaffold for tasks.md")
    add_tasks_cli_arguments(parser)
    args = parser.parse_args()

    try:
        ctx = load_tasks_context(args)
    except SystemExit as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    truth_root = Path(ctx["truth_boundary_root"])
    ordered_paths: list[str] = ctx["ordered_feature_paths"]
    if not ordered_paths:
        print(
            json.dumps(
                {"ok": False, "reason": "impact matrix has no add/update .feature entries"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    feature_phases = []
    for index, rel_path in enumerate(ordered_paths, start=2):
        feature_path = (truth_root / rel_path).resolve()
        feature_phases.append(
            {
                "phase_number": index,
                "feature_path": rel_path,
                "feature_label": display_label(feature_path),
                "section_titles": ["RED", "GREEN", "Refactor"],
                "red_slot": {"kind": "fixed-template"},
                "green_slot": {"kind": "fixed-template-with-wave-slot"},
                "refactor_slot": {"kind": "fixed-template"},
            }
        )

    payload = {
        "ok": True,
        "summary": "feature phase scaffold",
        "current_plan_package": ctx["current_plan_package"],
        "implementation_dir": ctx["plan_implementation_dir"],
        "impact_matrix_yml": ctx["impact_matrix_yml"],
        "tasks_md_path": ctx["tasks_md"],
        "infra_phase": {"phase_number": 1, "title": "Infra setup"},
        "feature_phases": feature_phases,
        "integration_phase": {
            "phase_number": len(feature_phases) + 2,
            "title": "Integration",
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
