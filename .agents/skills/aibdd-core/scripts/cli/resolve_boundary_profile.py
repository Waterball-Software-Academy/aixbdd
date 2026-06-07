#!/usr/bin/env python3
"""Resolve the merged boundary profile and emit it as JSON.

Single read path for $BOUNDARY_PROFILE: base preset for the active boundary type,
overlaid with boundary.yml profile_overrides (whole top-level key replacement).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _path in (_LIB_DIR, _SCRIPTS_DIR):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from shared.boundary_profile import (  # noqa: E402
    CORE_BOUNDARIES_ROOT,
    DEFAULT_BOUNDARY_YML,
    BoundaryProfileError,
    emit_profile_json,
    resolve_merged_profile,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve merged boundary profile (base preset + boundary.yml overrides)"
        )
    )
    parser.add_argument(
        "--boundary-yml",
        type=Path,
        default=DEFAULT_BOUNDARY_YML,
        help="Project boundary.yml path (default: specs/architecture/boundary.yml)",
    )
    parser.add_argument(
        "--boundaries-root",
        type=Path,
        default=CORE_BOUNDARIES_ROOT,
        help="Root of aibdd-core boundary preset assets",
    )
    args = parser.parse_args()

    try:
        profile = resolve_merged_profile(args.boundary_yml, args.boundaries_root)
    except BoundaryProfileError as exc:
        sys.stderr.write(f"[resolve-boundary-profile] {exc}\n")
        return 1

    sys.stdout.write(emit_profile_json(profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
