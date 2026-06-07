"""Resolve the merged boundary profile.

The merged profile is the committed base preset (``boundaries/<type>/profile.yml``)
overlaid with the optional ``profile_overrides`` declared in the project's
``boundary.yml``. Overrides replace whole top-level keys — never a deep merge —
so an override block must restate the complete key it replaces. No validation is
performed: the override is trusted as written, and a missing referenced skill
fails naturally later at the consuming specifier-delegation step.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared.repo_root import repo_root_from_module

PROFILE_FILENAME = "profile.yml"

_REPO_ROOT = repo_root_from_module()
CORE_BOUNDARIES_ROOT = _REPO_ROOT / ".claude/skills/aibdd-core/assets/boundaries"
DEFAULT_BOUNDARY_YML = _REPO_ROOT / "specs/architecture/boundary.yml"


class BoundaryProfileError(Exception):
    """Raised when the merged profile cannot be produced."""


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment guard
        raise BoundaryProfileError(f"PyYAML is required to parse {path}") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise BoundaryProfileError(f"expected YAML mapping in {path}")
    return data


def merge_profile(
    base: dict[str, Any], overrides: dict[str, Any]
) -> dict[str, Any]:
    """Overlay ``overrides`` onto ``base`` by whole top-level key replacement."""
    merged = dict(base)
    for key, value in overrides.items():
        merged[key] = value
    return merged


def resolve_merged_profile(
    boundary_yml: Path,
    boundaries_root: Path = CORE_BOUNDARIES_ROOT,
) -> dict[str, Any]:
    boundary_yml = Path(boundary_yml)
    if not boundary_yml.is_file():
        raise BoundaryProfileError(f"boundary.yml not found at {boundary_yml}")
    boundary = _load_yaml(boundary_yml)

    boundary_type = boundary.get("type")
    if not isinstance(boundary_type, str) or not boundary_type.strip():
        raise BoundaryProfileError("boundary.yml has no 'type' field")

    base_path = Path(boundaries_root) / boundary_type / PROFILE_FILENAME
    if not base_path.is_file():
        raise BoundaryProfileError(
            f"base profile not found for boundary type '{boundary_type}' "
            f"at {base_path}"
        )
    base = _load_yaml(base_path)

    overrides = boundary.get("profile_overrides") or {}
    if not isinstance(overrides, dict):
        raise BoundaryProfileError(
            "boundary.yml profile_overrides must be a mapping"
        )

    return merge_profile(base, overrides)


def emit_profile_json(profile: dict[str, Any]) -> str:
    return json.dumps(profile, ensure_ascii=False, indent=2)
