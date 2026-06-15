#!/usr/bin/env python3
"""Manage discovery impact-matrix.yml via CRUD, validation, and entry query."""

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

from lib.impact_matrix import (  # noqa: E402
    build_report,
    delete_entry,
    emit_report_json,
    filter_entries,
    init_matrix,
    list_entries,
    load_matrix,
    upsert_entry,
    validate_matrix,
)
from shared.project_args import resolve_key  # noqa: E402


def default_matrix_path(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    matrix_yml = resolve_key("IMPACT_MATRIX_YML")
    if matrix_yml:
        return Path(matrix_yml)
    reports_dir = resolve_key("PLAN_REPORTS_DIR")
    if reports_dir:
        return Path(reports_dir) / "impact-matrix.yml"
    raise FileNotFoundError(
        "impact matrix path unresolved: pass --matrix ${IMPACT_MATRIX_YML} "
        "or provide .aibdd/arguments.yml at project CWD"
    )


def emit_and_exit(report: dict[str, object], code: int = 0) -> int:
    sys.stdout.write(emit_report_json(report) + "\n")
    return code


def cmd_init(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    init_matrix(matrix_path)
    report = build_report(
        ok=True,
        summary="initialized impact matrix",
        entries=list_entries(load_matrix(matrix_path)),
        matrix_yaml=matrix_path.read_text(encoding="utf-8"),
    )
    return emit_and_exit(report)


def cmd_list(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    data = load_matrix(matrix_path)
    report = build_report(
        ok=True,
        summary="listed impact matrix entries",
        entries=list_entries(data),
        matrix_yaml=matrix_path.read_text(encoding="utf-8"),
    )
    return emit_and_exit(report)


def cmd_query(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    data = load_matrix(matrix_path)
    entries = filter_entries(
        data,
        suffix=args.suffix,
        change_types=args.change_type,
        path_prefix=args.path_prefix,
    )
    report = build_report(
        ok=True,
        summary="queried impact matrix entries",
        entries=entries,
    )
    return emit_and_exit(report)


def cmd_upsert(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    _, created = upsert_entry(
        matrix_path,
        entry_path=args.path,
        change_type=args.change_type,
        impact_summary=args.impact_summary,
    )
    data = load_matrix(matrix_path)
    report = build_report(
        ok=True,
        summary="created impact matrix entry" if created else "updated impact matrix entry",
        entries_changed=1,
        entries=list_entries(data),
        matrix_yaml=matrix_path.read_text(encoding="utf-8"),
    )
    return emit_and_exit(report)


def cmd_delete(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    _, deleted = delete_entry(matrix_path, entry_path=args.path)
    data = load_matrix(matrix_path)
    report = build_report(
        ok=True,
        summary="deleted impact matrix entry" if deleted else "impact matrix entry not found",
        entries_changed=1 if deleted else 0,
        entries=list_entries(data),
        matrix_yaml=matrix_path.read_text(encoding="utf-8"),
    )
    return emit_and_exit(report)


def cmd_validate(args: argparse.Namespace) -> int:
    matrix_path = default_matrix_path(args.matrix)
    data = load_matrix(matrix_path)
    questions, warnings = validate_matrix(data, matrix_path=str(matrix_path))
    ok = not questions
    report = build_report(
        ok=ok,
        summary="impact matrix valid" if ok else "impact matrix invalid",
        warnings=warnings,
        questions=questions,
        entries=list_entries(data),
        matrix_yaml=matrix_path.read_text(encoding="utf-8"),
    )
    return emit_and_exit(report, 0 if ok else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage discovery impact-matrix.yml")
    parser.add_argument("--matrix", type=Path, help="Path to impact-matrix.yml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create an empty impact-matrix.yml")

    sub.add_parser("list", help="List all entries")

    query = sub.add_parser("query", help="Filter entries by suffix, change_type, or path prefix")
    query.add_argument("--suffix", default=None, help="Match entry path suffix, e.g. .feature")
    query.add_argument(
        "--change-type",
        action="append",
        default=None,
        choices=["read_only_compare", "update", "add", "conditional_update", "remove"],
        help="Match one or more change_type values (OR semantics)",
    )
    query.add_argument(
        "--path-prefix",
        default=None,
        help="Match entry paths starting with this boundary-root-relative prefix",
    )

    upsert = sub.add_parser("upsert", help="Create or update one entry")
    upsert.add_argument("--path", required=True, help="Relative boundary-root file path")
    upsert.add_argument(
        "--change-type",
        required=True,
        choices=["read_only_compare", "update", "add", "conditional_update", "remove"],
    )
    upsert.add_argument("--impact-summary", required=True)

    delete = sub.add_parser("delete", help="Delete one entry by path")
    delete.add_argument("--path", required=True)

    sub.add_parser("validate", help="Validate impact-matrix.yml")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "init": cmd_init,
        "list": cmd_list,
        "query": cmd_query,
        "upsert": cmd_upsert,
        "delete": cmd_delete,
        "validate": cmd_validate,
    }
    try:
        return handlers[args.command](args)
    except (FileNotFoundError, ValueError) as exc:
        report = build_report(ok=False, summary=str(exc))
        sys.stderr.write(f"[manage-impact-matrix] {exc}\n")
        return emit_and_exit(report, 1)


if __name__ == "__main__":
    raise SystemExit(main())
