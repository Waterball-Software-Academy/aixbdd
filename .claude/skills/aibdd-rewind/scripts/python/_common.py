#!/usr/bin/env python3
"""Shared helpers for /aibdd-rewind preview & execute scripts.

Kept deliberately small:
- argument-file loading (with `${VAR}` expansion + `<boundary>` resolution);
- workspace-root path sandboxing;
- rule-table loading (with `chain_before` recursive resolution);
- feature-file rule-only reduction (used by both preview & execute).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_VAR_RE = re.compile(r"\$\{([^}]+)\}")


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML required to parse {path}: {exc}")
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if text.strip() else None


def read_arguments(args_path: Path) -> dict[str, str]:
    data = _load_yaml(args_path)
    if not isinstance(data, dict):
        raise SystemExit(f"arguments file must be a YAML mapping: {args_path}")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def expand_vars(value: str, mapping: dict[str, str], limit: int = 10) -> str:
    """Repeatedly substitute `${VAR}` against `mapping` until stable or `limit` hit."""
    result = value
    for _ in range(limit):
        replaced = _VAR_RE.sub(lambda m: mapping.get(m.group(1), m.group(0)), result)
        if replaced == result:
            return result
        result = replaced
    return result


def boundary_id_from_args(args_path: Path, args: dict[str, str]) -> str | None:
    boundary_yml_rel = expand_vars(args.get("BOUNDARY_YML", ""), args)
    if not boundary_yml_rel:
        return None
    p = Path(boundary_yml_rel)
    if not p.is_absolute():
        p = workspace_root(args_path) / p
    p = p.resolve()
    if not p.is_file():
        return None
    raw = _load_yaml(p) or {}
    boundaries = raw.get("boundaries") if isinstance(raw, dict) else None
    if not boundaries:
        return None
    bid = str(boundaries[0].get("id") or "").strip()
    return bid or None


def workspace_root(args_path: Path) -> Path:
    """The project root that owns `.aibdd/arguments.yml`."""
    return args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent


def resolve_path(workspace: Path, raw: str, args: dict[str, str], boundary: str | None) -> Path:
    """Expand `${VAR}` and `<boundary>` placeholders, return a resolved absolute path."""
    expanded = expand_vars(raw, args)
    if boundary:
        expanded = expanded.replace("<boundary>", boundary)
    p = Path(expanded)
    if not p.is_absolute():
        p = workspace / p
    return p.resolve()


def assert_inside_workspace(workspace: Path, candidate: Path) -> None:
    """Refuse paths that escape the workspace — sandbox per safety-guardrails.md."""
    try:
        candidate.relative_to(workspace)
    except ValueError:
        raise SystemExit(f"path escapes workspace sandbox: {candidate}")


@dataclass(frozen=True)
class RuleEntry:
    phase_id: str            # The phase skill that "just finished" — preserved.
    erases_skill: str        # The immediate downstream skill whose outputs are deleted.
    description: str
    delete_files: tuple[str, ...]
    delete_files_glob: tuple[str, ...]
    delete_dirs: tuple[str, ...]
    revert_to_skeleton: tuple[dict[str, str], ...]
    revert_feature_to_rule_only: tuple[str, ...]
    chain_before: tuple[str, ...]


def normalize_phase_id(raw: str) -> str:
    """Strip leading slash, lowercase, trim — accepts `/aibdd-plan`, `aibdd-plan`, ` AIBDD-Plan `."""
    return raw.strip().lstrip("/").lower()


def _parse_rule_entry(entry: dict) -> RuleEntry:
    return RuleEntry(
        phase_id=str(entry.get("phase_id")),
        erases_skill=str(entry.get("erases_skill") or ""),
        description=str(entry.get("description") or ""),
        delete_files=tuple(entry.get("delete_files") or ()),
        delete_files_glob=tuple(entry.get("delete_files_glob") or ()),
        delete_dirs=tuple(entry.get("delete_dirs") or ()),
        revert_to_skeleton=tuple(entry.get("revert_to_skeleton") or ()),
        revert_feature_to_rule_only=tuple(entry.get("revert_feature_to_rule_only") or ()),
        chain_before=tuple(entry.get("chain_before") or ()),
    )


def load_rule(rules_path: Path, phase_id: str) -> RuleEntry:
    raw = _load_yaml(rules_path)
    if not isinstance(raw, dict) or not isinstance(raw.get("phases"), list):
        raise SystemExit(f"rule table malformed: {rules_path}")
    target = normalize_phase_id(phase_id)
    for entry in raw["phases"]:
        if not isinstance(entry, dict):
            continue
        if normalize_phase_id(str(entry.get("phase_id", ""))) == target:
            return _parse_rule_entry(entry)
    raise SystemExit(f"phase_id `{phase_id}` not found in {rules_path}")


def load_rule_chain(rules_path: Path, phase_id: str) -> list[RuleEntry]:
    """Return the ordered list of rules to apply: `chain_before` prerequisites
    first (recursively, depth-first), then the requested rule itself.

    Cycles are broken by tracking visited phase_ids; each phase_id appears
    at most once in the returned list (first occurrence wins).
    """
    raw = _load_yaml(rules_path)
    if not isinstance(raw, dict) or not isinstance(raw.get("phases"), list):
        raise SystemExit(f"rule table malformed: {rules_path}")
    by_id: dict[str, dict] = {}
    for entry in raw["phases"]:
        if isinstance(entry, dict):
            pid = normalize_phase_id(str(entry.get("phase_id", "")))
            if pid:
                by_id[pid] = entry

    target = normalize_phase_id(phase_id)
    if target not in by_id:
        raise SystemExit(f"phase_id `{phase_id}` not found in {rules_path}")

    ordered: list[RuleEntry] = []
    seen: set[str] = set()

    def visit(pid: str, stack: tuple[str, ...]) -> None:
        if pid in seen:
            return
        if pid in stack:
            # cycle — bail rather than infinite-loop
            return
        if pid not in by_id:
            raise SystemExit(f"chain_before references unknown phase_id `{pid}`")
        entry = by_id[pid]
        for prereq in entry.get("chain_before") or ():
            visit(normalize_phase_id(str(prereq)), stack + (pid,))
        seen.add(pid)
        ordered.append(_parse_rule_entry(entry))

    visit(target, ())
    return ordered


# ---------------------------------------------------------------------------
# Feature file rule-only reduction
# ---------------------------------------------------------------------------

# Comment lines that /aibdd-spec-by-example-analyze adds and that must be
# stripped to return to rule-only shape.
_REDUCER_COMMENT_KEYS = (
    "@dsl_entry",
    "@binding_keys",
    "@type",
    "@techniques",
    "@dimensions",
    "@given_values",
    "@when_values",
    "@then_values",
    "@values_na",
    "@setup_required",
    "@merge_decision",
    "@cic",
    "@dimension_na",
)

# Block keywords whose entire indented block must be removed.
_BLOCK_KEYWORDS = ("Background:", "Scenario:", "Scenario Outline:", "Examples:")

# Top-level Gherkin keywords that terminate an indented block.
_TOPLEVEL_KEYWORDS = ("Feature:", "Rule:", "Background:", "Scenario:", "Scenario Outline:", "Examples:", "@")


def _is_reducer_comment(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return False
    body = stripped[1:].lstrip()
    return any(body.startswith(key) for key in _REDUCER_COMMENT_KEYS)


def _starts_block(line: str) -> bool:
    s = line.lstrip()
    return any(s.startswith(kw) for kw in _BLOCK_KEYWORDS)


def _is_block_terminator(line: str) -> bool:
    """A line that ends the current indented Background/Scenario/Examples block.

    Lines that begin (after indent) with a top-level Gherkin keyword OR a
    feature-tag (`@`) terminate the block. Blank lines do NOT terminate —
    they may appear inside an Examples table or between steps.
    """
    s = line.lstrip()
    if not s:
        return False
    return any(s.startswith(kw) for kw in _TOPLEVEL_KEYWORDS)


def _ensure_ignore_tag(tag_line: str) -> str:
    """Ensure the feature-header tag line contains `@ignore`. Preserve other tags."""
    parts = tag_line.split()
    has_ignore = any(p == "@ignore" for p in parts)
    if has_ignore:
        return tag_line
    # Prepend @ignore preserving leading indentation (typically none for feature header).
    leading = tag_line[: len(tag_line) - len(tag_line.lstrip())]
    rest = tag_line.lstrip()
    return f"{leading}@ignore {rest}".rstrip() + ("\n" if tag_line.endswith("\n") else "")


def reduce_feature_to_rule_only(text: str) -> str:
    """Reduce a feature file to its rule-only shape.

    Operations (in order, single pass with a small state machine):
      1. Drop entire Background / Scenario / Scenario Outline / Examples blocks
         (the keyword line + its indented body up to the next top-level keyword
         or feature-tag line).
      2. Drop every reducer comment line (`# @dsl_entry`, `# @type`, ...).
      3. Re-add `@ignore` to the feature-header tag line if absent.
      4. Keep Feature: line + description text + Rule: lines (with bodies).

    Idempotent: applying twice yields the same output.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    skipping_block = False
    feature_header_seen = False

    for line in lines:
        if skipping_block:
            # Continue skipping until we hit a line that terminates the block.
            if _is_block_terminator(line):
                skipping_block = False
                # Fall through — re-evaluate this line.
            else:
                continue

        # Strip reducer comments outright.
        if _is_reducer_comment(line):
            continue

        # Detect block start.
        if _starts_block(line):
            skipping_block = True
            continue

        # Feature header tag detection — first @-prefixed line at column 0
        # before `Feature:` is the header tag line.
        if not feature_header_seen:
            stripped = line.lstrip()
            if stripped.startswith("@"):
                line = _ensure_ignore_tag(line)
                feature_header_seen = True  # tag line consumed
                out.append(line)
                continue
            if stripped.startswith("Feature:"):
                # No tag line preceded the Feature: line — synthesize one.
                indent = line[: len(line) - len(line.lstrip())]
                out.append(f"{indent}@ignore\n")
                feature_header_seen = True
                out.append(line)
                continue

        out.append(line)

    # Trim trailing blank lines so the file ends with exactly one newline.
    while out and out[-1].strip() == "":
        out.pop()
    if out and not out[-1].endswith("\n"):
        out[-1] = out[-1] + "\n"
    return "".join(out)
