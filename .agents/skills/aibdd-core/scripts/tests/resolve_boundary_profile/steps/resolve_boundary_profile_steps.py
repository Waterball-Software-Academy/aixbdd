"""Resolve-boundary-profile BDD step definitions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given, then, when

_CLI = Path(__file__).resolve().parents[3] / "cli" / "resolve_boundary_profile.py"

_BOUNDARY_YML_RELPATH = "specs/architecture/boundary.yml"
_BOUNDARIES_ROOT_RELPATH = "boundaries"


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _project_root(context) -> Path:
    return getattr(context, "active_project", context.tmp_root)


@given("a temporary project directory at the default test path")
def step_default_project(context):
    context.active_project = context.tmp_root


@given('a boundaries assets root with a "{btype}" base profile:')
def step_base_profile(context, btype: str):
    target = _project_root(context) / _BOUNDARIES_ROOT_RELPATH / btype / "profile.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@given('a boundary file at "{relpath}" with content:')
def step_boundary_file(context, relpath: str):
    target = _project_root(context) / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@when("resolve_boundary_profile CLI is run")
def step_run_cli(context):
    proc = subprocess.run(
        [
            "python3",
            str(_CLI),
            "--boundary-yml",
            _BOUNDARY_YML_RELPATH,
            "--boundaries-root",
            _BOUNDARIES_ROOT_RELPATH,
        ],
        text=True,
        capture_output=True,
        cwd=_project_root(context),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.returncode == 0 else None


@then("CLI exit code is {code:d}")
def step_exit_code(context, code: int):
    assert context.last_result.returncode == code, context.last_result.stderr


@then("CLI stdout should be empty")
def step_stdout_empty(context):
    assert context.last_result.stdout == ""


@then("CLI stderr should equal:")
def step_stderr_equals(context):
    actual = _normalize_text(context.last_result.stderr)
    expected = _normalize_text(context.text)
    assert actual == expected, f"stderr={actual!r} expected={expected!r}"


@then("CLI JSON output should equal:")
def step_json_output_equals(context):
    expected = json.loads(context.text or "{}")
    assert context.last_json == expected, f"actual={context.last_json!r}"
