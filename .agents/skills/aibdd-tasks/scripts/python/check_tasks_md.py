#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import add_tasks_cli_arguments, basename_no_suffix, emit, feature_title, load_tasks_context, violation


PHASE_RE = re.compile(r"^# Phase (\d+) - (.+?)\s*$", re.MULTILINE)


def phase_headers(text: str) -> list[tuple[int, str]]:
    return [(int(num), title.strip()) for num, title in PHASE_RE.findall(text)]


def section_has_required_headings(section: str) -> bool:
    return "## RED" in section and "## GREEN" in section and "## Refactor" in section


def split_phase_sections(text: str) -> list[str]:
    starts = [m.start() for m in PHASE_RE.finditer(text)]
    if not starts:
        return []
    starts.append(len(text))
    return [text[starts[i] : starts[i + 1]] for i in range(len(starts) - 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check tasks.md structure")
    add_tasks_cli_arguments(parser)
    parser.add_argument("--tasks-md-basename", default="tasks.md")
    args = parser.parse_args()
    violations: list[dict[str, object]] = []

    try:
        ctx = load_tasks_context(args)
    except SystemExit as exc:
        violations.append(violation("TASKS_CONTEXT_INVALID", str(args.arguments_yml), str(exc)))
        return emit(False, "tasks.md structure check", violations)

    truth_root = Path(ctx["truth_boundary_root"])
    expected_paths: list[str] = ctx["ordered_feature_paths"]
    tasks_md_path = Path(ctx["tasks_md"]).parent / args.tasks_md_basename

    if not tasks_md_path.exists():
        violations.append(violation("TASKS_MD_MISSING", str(tasks_md_path), f"{tasks_md_path.name} not found"))
        return emit(False, "tasks.md structure check", violations)

    tasks_text = tasks_md_path.read_text(encoding="utf-8")
    headers = phase_headers(tasks_text)
    sections = split_phase_sections(tasks_text)

    if not headers:
        violations.append(violation("TASKS_PHASES_MISSING", str(tasks_md_path), "no phase headings found"))
        return emit(False, "tasks.md structure check", violations)

    expected_total = len(expected_paths) + 2
    if len(headers) != expected_total:
        violations.append(
            violation(
                "TASKS_PHASE_COUNT_MISMATCH",
                str(tasks_md_path),
                f"expected {expected_total} phases from impacted feature count {len(expected_paths)}, got {len(headers)}",
            )
        )

    for index, (num, _title) in enumerate(headers, start=1):
        if num != index:
            violations.append(
                violation(
                    "TASKS_PHASE_NUMBERING_INVALID",
                    str(tasks_md_path),
                    f"phase numbering must be sequential: expected {index}, got {num}",
                )
            )

    if headers[0][1] != "Infra setup":
        violations.append(violation("INFRA_PHASE_MISSING", str(tasks_md_path), "first phase must be `Infra setup`"))
    if headers[-1][1] != "Integration":
        violations.append(violation("INTEGRATION_PHASE_MISSING", str(tasks_md_path), "last phase must be `Integration`"))

    feature_sections = sections[1:-1]
    for idx, rel_path in enumerate(expected_paths):
        if idx >= len(feature_sections):
            break
        header_title = headers[idx + 1][1]
        feature_path = (truth_root / rel_path).resolve()
        expected_labels = {basename_no_suffix(rel_path)}
        if feature_path.exists():
            title = feature_title(feature_path.read_text(encoding="utf-8"))
            if title:
                expected_labels.add(title)
        if not any(label in header_title for label in expected_labels):
            violations.append(
                violation(
                    "FEATURE_PHASE_LABEL_MISMATCH",
                    str(tasks_md_path),
                    f"phase {idx + 2} title `{header_title}` does not match impacted feature `{rel_path}`",
                )
            )
        if not section_has_required_headings(feature_sections[idx]):
            violations.append(
                violation(
                    "FEATURE_PHASE_HEADINGS_MISSING",
                    str(tasks_md_path),
                    f"feature phase for `{rel_path}` must contain RED/GREEN/Refactor headings",
                )
            )

    return emit(not violations, "tasks.md structure check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
