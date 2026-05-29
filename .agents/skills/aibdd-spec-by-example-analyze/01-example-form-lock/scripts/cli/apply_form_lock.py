#!/usr/bin/env python3
"""Apply form-lock Example skeletons to project .feature files."""

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
    UnknownPrefixQuestion,
    apply_in_place_update,
    build_apply_report,
    discover_feature_paths,
    emit_apply_report_json,
    load_active_profile,
    load_profile_from_path,
    repo_root_from_module,
)

_REPO_ROOT = repo_root_from_module()
_AIBDD_CORE_SCRIPTS = _REPO_ROOT / ".claude/skills/aibdd-core/scripts"
_AIBDD_CORE_LIB = _AIBDD_CORE_SCRIPTS / "lib"
for _path in (_AIBDD_CORE_LIB, _AIBDD_CORE_SCRIPTS):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from shared.project_args import resolve_key  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply form-lock to .feature files")
    parser.add_argument(
        "feature_paths",
        nargs="*",
        type=Path,
        help="Explicit .feature paths; default: discover from arguments.yml",
    )
    parser.add_argument("--boundary-yml", type=Path, default=DEFAULT_BOUNDARY_YML)
    parser.add_argument("--profile-path", type=Path)
    parser.add_argument(
        "--boundaries-root",
        type=Path,
        default=CORE_BOUNDARIES_ROOT,
    )
    args = parser.parse_args()

    try:
        if args.profile_path:
            config = load_profile_from_path(args.profile_path)
        else:
            config = load_active_profile(args.boundary_yml, args.boundaries_root)
    except (FileNotFoundError, ValueError) as e:
        sys.stderr.write(f"[apply-form-lock] {e}\n")
        return 1

    if args.feature_paths:
        feature_paths = [p for p in args.feature_paths if p.suffix == ".feature"]
    else:
        feature_dir_str = resolve_key("FEATURE_SPECS_DIR")
        if feature_dir_str:
            candidate = Path(feature_dir_str)
            feature_paths = (
                discover_feature_paths(candidate)
                if candidate.is_dir()
                else discover_feature_paths(_REPO_ROOT / "specs/packages")
            )
        else:
            feature_paths = discover_feature_paths(_REPO_ROOT / "specs/packages")

    if not feature_paths:
        sys.stderr.write("[apply-form-lock] no .feature files found\n")
        return 1

    questions: list[UnknownPrefixQuestion] = []
    changed_features: list[str] = []
    for fp in feature_paths:
        if apply_in_place_update(fp, config, questions):
            changed_features.append(fp.name)

    report = build_apply_report(
        changed_count=len(changed_features),
        feature_count=len(feature_paths),
        questions=questions,
        changed_features=changed_features,
    )
    sys.stdout.write(emit_apply_report_json(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
