"""argparse entry for `python -m dsl_cli`.

Subcommands:
  generate-dsl-instructions --boundary <name>
                            --specs <path>... --dsl <path>...
                            [--boundaries-root <path>]
  eval                      --dsl <path>... [--shared-dsl <path>]
  query                     [--handler <id>...] [--step-text <text>]
                            [--dsl <path>...] [--shared-dsl <path>]
                            [--source-scope regular|shared|all]

`--boundaries-root` defaults to the canonical on-disk location
(.claude/skills/aibdd-core/assets/boundaries/) so production callers pass only
`--boundary`. Tests may override the root to point at a tempdir.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dsl_cli.orchestrator import run_eval, run_generate_dsl_instructions, run_query
from dsl_cli.reporter import render_eval_report, render_generation_report, render_query_json

# cli.py -> dsl_cli/ -> scripts/ -> aibdd-core/ -> assets/boundaries
_DEFAULT_BOUNDARIES_ROOT = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "boundaries"
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
