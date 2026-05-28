#!/usr/bin/env python3
"""Load active boundary form-lock profile and emit resolved config as JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.form_lock import (
    CORE_BOUNDARIES_ROOT,
    DEFAULT_BOUNDARY_YML,
    emit_config_json,
    load_active_profile,
    load_profile_from_path,
    resolve_profile_for_boundary_type,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Load form-lock.profile.yml for active boundary")
    parser.add_argument(
        "--boundary-yml",
        type=Path,
        default=DEFAULT_BOUNDARY_YML,
        help="Project boundary.yml path (default: specs/architecture/boundary.yml)",
    )
    parser.add_argument(
        "--boundary-type",
        help="Override boundary type instead of reading boundary.yml",
    )
    parser.add_argument(
        "--profile-path",
        type=Path,
        help="Load profile YAML directly (for tests)",
    )
    parser.add_argument(
        "--boundaries-root",
        type=Path,
        default=CORE_BOUNDARIES_ROOT,
        help="Root of aibdd-core boundary assets",
    )
    args = parser.parse_args()

    try:
        if args.profile_path:
            config = load_profile_from_path(args.profile_path)
        elif args.boundary_type:
            config = resolve_profile_for_boundary_type(
                args.boundary_type, args.boundaries_root
            )
        else:
            config = load_active_profile(args.boundary_yml, args.boundaries_root)
    except (FileNotFoundError, ValueError) as e:
        sys.stderr.write(f"[load-form-lock-profile] {e}\n")
        return 1

    sys.stdout.write(emit_config_json(config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
