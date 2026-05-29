"""Handler-candidate BDD step definitions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given, then, when

from lib.handler_candidates import (
    HandlerCandidateQuestion,
    apply_in_place_update,
    discover_dsl_paths,
    repo_root_from_module,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = repo_root_from_module()


def _write_file(context, relpath: str) -> Path:
    text = context.text or ""
    if text.startswith("\n"):
        text = text[1:]
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.last_file_path = target
    return target


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _format_questions(questions: list[HandlerCandidateQuestion]) -> str:
    lines: list[str] = []
    for q in questions:
        lines.append(f"- where: {q.path.name}:{q.line_no}")
        lines.append(f"  type: {q.kind}")
        lines.append(f"  text: {q.text}")
    return "\n".join(lines)


def _dsl_paths(context) -> tuple[list[Path], Path | None]:
    contracts_dir = context.tmp_root / "contracts"
    data_dir = context.tmp_root / "data"
    shared = context.files.get("shared_dsl")
    return discover_dsl_paths(contracts_dir, data_dir), shared


@given('a temporary file at "{relpath}" with content')
@given('a temporary file at "{relpath}" with content:')
def step_create_temp_file(context, relpath: str):
    _write_file(context, relpath)


@given('a temporary shared DSL file at "{relpath}" with content')
@given('a temporary shared DSL file at "{relpath}" with content:')
def step_create_shared_dsl(context, relpath: str):
    target = _write_file(context, relpath)
    context.files["shared_dsl"] = target


@given("handler-candidate apply is run on the last feature file")
@when("handler-candidate apply is run on the last feature file")
def step_apply_handler_candidates(context):
    regular_paths, shared = _dsl_paths(context)
    context.last_questions = []
    context.last_changed, context.last_updated_blocks = apply_in_place_update(
        context.last_file_path,
        regular_dsl_paths=regular_paths,
        shared_dsl_path=shared,
        questions=context.last_questions,
        cwd=context.tmp_root,
    )


@when("handler-candidate apply is run again on the last feature file")
def step_apply_handler_candidates_again(context):
    step_apply_handler_candidates(context)


@when("apply_handler_candidates CLI is run on the last feature file")
def step_run_apply_cli(context):
    feature_path = context.last_file_path
    script = _SCRIPTS_DIR / "cli" / "apply_handler_candidates.py"
    proc = subprocess.run(
        [
            "python3",
            str(script),
            str(feature_path),
            "--contracts-dir",
            str(context.tmp_root / "contracts"),
            "--data-dir",
            str(context.tmp_root / "data"),
            "--shared-dsl",
            str(context.files.get("shared_dsl", context.tmp_root / "shared/boundary.dsl.yml")),
            "--cwd",
            str(context.tmp_root),
        ],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.returncode == 0 else None


@then("CLI exit code is 0")
def step_cli_ok(context):
    assert context.last_result.returncode == 0


@then("the last feature file content should equal:")
def step_feature_content_equals(context):
    actual = context.last_file_path.read_text(encoding="utf-8")
    expected = context.text or ""
    assert _normalize_text(actual) == _normalize_text(expected)


@then("handler candidate questions should equal:")
def step_questions_equal(context):
    actual = _format_questions(context.last_questions)
    expected = context.text or ""
    assert _normalize_text(actual) == _normalize_text(expected)


@then("CLI apply JSON report should equal:")
def step_cli_apply_json_report_equals(context):
    expected = json.loads(context.text or "{}")
    assert context.last_json == expected


@then('no file exists at "{relpath}"')
def step_no_file_exists(context, relpath: str):
    assert not (context.tmp_root / relpath).exists()
