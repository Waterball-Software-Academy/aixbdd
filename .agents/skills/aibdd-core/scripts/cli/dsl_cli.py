#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "ruamel.yaml>=0.18,<0.19",
#   "prance>=25.4.8,<26",
#   "openapi-spec-validator>=0.7.1",
# ]
# ///
"""argparse entry for dsl_cli.

Preferred invocation:

    uv run .claude/skills/aibdd-core/scripts/cli/dsl_cli.py <subcommand> ...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_LIB_DIR = _SCRIPTS_DIR / "lib"
for path in (_LIB_DIR, _SCRIPTS_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from dsl_cli.orchestrator import run_eval, run_generate_dsl_instructions, run_query  # noqa: E402
from dsl_cli.reporter import render_eval_report, render_generation_report, render_query_json  # noqa: E402

_DEFAULT_BOUNDARIES_ROOT = (
    Path(__file__).resolve().parents[2] / "assets" / "boundaries"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dsl_cli")
    subs = parser.add_subparsers(dest="command", required=True)

    gen = subs.add_parser("generate-dsl-instructions")
    gen.add_argument("--boundary", required=True)
    gen.add_argument("--specs", nargs="+", type=Path, required=True)
    gen.add_argument("--dsl", nargs="+", type=Path, required=True)
    gen.add_argument("--boundaries-root", type=Path, default=_DEFAULT_BOUNDARIES_ROOT)

    ev = subs.add_parser("eval")
    ev.add_argument("--dsl", nargs="+", type=Path, required=True)
    ev.add_argument("--shared-dsl", type=Path, default=None)

    q = subs.add_parser("query")
    q.add_argument("--handler", action="append", default=None)
    q.add_argument("--step-text", default=None)
    q.add_argument("--dsl", action="append", type=Path, default=[])
    q.add_argument("--shared-dsl", type=Path, default=None)
    q.add_argument(
        "--source-scope",
        choices=("regular", "shared", "all"),
        default="regular",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "generate-dsl-instructions":
        report = run_generate_dsl_instructions(
            args.boundary, args.specs, args.dsl, args.boundaries_root
        )
        print(render_generation_report(report))
        return 0
    if args.command == "eval":
        report = run_eval(args.dsl, args.shared_dsl)
        print(render_eval_report(report))
        return 0 if report.status == "PASS" else 1
    if args.command == "query":
        handlers = args.handler or []
        if not handlers and not args.step_text:
            print(
                "query requires at least one of --handler or --step-text",
                file=sys.stderr,
            )
            return 1
        try:
            matches = run_query(
                args.dsl,
                handlers if handlers else None,
                args.shared_dsl,
                args.source_scope,
                step_text=args.step_text,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(render_query_json(matches), end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
