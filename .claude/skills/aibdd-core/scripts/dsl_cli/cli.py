"""argparse entry for `python -m dsl_cli`.

Subcommands:
  generate-dsl-instructions --boundary <name>
                            --specs <path>... --dsl <path>...
                            [--boundaries-root <path>]
  supplement-required-fields --specs <path>... --dsl <path>...
  eval                      --dsl <path>... [--shared-dsl <path>]

`--boundaries-root` defaults to the canonical on-disk location
(.claude/skills/aibdd-core/assets/boundaries/) so production callers pass only
`--boundary`. Tests may override the root to point at a tempdir.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dsl_cli.orchestrator import run_eval, run_generate_dsl_instructions
from dsl_cli.reporter import (
    render_eval_report,
    render_generation_report,
    render_supplement_report,
)
from dsl_cli.supplement import run_supplement

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

    sup = subs.add_parser("supplement-required-fields")
    sup.add_argument("--specs", nargs="+", type=Path, required=True)
    sup.add_argument("--dsl", nargs="+", type=Path, required=True)

    ev = subs.add_parser("eval")
    ev.add_argument("--dsl", nargs="+", type=Path, required=True)
    ev.add_argument("--shared-dsl", type=Path, default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "generate-dsl-instructions":
        report = run_generate_dsl_instructions(
            args.boundary, args.specs, args.dsl, args.boundaries_root
        )
        print(render_generation_report(report))
        return 0
    if args.command == "supplement-required-fields":
        report = run_supplement(args.specs, args.dsl)
        print(render_supplement_report(report))
        return 0
    if args.command == "eval":
        report = run_eval(args.dsl, args.shared_dsl)
        print(render_eval_report(report))
        return 0 if report.status == "PASS" else 1
    return 2
