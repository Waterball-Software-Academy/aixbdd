"""Resolve-args BDD step definitions."""

from __future__ import annotations

import subprocess
from pathlib import Path

from behave import given, then, when

_CLI = Path(__file__).resolve().parents[3] / "cli" / "resolve_args.py"


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _project_root(context) -> Path:
    return getattr(context, "active_project", context.tmp_root)


@given("a temporary project directory at the default test path")
def step_default_project(context):
    context.active_project = context.tmp_root


@given('project directory "project-a" at the default test path')
def step_project_a(context):
    context.active_project = context.project_a


@given('project directory "project-b" at the default test path')
def step_project_b(context):
    context.active_project = context.project_b


@given('an arguments file at "{relative_path}" with content:')
def step_arguments_file(context, relative_path: str):
    target = _project_root(context) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@when("resolve_args CLI is run with stdin:")
def step_run_resolve_args(context):
    proc = subprocess.run(
        ["python3", str(_CLI)],
        input=context.text,
        text=True,
        capture_output=True,
        cwd=_project_root(context),
    )
    context.last_result = proc


@then("CLI exit code is {code:d}")
def step_exit_code(context, code: int):
    assert context.last_result.returncode == code


@then("CLI stdout should equal:")
def step_stdout_equals(context):
    actual = _normalize_text(context.last_result.stdout)
    assert actual == _normalize_text(context.text)


@then("CLI stderr should equal:")
def step_stderr_equals(context):
    actual = _normalize_text(context.last_result.stderr)
    expected = _normalize_text(context.text)
    if "{ARGS_PATH}" in expected:
        args_path = (_project_root(context) / ".aibdd/arguments.yml").resolve()
        expected = expected.replace("{ARGS_PATH}", str(args_path))
    assert actual == expected


@then("CLI stdout should be empty")
def step_stdout_empty(context):
    assert context.last_result.stdout == ""
