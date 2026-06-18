#!/usr/bin/env python3
"""Manage discovery impact-matrix.yml (v2) via init/write/transit-status/remove/read.

Output is always one JSON envelope on stdout: {ok, violations, impacts}.
Exit code is 0 when ok is true, 1 otherwise. Never silent: an unresolved matrix
path, a bad regex, or an invariant breach all surface as `violations`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _path in (_LIB_DIR, _SCRIPTS_DIR):
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from lib.impact_matrix import (  # noqa: E402
    MatrixError,
    MatrixViolation,
    add_spec,
    build_report,
    emit_report_json,
    init_matrix,
    list_impacts,
    load_matrix,
    read_impacts,
    remove_impact,
    transit_status,
    write_impact,
)

OWNERS = (
    "aibdd-flows-specify",
    "aibdd-rules-specify",
    "aibdd-spec-by-example",
    "aibdd-plan",
    "aibdd-api-plan",
    "aibdd-data-plan",
)


def resolve_matrix_path(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    # lazy: only the default-path fallback needs project_args / lib.shared,
    # so a standalone copy that always passes --matrix needs only lib.impact_matrix.
    try:
        from shared.project_args import resolve_key
    except ImportError as exc:
        raise MatrixError(
            [
                MatrixViolation(
                    "args.matrix",
                    "NOT_FOUND",
                    "impact matrix path unresolved: pass --matrix",
                )
            ]
        ) from exc

    matrix_yml = resolve_key("IMPACT_MATRIX_YML")
    if matrix_yml:
        return Path(matrix_yml)
    reports_dir = resolve_key("PLAN_REPORTS_DIR")
    if reports_dir:
        return Path(reports_dir) / "impact-matrix.yml"
    raise MatrixError(
        [
            MatrixViolation(
                location="args.matrix",
                type="NOT_FOUND",
                message=(
                    "impact matrix path unresolved: pass --matrix or provide "
                    ".aibdd/arguments.yml at project CWD"
                ),
            )
        ]
    )


def emit(report: dict[str, object], code: int = 0) -> int:
    sys.stdout.write(emit_report_json(report) + "\n")
    return code


def cmd_init(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    data = init_matrix(path)
    return emit(build_report(ok=True, impacts=list_impacts(data)))


def cmd_write(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    data, _ = write_impact(
        path,
        owner=args.owner,
        quotes=args.quote,
        rationale=args.rationale,
        spec_paths=args.spec or [],
        impact_id=args.id,
    )
    return emit(build_report(ok=True, impacts=list_impacts(data)))


def cmd_add_spec(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    data = add_spec(path, impact_id=args.id, spec_path=args.spec, status=args.status)
    return emit(build_report(ok=True, impacts=list_impacts(data)))


def cmd_transit_status(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    data = transit_status(
        path, impact_id=args.id, spec_path=args.spec, status=args.status
    )
    return emit(build_report(ok=True, impacts=list_impacts(data)))


def cmd_remove(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    data = remove_impact(path, impact_id=args.id, spec_path=args.spec)
    return emit(build_report(ok=True, impacts=list_impacts(data)))


def cmd_read(args: argparse.Namespace) -> int:
    path = resolve_matrix_path(args.matrix)
    if args.spec_path is not None:
        try:
            re.compile(args.spec_path)
        except re.error as exc:
            raise MatrixError(
                [
                    MatrixViolation(
                        location="args.spec_path",
                        type="INVALID_VALUE",
                        message=f"invalid --spec-path regex: {exc}",
                    )
                ]
            ) from exc
    data = load_matrix(path)
    impacts = read_impacts(
        data,
        impact_id=args.id,
        owners=args.owner,
        impact_status=args.impact_status,
        spec_status=args.spec_status,
        spec_path=args.spec_path,
    )
    return emit(build_report(ok=True, impacts=impacts))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage discovery impact-matrix.yml (v2)")
    parser.add_argument("--matrix", type=Path, help="Path to impact-matrix.yml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create an empty v2 impact-matrix.yml")

    write = sub.add_parser("write", help="Create or replace one impact")
    write.add_argument("--id", default=None, help="Existing impact id to replace")
    write.add_argument("--owner", required=True, choices=OWNERS)
    write.add_argument("--quote", required=True, action="append", help="Requirement quote (repeatable)")
    write.add_argument("--rationale", required=True)
    write.add_argument("--spec", action="append", default=None, help="Spec path (repeatable); omit for a spec-less pending impact")

    add_spec_p = sub.add_parser("add-spec", help="Add a new spec to an existing impact")
    add_spec_p.add_argument("--id", required=True)
    add_spec_p.add_argument("--spec", required=True)
    add_spec_p.add_argument("--status", required=True, choices=["inconsistent", "consistent"])

    transit = sub.add_parser("transit-status", help="Set a spec status (--spec), or the impact status (no --spec)")
    transit.add_argument("--id", required=True)
    transit.add_argument("--spec", default=None, help="Spec path; omit to set the impact status")
    transit.add_argument(
        "--status",
        required=True,
        choices=["inconsistent", "consistent", "pending", "resolved"],
    )

    remove = sub.add_parser("remove", help="Remove a spec (or the whole impact)")
    remove.add_argument("--id", required=True)
    remove.add_argument("--spec", default=None, help="Spec path; omit to remove the whole impact")

    read = sub.add_parser("read", help="Read impacts with optional filters")
    read.add_argument("--id", default=None)
    read.add_argument("--owner", action="append", default=None, choices=OWNERS)
    read.add_argument("--impact-status", default=None, choices=["pending", "resolved"])
    read.add_argument("--spec-status", default=None, choices=["inconsistent", "consistent"])
    read.add_argument("--spec-path", default=None, help="Regex matched against spec path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "init": cmd_init,
        "write": cmd_write,
        "add-spec": cmd_add_spec,
        "transit-status": cmd_transit_status,
        "remove": cmd_remove,
        "read": cmd_read,
    }
    try:
        return handlers[args.command](args)
    except MatrixError as exc:
        return emit(build_report(ok=False, violations=exc.violations), 1)
    except FileNotFoundError as exc:
        violation = MatrixViolation(location="args.matrix", type="NOT_FOUND", message=str(exc))
        return emit(build_report(ok=False, violations=[violation]), 1)
    except ValueError as exc:
        violation = MatrixViolation(location="args.matrix", type="INVALID_VALUE", message=str(exc))
        return emit(build_report(ok=False, violations=[violation]), 1)


if __name__ == "__main__":
    raise SystemExit(main())
