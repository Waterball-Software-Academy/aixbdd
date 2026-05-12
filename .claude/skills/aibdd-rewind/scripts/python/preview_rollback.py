#!/usr/bin/env python3
"""Preview what /aibdd-rewind would delete or revert for a given phase_id.

Emits a JSON object on stdout:
    {
      "phase_id": "...",
      "erases_skill": "...",
      "chain": [...phase_ids in apply order...],
      "files_to_delete": [...absolute paths...],
      "dirs_to_delete":  [...],
      "files_to_revert": [{"path": "...", "body": "..."}],
      "features_to_rule_only": [{"path": "...", "body": "..."}],
      "no_op_reasons":   [...]
    }

Pure read-only. The executor is `execute_rollback.py`.

Rule-oriented: each "action kind" (file / glob / dir / skeleton / rule-only)
has one single-purpose function fed by the rule table; the main function
composes them in order. `chain_before` is resolved via `load_rule_chain` so
prerequisite rules are applied (in preview: unioned) before the requested
rule itself.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import (
    RuleEntry,
    assert_inside_workspace,
    boundary_id_from_args,
    load_rule_chain,
    read_arguments,
    reduce_feature_to_rule_only,
    resolve_path,
    workspace_root,
)


def _existing_files(rule_paths: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    out: list[str] = []
    for raw in rule_paths:
        p = resolve_path(workspace, raw, args, boundary)
        assert_inside_workspace(workspace, p)
        if p.is_file():
            out.append(str(p))
    return sorted(out)


def _existing_glob(rule_globs: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    out: set[str] = set()
    for raw in rule_globs:
        # Resolve `${VAR}` and `<boundary>` first; THEN glob the result.
        expanded = resolve_path(workspace, raw, args, boundary)
        # The expanded path may itself contain wildcards; glob from workspace root.
        try:
            rel = expanded.relative_to(workspace)
        except ValueError:
            assert_inside_workspace(workspace, expanded)
            continue
        for hit in workspace.glob(str(rel)):
            assert_inside_workspace(workspace, hit)
            if hit.is_file():
                out.add(str(hit))
    return sorted(out)


def _existing_dirs(rule_dirs: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    out: list[str] = []
    for raw in rule_dirs:
        p = resolve_path(workspace, raw, args, boundary)
        assert_inside_workspace(workspace, p)
        if p.is_dir():
            out.append(str(p))
    return sorted(out)


def _skeleton_targets(
    rule_reverts: tuple[dict[str, str], ...],
    workspace: Path,
    args: dict[str, str],
    boundary: str | None,
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for entry in rule_reverts:
        raw_path = str(entry.get("path") or "")
        body = str(entry.get("body") or "")
        if not raw_path:
            continue
        p = resolve_path(workspace, raw_path, args, boundary)
        assert_inside_workspace(workspace, p)
        # Skip when parent directory is missing — the skeleton is logically
        # owned by a phase whose directory has already been erased by a
        # downstream rule in the chain (e.g. chained aibdd-discovery → kickoff
        # reverts BOUNDARY_PACKAGE_DSL but kickoff rule then deletes its parent
        # function package recursively). Without this guard the executor would
        # mkdir(parents=True) and resurrect the just-deleted directory,
        # breaking idempotency.
        if not p.parent.is_dir():
            continue
        # Only include if file is missing OR content differs from skeleton.
        if not p.is_file() or p.read_text(encoding="utf-8") != body:
            out.append({"path": str(p), "body": body})
    return out


def _rule_only_targets(
    rule_globs: tuple[str, ...],
    workspace: Path,
    args: dict[str, str],
    boundary: str | None,
) -> list[dict[str, str]]:
    """For every feature matched by `rule_globs`, return {path, body} where
    body is the proposed rule-only reduction. Files already in rule-only
    shape (reduction == current text) are omitted (no-op idempotency)."""
    out: dict[str, dict[str, str]] = {}
    for raw in rule_globs:
        expanded = resolve_path(workspace, raw, args, boundary)
        try:
            rel = expanded.relative_to(workspace)
        except ValueError:
            assert_inside_workspace(workspace, expanded)
            continue
        for hit in sorted(workspace.glob(str(rel))):
            assert_inside_workspace(workspace, hit)
            if not hit.is_file():
                continue
            current = hit.read_text(encoding="utf-8")
            reduced = reduce_feature_to_rule_only(current)
            if reduced != current:
                out[str(hit)] = {"path": str(hit), "body": reduced}
    return [out[k] for k in sorted(out)]


def derive_delta_for_rule(rule: RuleEntry, workspace: Path, args: dict[str, str], boundary: str | None) -> dict:
    return {
        "files_to_delete": [
            *_existing_files(rule.delete_files, workspace, args, boundary),
            *_existing_glob(rule.delete_files_glob, workspace, args, boundary),
        ],
        "dirs_to_delete": _existing_dirs(rule.delete_dirs, workspace, args, boundary),
        "files_to_revert": _skeleton_targets(rule.revert_to_skeleton, workspace, args, boundary),
        "features_to_rule_only": _rule_only_targets(rule.revert_feature_to_rule_only, workspace, args, boundary),
    }


def derive_delta(rules: list[RuleEntry], workspace: Path, args: dict[str, str], boundary: str | None) -> dict:
    """Union the delta across all rules in the chain (chain order doesn't
    affect the preview union — only the executor cares about ordering)."""
    files: set[str] = set()
    dirs: set[str] = set()
    revert_by_path: dict[str, dict[str, str]] = {}
    rule_only_by_path: dict[str, dict[str, str]] = {}

    for rule in rules:
        sub = derive_delta_for_rule(rule, workspace, args, boundary)
        files.update(sub["files_to_delete"])
        dirs.update(sub["dirs_to_delete"])
        for entry in sub["files_to_revert"]:
            revert_by_path[entry["path"]] = entry
        for entry in sub["features_to_rule_only"]:
            rule_only_by_path[entry["path"]] = entry

    head = rules[-1]  # the requested rule
    return {
        "phase_id": head.phase_id,
        "erases_skill": head.erases_skill,
        "chain": [r.phase_id for r in rules],
        "files_to_delete": sorted(files),
        "dirs_to_delete": sorted(dirs),
        "files_to_revert": [revert_by_path[k] for k in sorted(revert_by_path)],
        "features_to_rule_only": [rule_only_by_path[k] for k in sorted(rule_only_by_path)],
        "no_op_reasons": [],
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: preview_rollback.py <arguments.yml> <phase_id>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    phase_id = sys.argv[2].strip()

    args = read_arguments(args_path)
    workspace = workspace_root(args_path).resolve()
    boundary = boundary_id_from_args(args_path, args)
    rules_path = Path(__file__).resolve().parent.parent.parent / "references" / "phase-rollback-rules.yml"
    rules = load_rule_chain(rules_path, phase_id)

    delta = derive_delta(rules, workspace, args, boundary)
    print(json.dumps(delta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
