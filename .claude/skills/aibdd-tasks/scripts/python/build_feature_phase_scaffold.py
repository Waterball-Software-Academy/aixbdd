#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import extract_impacted_feature_paths, feature_title, read_args, resolve_arg_path


def sorted_feature_paths(feature_dir: Path, workspace_root: Path) -> list[str]:
    paths = sorted(feature_dir.glob("*.feature"))
    return [str(path.resolve().relative_to(workspace_root)).replace("\\", "/") for path in paths]


def display_label(feature_path: Path) -> str:
    text = feature_path.read_text(encoding="utf-8") if feature_path.exists() else ""
    title = feature_title(text)
    return title or feature_path.stem


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_feature_phase_scaffold.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    workspace_root = args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent

    plan_md = resolve_arg_path(args_path, args, "PLAN_MD")
    feature_dir = resolve_arg_path(args_path, args, "FEATURE_SPECS_DIR")
    implementation_dir = resolve_arg_path(args_path, args, "PLAN_IMPLEMENTATION_DIR")
    current_plan_package = resolve_arg_path(args_path, args, "CURRENT_PLAN_PACKAGE")
    tasks_md = (plan_md.parent / "tasks.md") if plan_md else None

    if plan_md is None or feature_dir is None or implementation_dir is None or current_plan_package is None:
        print(
            json.dumps(
                {"ok": False, "reason": "missing PLAN_MD, FEATURE_SPECS_DIR, PLAN_IMPLEMENTATION_DIR, or CURRENT_PLAN_PACKAGE"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    plan_text = plan_md.read_text(encoding="utf-8") if plan_md.exists() else ""
    ordered_paths = extract_impacted_feature_paths(plan_text)
    fallback_used = False
    if not ordered_paths:
        ordered_paths = sorted_feature_paths(feature_dir, workspace_root)
        fallback_used = True

    feature_phases = []
    for index, rel_path in enumerate(ordered_paths, start=2):
        feature_path = (workspace_root / rel_path).resolve()
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
        "fallback_used": fallback_used,
        "current_plan_package": str(current_plan_package),
        "implementation_dir": str(implementation_dir),
        "tasks_md_path": str(tasks_md) if tasks_md else "",
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
