"""Wire dsl_cli modules into the two top-level commands.

`run_generate_dsl_instructions(...)`: HARNESS phase.
  parse specs → diff against resolved entries → load preset plugin →
  call plugin.generate_templates(unresolved) → route templates per file →
  append each bucket → return GenerationReport.

`run_eval(...)`: EVAL phase.
  load dsl files → optionally collect shared-dsl name namespace → run
  universal rule chain → return EvalReport.

Neither function reads cwd. Caller passes all paths (specs, dsl, shared-dsl,
boundaries_root) — for production, aibdd-plan SOP resolves these from
arguments.yml before invoking.
"""

from __future__ import annotations

from pathlib import Path

from dsl_cli.catalog import query_catalog
from dsl_cli.diff import compute_unresolved
from dsl_cli.dsl_reader import index_resolved_parts, load_dsl_files
from dsl_cli.eval_rules.rules import evaluate
from dsl_cli.models import AddedEntry, CatalogMatch, EvalReport, GenerationReport
from dsl_cli.preset_loader import load_preset_plugin
from shared.spec_parsers.dispatcher import dispatch_spec_parser
from dsl_cli.writer import append_templates, route_template_to_file


def run_generate_dsl_instructions(
    boundary: str,
    spec_paths: list[Path],
    dsl_paths: list[Path],
    boundaries_root: Path,
) -> GenerationReport:
    all_parts = []
    for spec in spec_paths:
        parser = dispatch_spec_parser(spec)
        all_parts.extend(parser.parse(spec))

    entries_by_file = load_dsl_files(dsl_paths)
    resolved_targets = index_resolved_parts(entries_by_file)
    unresolved_parts = compute_unresolved(all_parts, resolved_targets)
    skipped = [
        p.target_part_path
        for p in all_parts
        if p.target_part_path not in {u.target_part_path for u in unresolved_parts}
    ]

    plugin = load_preset_plugin(boundary, boundaries_root)
    templates = plugin.generate_templates(unresolved_parts, {})

    added: list[AddedEntry] = []
    by_file: dict[Path, list] = {}
    for template in templates:
        target_file = route_template_to_file(template)
        by_file.setdefault(target_file, []).append(template)
        added.append(
            AddedEntry(
                entry_name=template.name,
                target_file=target_file,
                handler=template.handler,
            )
        )
    for path, group in by_file.items():
        append_templates(path, group)

    return GenerationReport(
        added_entries=added,
        skipped_parts=skipped,
        processed_specs=list(spec_paths),
    )


def run_eval(
    dsl_paths: list[Path],
    shared_dsl_path: Path | None = None,
) -> EvalReport:
    entries_by_file = load_dsl_files(dsl_paths)
    shared_names: set[str] = set()
    if shared_dsl_path and shared_dsl_path.is_file():
        shared_loaded = load_dsl_files([shared_dsl_path])[shared_dsl_path]
        shared_names = {e.name for e in shared_loaded}
    return evaluate(entries_by_file, shared_names)


def run_query(
    dsl_paths: list[Path],
    handlers: list[str] | None = None,
    shared_dsl_path: Path | None = None,
    source_scope: str = "regular",
    step_text: str | None = None,
) -> list[CatalogMatch]:
    if source_scope not in ("regular", "shared", "all"):
        raise ValueError(
            f"source_scope must be regular|shared|all, got {source_scope!r}"
        )
    handler_list = handlers or []
    if not handler_list and not step_text:
        raise ValueError(
            "query requires at least one of --handler or --step-text"
        )
    return query_catalog(
        dsl_paths=dsl_paths,
        handlers=handler_list if handler_list else None,
        step_text=step_text,
        shared_dsl_path=shared_dsl_path,
        source_scope=source_scope,  # type: ignore[arg-type]
    )
