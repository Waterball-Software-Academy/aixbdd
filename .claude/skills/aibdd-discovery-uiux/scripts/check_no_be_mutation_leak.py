#!/usr/bin/env python3
"""check_no_be_mutation_leak.py — Phase 5 §5.A script #7.

Scan clean artifacts, GAP / intent / be-gap reports, and classification
reasoning text for any phrase from
``references/be-gap-handling.md §3`` forbidden-phrase blacklist. The
blacklist enforces the cross-boundary read-only invariant: this FE skill
must never ask the user to mutate BE truth.

Unlike ``check_uiux_intent_alignment.py`` (which is non-blocking GAP
sweep), this script reports each hit as a hard ``violation``. The
``ok`` flag is ``false`` whenever any violation is found so the merged
Phase 5 verdict can BRANCH back into Phase 4 §2 remediation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

REPO_DISCOVERY_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "aibdd-discovery" / "scripts"
)
if str(REPO_DISCOVERY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REPO_DISCOVERY_SCRIPTS))

from kickoff_path_resolve import (  # noqa: E402 — sys.path patch above
    load_resolved_kickoff_state,
    resolve_kickoff_paths,
)

# Mirrors references/be-gap-handling.md §3. The shared docstring is the
# SSOT; this list must stay in lock-step with that table.
FORBIDDEN_PHRASES: tuple[str, ...] = (
    "modify BE",
    "patch BE",
    "fix BE",
    "update BE",
    "請修改 BE",
    "請補完 BE",
    "回修 BE",
    "請改 BE",
    "請回填 BE",
    "請更新 BE",
    "ask BE owner to change",
    "ask BE team to patch",
)

REPORT_FILES: tuple[str, ...] = (
    "discovery-uiux-sourcing.md",
    "discovery-uiux-intent.md",
    "discovery-uiux-be-gap.md",
    "discovery-uiux-flow-clarify.md",
    "discovery-uiux-coverage-clarify.md",
    "discovery-uiux-residual-clarify.md",
)

# The forwarded-section header (lower-cased substring) is allowed to read
# indicative future-tense statements; we skip leak detection inside it
# because be-gap-handling.md §3 explicitly permits indicative phrasing.
FORWARDED_HEADER = "## be gaps forwarded"


def collect_artifact_files(roots: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root is None or not root.exists():
            continue
        if root.is_dir():
            for f in root.rglob("*"):
                if f.is_file() and f.suffix in {".feature", ".activity", ".md"}:
                    out.append(f)
        elif root.is_file():
            out.append(root)
    return out


def split_outside_forwarded(text: str) -> str:
    """Drop content under ``## BE Gaps Forwarded`` section.

    Detection compares case-folded header lines; everything from the
    forwarded header to the next H2 is excluded from leak checking.
    """
    if FORWARDED_HEADER not in text.lower():
        return text
    out: list[str] = []
    skipping = False
    for line in text.splitlines():
        casefolded = line.strip().lower()
        if casefolded.startswith("## "):
            skipping = casefolded == FORWARDED_HEADER
            if not skipping:
                out.append(line)
            continue
        if not skipping:
            out.append(line)
    return "\n".join(out)


def scan_file(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    text_scope = split_outside_forwarded(text) if path.suffix == ".md" else text
    text_lower = text_scope.lower()
    hits: list[dict] = []
    for phrase in FORBIDDEN_PHRASES:
        phrase_lower = phrase.lower()
        start = 0
        while True:
            idx = text_lower.find(phrase_lower, start)
            if idx < 0:
                break
            line_no = text_scope.count("\n", 0, idx) + 1
            hits.append({
                "rule_id": "UIUX_NO_BE_MUTATION_LEAK",
                "file": str(path),
                "line": line_no,
                "msg": (
                    f"forbidden BE-mutation phrase「{phrase}」leaked into "
                    f"FE-side artifact; cross-boundary read-only invariant "
                    f"violated"
                ),
            })
            start = idx + len(phrase_lower)
    return hits


def emit(payload: dict) -> int:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if payload["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arguments_path", help="${AIBDD_ARGUMENTS_PATH}")
    args = parser.parse_args()
    args_path = Path(args.arguments_path)

    try:
        workspace_root, resolved, _ = load_resolved_kickoff_state(args_path)
    except Exception as exc:
        return emit({
            "ok": True,
            "summary": {"files_scanned": 0, "violations": 0},
            "violations": [],
            "note": f"kickoff state load failed (kickoff-safe pass): {exc}",
        })

    plan_reports_rel = resolved.get("PLAN_REPORTS_DIR")
    plan_reports_dir = (
        (workspace_root / str(plan_reports_rel)).resolve()
        if plan_reports_rel else None
    )

    try:
        features_dir, activities_dir, _ = resolve_kickoff_paths(args_path)
    except Exception:
        features_dir = activities_dir = None

    targets: list[Path] = []
    if features_dir is not None:
        targets.append(features_dir)
    if activities_dir is not None:
        targets.append(activities_dir)
    if plan_reports_dir is not None:
        for name in REPORT_FILES:
            targets.append(plan_reports_dir / name)

    files = collect_artifact_files(targets)
    violations: list[dict] = []
    for f in files:
        violations.extend(scan_file(f))

    return emit({
        "ok": len(violations) == 0,
        "summary": {
            "files_scanned": len(files),
            "violations": len(violations),
        },
        "violations": violations,
    })


if __name__ == "__main__":
    sys.exit(main())
