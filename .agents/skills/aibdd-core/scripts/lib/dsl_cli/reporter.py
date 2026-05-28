"""Render `GenerationReport` and `EvalReport` for terminal display.

Plain text, deterministic line ordering. Used by `dsl_cli` subcommands after
the orchestrator returns.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from dsl_cli.models import CatalogMatch, EvalReport, GenerationReport


def render_generation_report(report: GenerationReport) -> str:
    lines = ["Generation Report", "================="]
    if report.added_entries:
        lines.append(f"Added {len(report.added_entries)} entries:")
        for added in report.added_entries:
            lines.append(
                f"  - {added.entry_name} -> {added.target_file.as_posix()} "
                f"({added.handler})"
            )
    else:
        lines.append("Added 0 entries.")
    if report.skipped_parts:
        lines.append(f"Skipped {len(report.skipped_parts)} already-resolved parts:")
        for sp in report.skipped_parts:
            lines.append(f"  - {sp}")
    if report.processed_specs:
        lines.append(f"Processed {len(report.processed_specs)} spec files:")
        for spec in report.processed_specs:
            lines.append(f"  - {spec.as_posix()}")
    return "\n".join(lines) + "\n"


def render_eval_report(report: EvalReport) -> str:
    lines = [f"Eval Report — {report.status}", "==================="]
    lines.append(f"Total entries: {report.total_entries}")
    if not report.violations:
        lines.append("No violations.")
        return "\n".join(lines) + "\n"
    lines.append(f"Violations ({len(report.violations)}):")
    for v in report.violations:
        lines.append(
            f"  - [{v.rule_id}] {v.entry_name} @ {v.entry_file.as_posix()}"
        )
        lines.append(f"    {v.message}")
        if v.hint:
            lines.append(f"    hint: {v.hint}")
    return "\n".join(lines) + "\n"


def render_query_json(matches: list[CatalogMatch]) -> str:
    payload = [asdict(match) for match in matches]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
