"""When-format BDD step definitions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given, then, when

from lib.when_format import (
    WhenFormatQuestion,
    apply_when_format_in_place,
    repo_root_from_module,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = repo_root_from_module()


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _format_questions(questions: list[WhenFormatQuestion]) -> str:
    lines: list[str] = []
    for q in questions:
        lines.append(f"- where: {q.path.name}:{q.line_no}")
        lines.append(f"  type: {q.kind}")
        lines.append(f"  text: {q.text}")
    return "\n".join(lines)


def _read_when_format(context) -> str:
    text = context.text or ""
    if text.startswith("\n"):
        text = text[1:]
    return text.rstrip("\n")


def _run_apply(context, when_format: str) -> None:
    context.last_when_format = when_format
    context.last_questions = []
    context.last_changed, context.last_updated_whens = apply_when_format_in_place(
        context.last_file_path,
        when_format=when_format,
        questions=context.last_questions,
    )


@given("when-format apply is run on the last feature file with format:")
@when("when-format apply is run on the last feature file with format:")
def step_apply_when_format(context):
    _run_apply(context, _read_when_format(context))


@when("when-format apply is run again on the last feature file with format:")
def step_apply_when_format_again(context):
    _run_apply(context, _read_when_format(context))


@when("when-format apply is run on the last feature file with empty format")
def step_apply_when_format_empty(context):
    _run_apply(context, "")


@when("apply_when_format CLI is run on the last feature file with format:")
def step_run_apply_when_format_cli(context):
    feature_path = context.last_file_path
    when_format = _read_when_format(context)
    script = _SCRIPTS_DIR / "cli" / "apply_when_format.py"
    proc = subprocess.run(
        [
            "python3",
            str(script),
            str(feature_path),
            "--format",
            when_format,
        ],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.returncode == 0 else None


@then("when format questions should equal:")
def step_when_format_questions_equal(context):
    actual = _format_questions(context.last_questions)
    expected = context.text or ""
    assert _normalize_text(actual) == _normalize_text(expected)
