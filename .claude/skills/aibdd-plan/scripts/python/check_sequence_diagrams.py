#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import emit, read_args, resolve_arg_path, violation


SEQ_RE = re.compile(r"^(.+)\.(happy|alt|err)\.sequence\.mmd$")
PLAN_REF_RE = re.compile(r"`([^`]*implementation/sequences/[^`]+\.sequence\.mmd)`")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_sequence_diagrams.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    violations = []

    plan_spec = resolve_arg_path(args_path, args, "PLAN_SPEC")
    if plan_spec is None:
        violations.append(violation("PLAN_SPEC_UNRESOLVED", str(args_path), "PLAN_SPEC is missing or unresolved"))
        return emit(False, "sequence diagram check", violations)

    current_plan_package = plan_spec.parent
    plan_md = resolve_arg_path(args_path, args, "PLAN_MD") or (current_plan_package / "plan.md")
    seq_dir = resolve_arg_path(args_path, args, "PLAN_SEQUENCE_DIR") or (current_plan_package / "implementation" / "sequences")

    if not seq_dir.is_dir():
        violations.append(violation("SEQUENCE_DIR_MISSING", str(seq_dir), "sequence directory is missing"))
        return emit(False, "sequence diagram check", violations)

    seq_files = sorted(seq_dir.glob("*.sequence.mmd"))
    categories: set[str] = set()
    for f in seq_files:
        name = f.name
        if ".backend.sequence.mmd" in name:
            violations.append(violation("SEQUENCE_LEGACY_BACKEND_NAME", str(f), "legacy *.backend.sequence.mmd is not allowed"))
        m = SEQ_RE.match(name)
        if not m:
            violations.append(violation("SEQUENCE_NAME_INVALID", str(f), "filename must be <scenario>.<happy|alt|err>.sequence.mmd"))
            continue
        scenario, category = m.groups()
        categories.add(category)
        if not scenario.strip():
            violations.append(violation("SEQUENCE_SCENARIO_EMPTY", str(f), "scenario slug is empty"))

    for required in ("happy", "alt", "err"):
        if required not in categories:
            violations.append(violation("SEQUENCE_CATEGORY_MISSING", str(seq_dir), f"missing at least one {required} sequence"))

    if not plan_md.is_file():
        violations.append(violation("PLAN_MD_MISSING", str(plan_md), "plan.md is missing"))
    else:
        text = plan_md.read_text(encoding="utf-8")
        refs = {Path(ref).name for ref in PLAN_REF_RE.findall(text)}
        existing = {f.name for f in seq_files}
        for missing_ref in sorted(existing - refs):
            violations.append(violation("SEQUENCE_NOT_LISTED_IN_PLAN", str(plan_md), f"{missing_ref} exists but is not listed in plan.md"))
        for stale_ref in sorted(refs - existing):
            violations.append(violation("SEQUENCE_PLAN_REF_MISSING_FILE", str(plan_md), f"{stale_ref} is listed but file is missing"))

    return emit(not violations, "sequence diagram check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
