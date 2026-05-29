#!/usr/bin/env python3
"""Apply selected when format to all When <dsl> placeholders in a .feature file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.when_format import (
    WhenFormatQuestion,
    apply_when_format_in_place,
    build_apply_report,
    emit_apply_report_json,
    repo_root_from_module,
)

_REPO_ROOT = repo_root_from_module()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace When <dsl> placeholders with a selected when format"
    )
    parser.add_argument(
        "feature_path",
        type=Path,
        help="Target .feature file path",
    )
    parser.add_argument(
        "--format",
        required=True,
        help="Selected when step format; parameter placeholders are preserved as-is",
    )
    args = parser.parse_args()

    feature_path = args.feature_path
    if feature_path.suffix != ".feature" or not feature_path.is_file():
        sys.stderr.write(f"[apply-when-format] not a .feature file: {feature_path}\n")
        return 1

    questions: list[WhenFormatQuestion] = []
    changed, updated_when_count = apply_when_format_in_place(
        feature_path,
        when_format=args.format,
        questions=questions,
    )

    changed_features = [feature_path.name] if changed else []
    report = build_apply_report(
        changed_count=len(changed_features),
        feature_count=1,
        changed_features=changed_features,
        updated_when_count=updated_when_count,
        questions=questions,
    )
    sys.stdout.write(emit_apply_report_json(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
