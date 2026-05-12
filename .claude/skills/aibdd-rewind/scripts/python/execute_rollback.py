#!/usr/bin/env python3
"""Execute a /aibdd-rewind rule entry against the live filesystem.

Emits a JSON object on stdout:
    {
      "phase_id": "...",
      "erases_skill": "...",
      "chain": [...phase_ids in apply order...],
      "deleted_files":  [...absolute paths...],
      "deleted_dirs":   [...],
      "reverted_files": [...],
      "rule_only_files": [...]
    }

Mirrors `preview_rollback.py` but performs the writes. For each rule in
the chain (prerequisites first, then the requested rule), order matters:
1. Delete named files.
2. Delete glob-matched files.
3. Delete directories recursively.
4. Revert skeleton files (overwrite with the rule-table body).
5. Reduce feature files to rule-only shape.

Rule-oriented: same single-purpose helpers as the preview, kept idempotent.
"""

from __future__ import annotations

import json
import shutil
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


def _delete_named_files(rule_paths: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    deleted: list[str] = []
    for raw in rule_paths:
        p = resolve_path(workspace, raw, args, boundary)
        assert_inside_workspace(workspace, p)
        if p.is_file():
            p.unlink()
            deleted.append(str(p))
    return deleted


def _delete_glob_files(rule_globs: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    deleted: list[str] = []
    for raw in rule_globs:
        expanded = resolve_path(workspace, raw, args, boundary)
        try:
            rel = expanded.relative_to(workspace)
        except ValueError:
            assert_inside_workspace(workspace, expanded)
            continue
        for hit in sorted(workspace.glob(str(rel))):
            assert_inside_workspace(workspace, hit)
            if hit.is_file():
                hit.unlink()
                deleted.append(str(hit))
    return deleted


def _delete_dirs(rule_dirs: tuple[str, ...], workspace: Path, args: dict[str, str], boundary: str | None) -> list[str]:
    deleted: list[str] = []
    for raw in rule_dirs:
        p = resolve_path(workspace, raw, args, boundary)
        assert_inside_workspace(workspace, p)
        if p.is_dir():
            shutil.rmtree(p)
            deleted.append(str(p))
    return deleted


def _revert_skeletons(
    rule_reverts: tuple[dict[str, str], ...],
    workspace: Path,
    args: dict[str, str],
    boundary: str | None,
) -> list[str]:
    reverted: list[str] = []
    for entry in rule_reverts:
        raw_path = str(entry.get("path") or "")
        body = str(entry.get("body") or "")
        if not raw_path:
            continue
        p = resolve_path(workspace, raw_path, args, boundary)
        assert_inside_workspace(workspace, p)
        # Skip when parent directory is missing — mirrors preview's guard.
        # When a chain rule has already deleted the parent (e.g. kickoff rule
        # erases TRUTH_FUNCTION_PACKAGE after the chained aibdd-discovery rule
        # tried to revert BOUNDARY_PACKAGE_DSL inside it), we must not
        # resurrect that directory. Without this guard idempotency breaks:
        # every subsequent rewind run would re-create then re-delete the
        # skeleton file in an endless oscillation.
        if not p.parent.is_dir():
            continue
        if not p.is_file() or p.read_text(encoding="utf-8") != body:
            p.write_text(body, encoding="utf-8")
            reverted.append(str(p))
    return reverted


def _revert_features_to_rule_only(
    rule_globs: tuple[str, ...],
    workspace: Path,
    args: dict[str, str],
    boundary: str | None,
) -> list[str]:
    """Reduce each feature file matching `rule_globs` to rule-only shape.
    Idempotent — files already in rule-only shape are skipped (no write)."""
    rewritten: list[str] = []
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
                hit.write_text(reduced, encoding="utf-8")
                rewritten.append(str(hit))
    return rewritten


def execute_rule(rule: RuleEntry, workspace: Path, args: dict[str, str], boundary: str | None) -> dict:
    deleted_files = [
        *_delete_named_files(rule.delete_files, workspace, args, boundary),
        *_delete_glob_files(rule.delete_files_glob, workspace, args, boundary),
    ]
    deleted_dirs = _delete_dirs(rule.delete_dirs, workspace, args, boundary)
    reverted_files = _revert_skeletons(rule.revert_to_skeleton, workspace, args, boundary)
    rule_only_files = _revert_features_to_rule_only(rule.revert_feature_to_rule_only, workspace, args, boundary)
    return {
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
        "reverted_files": reverted_files,
        "rule_only_files": rule_only_files,
    }


def execute(rules: list[RuleEntry], workspace: Path, args: dict[str, str], boundary: str | None) -> dict:
    """Apply every rule in the chain (prerequisites first, then the requested
    rule). Aggregate the results across all rules into one report."""
    deleted_files: list[str] = []
    deleted_dirs: list[str] = []
    reverted_files: list[str] = []
    rule_only_files: list[str] = []

    for rule in rules:
        sub = execute_rule(rule, workspace, args, boundary)
        deleted_files.extend(sub["deleted_files"])
        deleted_dirs.extend(sub["deleted_dirs"])
        reverted_files.extend(sub["reverted_files"])
        rule_only_files.extend(sub["rule_only_files"])

    head = rules[-1]  # the requested rule
    return {
        "phase_id": head.phase_id,
        "erases_skill": head.erases_skill,
        "chain": [r.phase_id for r in rules],
        "deleted_files": sorted(set(deleted_files)),
        "deleted_dirs": sorted(set(deleted_dirs)),
        "reverted_files": sorted(set(reverted_files)),
        "rule_only_files": sorted(set(rule_only_files)),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: execute_rollback.py <arguments.yml> <phase_id>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    phase_id = sys.argv[2].strip()

    args = read_arguments(args_path)
    workspace = workspace_root(args_path).resolve()
    boundary = boundary_id_from_args(args_path, args)
    rules_path = Path(__file__).resolve().parent.parent.parent / "references" / "phase-rollback-rules.yml"
    rules = load_rule_chain(rules_path, phase_id)

    result = execute(rules, workspace, args, boundary)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
