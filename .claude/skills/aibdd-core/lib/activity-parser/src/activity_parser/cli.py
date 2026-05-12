"""CLI entry for the activity-parser package.

Usage::

    activity-parser parse <activity-file>.activity    # canonical (plugin MVP)
    activity-parser parse <activity-file>.mmd         # legacy (upstream AIBDD)
    activity-parser paths    --specs-root specs/<feature>/
    activity-parser skeleton --specs-root specs/<feature>/ --out specs/<feature>/test-plan/

Implementation notes:
    MVP — the parser handles the flat event-flow Mermaid dialect defined by
    ``sf-desktop-app-electron/To-Be-整合/README.md``. Mermaid classDiagram /
    stateDiagram variants are out of scope.
"""
from __future__ import annotations

from pathlib import Path

import click

from . import gherkin_skeleton, parser, path


@click.group()
@click.version_option("0.1.0", prog_name="activity-parser")
def main() -> None:
    """Activity DSL parser + Path extractor + Gherkin skeleton emitter."""


@main.command()
@click.argument(
    "activity_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False, readable=True),
)
def parse(activity_file: Path) -> None:
    """Dump the parsed AST of a single activity file."""
    ast = parser.parse_file(activity_file)
    click.echo(parser.format_ast(ast))


@main.command()
@click.option(
    "--specs-root",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    help="Feature package root (contains activities/).",
)
def paths(specs_root: Path) -> None:
    """List Paths extracted from every activity file under <specs-root>/activities/."""
    activities_dir = specs_root / "activities"
    if not activities_dir.is_dir():
        raise click.UsageError(f"no activities/ directory under {specs_root}")
    for activity in sorted([*activities_dir.glob("*.activity"), *activities_dir.glob("*.mmd")]):
        ast = parser.parse_file(activity)
        paths_ = path.extract_paths(ast, policy="node-once")
        click.echo(f"# {activity.name} — {len(paths_)} path(s)")
        for idx, p in enumerate(paths_, 1):
            click.echo(f"  {idx}. {p.title or '(untitled)'}  [{len(p.steps)} step(s)]")


@main.command()
@click.option(
    "--specs-root",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=False),
)
@click.option(
    "--policy", default="node-once", show_default=True, type=click.Choice(["node-once"])
)
@click.option(
    "--out",
    required=True,
    type=click.Path(path_type=Path, file_okay=False),
    help="Output directory for generated .feature skeleton files.",
)
def skeleton(specs_root: Path, policy: str, out: Path) -> None:
    """Emit Gherkin skeleton files (1 per Activity) into <out>/."""
    activities_dir = specs_root / "activities"
    if not activities_dir.is_dir():
        raise click.UsageError(f"no activities/ directory under {specs_root}")
    out.mkdir(parents=True, exist_ok=True)

    for activity in sorted([*activities_dir.glob("*.activity"), *activities_dir.glob("*.mmd")]):
        ast = parser.parse_file(activity)
        paths_ = path.extract_paths(ast, policy=policy)
        slug = activity.stem
        skeleton_text = gherkin_skeleton.emit(slug, paths_)
        target = out / f"{slug}.feature"
        target.write_text(skeleton_text, encoding="utf-8")
        click.echo(f"wrote: {target}")


if __name__ == "__main__":  # pragma: no cover
    main()
