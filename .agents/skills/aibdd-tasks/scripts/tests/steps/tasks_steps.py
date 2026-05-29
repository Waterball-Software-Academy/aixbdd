"""BDD step definitions for aibdd-tasks scripts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given, then, when

_PYTHON_DIR = Path(__file__).resolve().parents[2] / "python"
_RESOLVE_CLI = _PYTHON_DIR / "resolve_tasks_paths.py"
_SCAFFOLD_CLI = _PYTHON_DIR / "build_feature_phase_scaffold.py"
_SCAFFOLD_CHECK_CLI = _PYTHON_DIR / "check_feature_phase_scaffold.py"
_TASKS_CHECK_CLI = _PYTHON_DIR / "check_tasks_md.py"


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _project_root(context) -> Path:
    return context.project_root


@given("a temporary tasks project at the default test path")
def step_default_project(context):
    context.project_root = context.tmp_root


@given('an arguments file at ".aibdd/arguments.yml" with content:')
def step_arguments_file(context):
    target = _project_root(context) / ".aibdd" / "arguments.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.args_path = target


@given('a file at "{relative_path}" with content:')
def step_write_file(context, relative_path: str):
    target = _project_root(context) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@when("resolve_tasks_paths is run")
def step_run_resolve_tasks_paths(context):
    cmd = ["python3", str(_RESOLVE_CLI), str(context.args_path)]
    plan_package = getattr(context, "plan_package", None)
    if plan_package:
        cmd.extend(["--plan-package", plan_package])
    context.last_result = subprocess.run(cmd, capture_output=True, text=True, cwd=_project_root(context))
    if context.last_result.returncode == 0 and context.last_result.stdout.strip():
        context.last_json = json.loads(context.last_result.stdout)


@when('resolve_tasks_paths is run with plan package "{plan_package}"')
def step_run_resolve_with_plan_package(context, plan_package: str):
    context.plan_package = plan_package
    step_run_resolve_tasks_paths(context)


@when("build_feature_phase_scaffold is run")
def step_run_scaffold(context):
    cmd = ["python3", str(_SCAFFOLD_CLI), str(context.args_path)]
    plan_package = getattr(context, "plan_package", None)
    if plan_package:
        cmd.extend(["--plan-package", plan_package])
    feature_paths = getattr(context, "feature_paths_json", None)
    if feature_paths:
        cmd.extend(["--feature-paths", feature_paths])
    context.last_result = subprocess.run(cmd, capture_output=True, text=True, cwd=_project_root(context))
    if context.last_result.returncode == 0 and context.last_result.stdout.strip():
        context.last_json = json.loads(context.last_result.stdout)


@when('build_feature_phase_scaffold is run with plan package "{plan_package}"')
def step_run_scaffold_with_plan_package(context, plan_package: str):
    context.plan_package = plan_package
    step_run_scaffold(context)


@when('build_feature_phase_scaffold is run with plan package "{plan_package}" and feature paths:')
def step_run_scaffold_with_paths(context, plan_package: str):
    context.plan_package = plan_package
    context.feature_paths_json = context.text.strip()
    step_run_scaffold(context)


@given('build_feature_phase_scaffold is run with plan package "{plan_package}" and feature paths:')
def step_given_scaffold_with_paths(context, plan_package: str):
    context.plan_package = plan_package
    context.feature_paths_json = context.text.strip()
    step_run_scaffold(context)


@when('check_tasks_md is run with plan package "{plan_package}" and feature paths:')
def step_run_tasks_check_with_paths(context, plan_package: str):
    context.plan_package = plan_package
    context.feature_paths_json = context.text.strip()
    step_run_tasks_check(context)


@when("check_feature_phase_scaffold is run")
def step_run_scaffold_check(context):
    cmd = ["python3", str(_SCAFFOLD_CHECK_CLI), str(context.args_path)]
    plan_package = getattr(context, "plan_package", None)
    if plan_package:
        cmd.extend(["--plan-package", plan_package])
    feature_paths = getattr(context, "feature_paths_json", None)
    if feature_paths:
        cmd.extend(["--feature-paths", feature_paths])
    context.last_result = subprocess.run(cmd, capture_output=True, text=True, cwd=_project_root(context))
    if context.last_result.stdout.strip():
        context.last_json = json.loads(context.last_result.stdout)


@when("check_tasks_md is run")
def step_run_tasks_check(context):
    cmd = ["python3", str(_TASKS_CHECK_CLI), str(context.args_path)]
    plan_package = getattr(context, "plan_package", None)
    if plan_package:
        cmd.extend(["--plan-package", plan_package])
    feature_paths = getattr(context, "feature_paths_json", None)
    if feature_paths:
        cmd.extend(["--feature-paths", feature_paths])
    context.last_result = subprocess.run(cmd, capture_output=True, text=True, cwd=_project_root(context))
    if context.last_result.stdout.strip():
        context.last_json = json.loads(context.last_result.stdout)


@then("CLI exit code is {code:d}")
def step_exit_code(context, code: int):
    assert context.last_result.returncode == code


@then("JSON ok is {value}")
def step_json_ok(context, value: str):
    expected = value.lower() == "true"
    assert context.last_json is not None
    assert context.last_json.get("ok") is expected


@then("JSON matrix_feature_paths should equal:")
def step_matrix_feature_paths(context):
    expected = json.loads(context.text)
    assert context.last_json is not None
    assert context.last_json.get("matrix_feature_paths") == expected


@then("JSON feature_phases paths should equal:")
def step_feature_phase_paths(context):
    expected = json.loads(context.text)
    assert context.last_json is not None
    actual = [item["feature_path"] for item in context.last_json.get("feature_phases", [])]
    assert actual == expected


@then("JSON reason contains {snippet}")
def step_json_reason_contains(context, snippet: str):
    payload = context.last_json or json.loads(context.last_result.stdout)
    reason = str(payload.get("reason", ""))
    assert snippet in reason


@then("checker summary is {summary}")
def step_checker_summary(context, summary: str):
    assert context.last_json is not None
    assert context.last_json.get("summary") == summary


def _json_field(payload: dict, field_name: str):
    cur = payload
    for part in field_name.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


@then("CLI stdout JSON field {field_name} equals {value}")
def step_stdout_field_equals(context, field_name: str, value: str):
    assert context.last_json is not None
    actual = _json_field(context.last_json, field_name)
    if value.startswith('"') and value.endswith('"'):
        assert actual == value[1:-1]
    elif value.isdigit():
        assert actual == int(value)
    else:
        assert str(actual) == value
