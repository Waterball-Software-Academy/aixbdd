"""When format apply: replace When <dsl> placeholders with selected format."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WHEN_DSL_PATTERN = re.compile(r"^(\s*)When\s+<dsl>\s*$")


def repo_root_from_module() -> Path:
    module_dir = Path(__file__).resolve()
    for parent in module_dir.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    raise FileNotFoundError("cannot locate repo root from when_format module")


@dataclass
class WhenFormatQuestion:
    path: Path
    line_no: int
    kind: str
    text: str


def apply_when_format_in_place(
    path: Path,
    *,
    when_format: str,
    questions: list[WhenFormatQuestion],
) -> tuple[bool, int]:
    if not when_format.strip():
        questions.append(
            WhenFormatQuestion(
                path=path,
                line_no=1,
                kind="missing-when-format",
                text=f"--format must be a non-empty when step format for {path.name}",
            )
        )
        return False, 0

    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    updated_when_count = 0
    changed = False

    for idx, line in enumerate(lines):
        match = WHEN_DSL_PATTERN.match(line)
        if not match:
            continue
        indent = match.group(1)
        replacement = f"{indent}When {when_format}"
        if line != replacement:
            lines[idx] = replacement
            changed = True
        updated_when_count += 1

    if changed:
        trailing_newline = original.endswith("\n")
        rendered = "\n".join(lines)
        if trailing_newline or not rendered.endswith("\n"):
            rendered += "\n"
        path.write_text(rendered, encoding="utf-8")

    return changed, updated_when_count


def question_to_json_dict(question: WhenFormatQuestion) -> dict[str, str]:
    return {
        "where": f"{question.path.name}:{question.line_no}",
        "type": question.kind,
        "text": question.text,
    }


def build_apply_report(
    *,
    changed_count: int,
    feature_count: int,
    changed_features: list[str],
    updated_when_count: int,
    questions: list[WhenFormatQuestion],
) -> dict[str, Any]:
    return {
        "changed_count": changed_count,
        "feature_count": feature_count,
        "changed_features": changed_features,
        "updated_when_count": updated_when_count,
        "questions": [question_to_json_dict(q) for q in questions],
        "report": {
            "summary": (
                f"changed={changed_count} features={feature_count} "
                f"whens={updated_when_count} questions={len(questions)}"
            ),
        },
    }


def emit_apply_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
