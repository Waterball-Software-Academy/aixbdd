#!/usr/bin/env python3
"""Apply handler candidate enrichment to project .feature files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.handler_candidates import (
    build_apply_report,
    discover_dsl_paths,
    discover_feature_paths,
    emit_apply_report_json,
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
    parser = argparse.ArgumentParser(
        description="Apply handler candidate lists to .feature # @dsl blocks"
    )
    parser.add_argument(
        "feature_paths",
        nargs="*",
        type=Path,
        help="Explicit .feature paths; default: discover from arguments.yml",
    )
    parser.add_argument("--contracts-dir", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--shared-dsl", type=Path)
    parser.add_argument("--cwd", type=Path, help="Working directory for dsl_cli query paths")
    args = parser.parse_args()

    contracts_dir = args.contracts_dir
    data_dir = args.data_dir
    shared_dsl = args.shared_dsl
    if contracts_dir is None:
        contracts_str = resolve_key("CONTRACTS_DIR")
        contracts_dir = Path(contracts_str) if contracts_str else _REPO_ROOT / "specs/contracts"
    if data_dir is None:
        data_str = resolve_key("DATA_DIR")
        data_dir = Path(data_str) if data_str else _REPO_ROOT / "specs/data"
    if shared_dsl is None:
        shared_str = resolve_key("BOUNDARY_SHARED_DSL")
        shared_dsl = Path(shared_str) if shared_str else None

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
        sys.stderr.write("[apply-handler-candidates] no .feature files found\n")
        return 1

    regular_dsl_paths = discover_dsl_paths(contracts_dir, data_dir)
    work_cwd = args.cwd or _REPO_ROOT

    from lib.handler_candidates import HandlerCandidateQuestion, apply_in_place_update

    questions: list[HandlerCandidateQuestion] = []
    changed_features: list[str] = []
    updated_block_count = 0
    for fp in feature_paths:
        changed, blocks_updated = apply_in_place_update(
            fp,
            regular_dsl_paths=regular_dsl_paths,
            shared_dsl_path=shared_dsl if shared_dsl and shared_dsl.is_file() else None,
            questions=questions,
            cwd=work_cwd,
        )
        updated_block_count += blocks_updated
        if changed:
            changed_features.append(fp.name)

    report = build_apply_report(
        changed_count=len(changed_features),
        feature_count=len(feature_paths),
        changed_features=changed_features,
        updated_block_count=updated_block_count,
        questions=questions,
    )
    sys.stdout.write(emit_apply_report_json(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
