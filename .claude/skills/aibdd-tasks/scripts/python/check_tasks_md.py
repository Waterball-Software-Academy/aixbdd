#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import basename_no_suffix, emit, extract_impacted_feature_paths, feature_title, read_args, resolve_arg_path, violation


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
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: check_tasks_md.py <arguments.yml> [tasks_md_basename]", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    tasks_basename = Path(sys.argv[2]).name if len(sys.argv) == 3 else "tasks.md"
    args = read_args(args_path)
    violations: list[dict[str, object]] = []
    workspace_root = args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent

    plan_md_path = resolve_arg_path(args_path, args, "PLAN_MD")
    feature_dir = resolve_arg_path(args_path, args, "FEATURE_SPECS_DIR")
    if plan_md_path is None or feature_dir is None:
        violations.append(violation("MISSING_REQUIRED_PATH", str(args_path), "PLAN_MD or FEATURE_SPECS_DIR missing"))
        return emit(False, "tasks.md structure check", violations)

    tasks_md_path = plan_md_path.parent / tasks_basename
    if not tasks_md_path.exists():
        violations.append(violation("TASKS_MD_MISSING", str(tasks_md_path), f"{tasks_basename} not found"))
        return emit(False, "tasks.md structure check", violations)

    plan_text = plan_md_path.read_text(encoding="utf-8")
    tasks_text = tasks_md_path.read_text(encoding="utf-8")
    impacted = extract_impacted_feature_paths(plan_text)
    headers = phase_headers(tasks_text)
    sections = split_phase_sections(tasks_text)

    if not headers:
        violations.append(violation("TASKS_PHASES_MISSING", str(tasks_md_path), "no phase headings found"))
        return emit(False, "tasks.md structure check", violations)

    expected_total = len(impacted) + 2
    if len(headers) != expected_total:
        violations.append(
            violation(
                "TASKS_PHASE_COUNT_MISMATCH",
                str(tasks_md_path),
                f"expected {expected_total} phases from impacted feature count {len(impacted)}, got {len(headers)}",
            )
        )

    for index, (num, _title) in enumerate(headers, start=1):
        if num != index:
            violations.append(
                violation("TASKS_PHASE_NUMBERING_INVALID", str(tasks_md_path), f"phase numbering must be sequential: expected {index}, got {num}")
            )

    if headers[0][1] != "Infra setup":
        violations.append(violation("INFRA_PHASE_MISSING", str(tasks_md_path), "first phase must be `Infra setup`"))
    if headers[-1][1] != "Integration":
        violations.append(violation("INTEGRATION_PHASE_MISSING", str(tasks_md_path), "last phase must be `Integration`"))

    feature_sections = sections[1:-1]
    for idx, rel_path in enumerate(impacted):
        if idx >= len(feature_sections):
            break
        header_title = headers[idx + 1][1]
        feature_path = (workspace_root / rel_path).resolve()
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
