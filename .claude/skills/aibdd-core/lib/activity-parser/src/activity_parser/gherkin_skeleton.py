"""Gherkin skeleton emitter — Path → Scenario body with comment-only steps.

Emitted skeleton satisfies ``test-plan-rules.md``:
    - @flow-oriented + @feature:<slug> tags on Feature
    - Keywords in English, descriptions in Traditional Chinese where the label
      content already is zh-TW (we just pass through the label text)
    - Each Action node → one "When" annotation comment
    - Each BRANCH guard → "Then" annotation comment (pending step-fill)
"""
from __future__ import annotations

from .path import ExtractedPath


def emit(slug: str, paths: list[ExtractedPath]) -> str:
    lines: list[str] = [
        "@flow-oriented",
        f"@feature:{slug}",
        f"Feature: {slug}",
        "",
        "  # TODO(phase-5b): populate Background with shared business preconditions.",
        "  # Technical mocking details MUST stay in DSL entry L4, not on the scenario surface.",
        "",
    ]
    for p in paths:
        lines.append(f"  @path:{p.number}")
        lines.append(f"  Scenario: {p.title or f'Path {p.number}'}")
        if not p.steps:
            lines.append("    # TODO(phase-5b): skeleton empty — verify activity has action nodes.")
            lines.append("")
            continue
        for idx, step in enumerate(p.steps, 1):
            if step.kind == "BRANCH":
                lines.append(f"    # Then (branch guard={step.guard!r}): {step.label}")
            else:
                verb = "Given" if idx == 1 else "When"
                lines.append(f"    # {verb} ({step.kind} id={step.node_id}): {step.label}")
        lines.append("")
    return "\n".join(lines)
