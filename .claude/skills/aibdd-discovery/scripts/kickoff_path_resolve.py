"""Resolve `.aibdd/arguments.yml` + `boundary.yml` into concrete discovery paths.

SSOT: aibdd-kickoff convention — `<boundary>` from boundary id.
After iterative `${VAR}` substitution:

- Kickoff MAY omit `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR`; then behavior paths are
  unbound until `/aibdd-discovery` persists `TRUTH_FUNCTION_PACKAGE`.
- Discovery consumes accepted behavior truth under resolved `FEATURE_SPECS_DIR`
  once bound; plan-session artifacts remain under `CURRENT_PLAN_PACKAGE`.
"""
from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any

import yaml


def _apply_placeholders(s: str, boundary_id: str) -> str:
    return s.replace("<boundary>", boundary_id)


def load_boundary_id(boundary_yml: Path) -> str:
    """Return boundary_id for kickoff single-boundary contract."""
    raw = yaml.safe_load(boundary_yml.read_text(encoding="utf-8")) or {}
    boundaries = raw.get("boundaries") or []
    if not boundaries:
        raise ValueError(f"no boundaries in {boundary_yml}")
    b0 = boundaries[0]
    bid = str(b0.get("id") or "").strip()
    if not bid:
        raise ValueError(f"missing boundary id in {boundary_yml}")
    return bid


def dollar_pass(d: dict[str, Any]) -> dict[str, Any]:
    """Iteratively substitute ${VAR} in string values."""

    def _substitute(mapping: dict[str, Any]) -> dict[str, Any]:
        out = dict(mapping)
        for key, value in list(out.items()):
            if isinstance(value, str):
                prev = None
                current = value
                while current != prev:
                    prev = current
                    current = Template(current).safe_substitute(out)
                out[key] = current
        return out

    return _substitute(d)


def load_resolved_kickoff_state(args_path: Path) -> tuple[Path, dict[str, Any], str]:
    """Return backend_root, resolved args (with placeholders expanded), boundary_id."""

    args_path = args_path.resolve()
    if not args_path.is_file():
        raise FileNotFoundError(f"arguments.yml not found: {args_path}")

    if args_path.parent.name != ".aibdd":
        raise ValueError(f"arguments.yml must live under .aibdd/: {args_path}")
    workspace_root = args_path.parent.parent
    raw = yaml.safe_load(args_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("arguments.yml must be a mapping at top level")

    resolved: dict[str, Any] = {str(k): v for k, v in raw.items()}
    resolved = dollar_pass(resolved)

    boundary_rel = resolved.get("BOUNDARY_YML")
    if not isinstance(boundary_rel, str) or not boundary_rel.strip():
        raise ValueError("BOUNDARY_YML missing after ${} resolve")

    boundary_yml = (workspace_root / boundary_rel.replace("\\", "/")).resolve()
    if not boundary_yml.is_file():
        raise FileNotFoundError(f"boundary.yml not found: {boundary_yml}")

    boundary_id = load_boundary_id(boundary_yml)

    for k, v in list(resolved.items()):
        if isinstance(v, str):
            resolved[k] = _apply_placeholders(v, boundary_id)

    resolved = dollar_pass(resolved)
    return workspace_root, resolved, boundary_id


def resolve_kickoff_paths(
    args_path: Path,
) -> tuple[Path | None, Path | None, dict[str, Any]]:
    """Return (features_dir_or_none, activities_dir_or_none, resolved_args).

    `args_path` is `${AIBDD_CONFIG_DIR}/arguments.yml`.
    When `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` are absent after resolve, dirs are
    ``None`` and callers must `/aibdd-discovery`-bind paths first.
    """
    workspace_root, resolved, boundary_id = load_resolved_kickoff_state(args_path)

    feat = resolved.get("FEATURE_SPECS_DIR")
    act = resolved.get("ACTIVITIES_DIR")

    features_dir: Path | None = None
    activities_dir: Path | None = None

    if isinstance(feat, str) and feat.strip():
        features_dir = (workspace_root / feat.replace("\\", "/")).resolve()
    if isinstance(act, str) and act.strip():
        activities_dir = (workspace_root / act.replace("\\", "/")).resolve()

    return features_dir, activities_dir, resolved


def _resolved_path(workspace_root: Path, resolved: dict[str, Any], key: str) -> str | None:
    value = resolved.get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return str((workspace_root / value.replace("\\", "/")).resolve())


def main() -> None:
    import json
    import sys

    if len(sys.argv) < 2:
        print("usage: kickoff_path_resolve.py <AIBDD_ARGUMENTS_PATH>", file=sys.stderr)
        sys.exit(2)
    args_path = Path(sys.argv[1]).resolve()
    try:
        workspace_root, resolved_state, boundary_id = load_resolved_kickoff_state(args_path)
        features_dir, activities_dir, resolved = resolve_kickoff_paths(args_path)
        specs_root = _resolved_path(workspace_root, resolved_state, "SPECS_ROOT_DIR")
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    behavior_bound = features_dir is not None and activities_dir is not None
    print(
        json.dumps(
            {
                "ok": True,
                "behavior_paths_bound": behavior_bound,
                "boundary_id": boundary_id,
                "specs_root": specs_root,
                "features_dir": str(features_dir) if features_dir else None,
                "activities_dir": str(activities_dir) if activities_dir else None,
                "FEATURE_SPECS_DIR": resolved.get("FEATURE_SPECS_DIR"),
                "ACTIVITIES_DIR": resolved.get("ACTIVITIES_DIR"),
                "PLAN_SPEC": resolved.get("PLAN_SPEC"),
                "PLAN_REPORTS_DIR": resolved.get("PLAN_REPORTS_DIR"),
                "TRUTH_BOUNDARY_ROOT": resolved.get("TRUTH_BOUNDARY_ROOT"),
                "TRUTH_FUNCTION_PACKAGE": resolved.get("TRUTH_FUNCTION_PACKAGE"),
                "BOUNDARY_SHARED_DSL": resolved.get("BOUNDARY_SHARED_DSL"),
                "BOUNDARY_PACKAGE_DSL": resolved.get("BOUNDARY_PACKAGE_DSL"),
                "resolved_paths": {
                    "plan_spec": _resolved_path(workspace_root, resolved, "PLAN_SPEC"),
                    "plan_reports_dir": _resolved_path(workspace_root, resolved, "PLAN_REPORTS_DIR"),
                    "truth_boundary_root": _resolved_path(workspace_root, resolved, "TRUTH_BOUNDARY_ROOT"),
                    "truth_function_package": _resolved_path(workspace_root, resolved, "TRUTH_FUNCTION_PACKAGE"),
                    "boundary_shared_dsl": _resolved_path(workspace_root, resolved, "BOUNDARY_SHARED_DSL"),
                    "boundary_package_dsl": _resolved_path(workspace_root, resolved, "BOUNDARY_PACKAGE_DSL"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
