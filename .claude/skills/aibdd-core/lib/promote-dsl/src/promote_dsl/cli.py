"""CLI entry for the promote-dsl package.

Usage::

    promote-dsl scan --specs-root specs/
    promote-dsl propose --specs-root specs/ --threshold 20
    promote-dsl apply --proposal path/to/promotion-proposal.md --dsl-core .specify/memory/dsl.md

Implementation notes:
    MVP — modules intentionally implement only the minimum plumbing needed
    for the end-to-end workflow to run; canonicalize / infra-utility heuristics
    live in ``docs/sub-proposals/01-dsl-promotion-detail.md``.
"""
from __future__ import annotations

from pathlib import Path

import click

from . import applier, proposal, scanner


@click.group()
@click.version_option("0.1.0", prog_name="promote-dsl")
def main() -> None:
    """DSL Two-Tier promotion executor for spec-kit-aibdd."""


@main.command()
@click.option(
    "--specs-root",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    help="Root of the specs tree (usually ``specs/``).",
)
@click.option(
    "--threshold",
    default=20,
    show_default=True,
    type=int,
    help="Gate threshold — cross-spec-package reuse count required to surface a candidate.",
)
def scan(specs_root: Path, threshold: int) -> None:
    """Report reuseability stats per boundary dsl.md entry."""
    result = scanner.scan_specs(specs_root, threshold=threshold)
    click.echo(scanner.format_report(result))


@main.command()
@click.option(
    "--specs-root",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=False),
)
@click.option("--threshold", default=20, show_default=True, type=int)
@click.option(
    "--out",
    default=None,
    type=click.Path(path_type=Path, dir_okay=False),
    help="Where to write promotion-proposal.md; defaults to <specs-root>/promotion-proposal.md",
)
def propose(specs_root: Path, threshold: int, out: Path | None) -> None:
    """Emit a promotion-proposal.md when the gate fires."""
    result = scanner.scan_specs(specs_root, threshold=threshold)
    if not result.candidates:
        click.echo("Gate not fired — no candidates above threshold.")
        return
    target = out or (specs_root / "promotion-proposal.md")
    proposal.write_proposal(result, target)
    click.echo(f"Proposal written: {target}")


@main.command()
@click.option(
    "--proposal",
    "proposal_path",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--dsl-core",
    required=True,
    type=click.Path(path_type=Path, dir_okay=False),
    help="Path to .specify/memory/dsl.md",
)
@click.option(
    "--dry-run", is_flag=True, default=False, help="Preview the move plan without touching files."
)
def apply(proposal_path: Path, dsl_core: Path, dry_run: bool) -> None:
    """Apply a reviewed promotion proposal."""
    plan = applier.build_plan(proposal_path, dsl_core)
    click.echo(applier.format_plan(plan))
    if dry_run:
        click.echo("dry-run — no files written.")
        return
    applier.execute_plan(plan)
    click.echo("Applied.")


if __name__ == "__main__":  # pragma: no cover
    main()
