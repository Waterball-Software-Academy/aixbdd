"""Build-mapping BDD step definitions."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from behave import given, then, when

# parents[3] = scripts dir; build_mapping.py lives at its root
_CLI = Path(__file__).resolve().parents[3] / "build_mapping.py"


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _run(args: list[str], *, drop_data_dir_env: bool = False, stdin: str | None = None):
    env = dict(os.environ)
    if drop_data_dir_env:
        env.pop("DATA_DIR", None)
    return subprocess.run(
        ["uv", "run", str(_CLI), *args],
        text=True,
        capture_output=True,
        input=stdin,
        env=env,
    )


@given("a temporary data directory")
def step_temp_data_dir(context):
    # data_dir already created by before_scenario; this documents intent.
    assert context.data_dir.is_dir()


@given('a schema file "{filename}" with content:')
def step_schema_file(context, filename: str):
    target = context.data_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@given('an existing mapping "{relpath}" with content:')
def step_existing_mapping(context, relpath: str):
    target = context.data_dir / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@when("build_mapping CLI is run against the data directory")
def step_run_against_data_dir(context):
    context.last_result = _run([str(context.data_dir)])


@when("build_mapping plan is run against the data directory")
def step_run_plan(context):
    context.last_result = _run(["plan", str(context.data_dir)])


@when("build_mapping apply is run against the data directory with naming:")
def step_run_apply(context):
    context.last_result = _run(
        ["apply", str(context.data_dir)], stdin=context.text
    )


@when("build_mapping CLI is run against a missing data directory")
def step_run_missing_dir(context):
    missing = context.tmp_root / "does-not-exist"
    context.last_result = _run([str(missing)])


@when("build_mapping CLI is run with no arguments")
def step_run_no_args(context):
    context.last_result = _run([], drop_data_dir_env=True)


@then("CLI exit code is {code:d}")
def step_exit_code(context, code: int):
    assert context.last_result.returncode == code, (
        f"expected exit {code}, got {context.last_result.returncode}\n"
        f"stderr: {context.last_result.stderr}"
    )


@then("the generated mapping should equal:")
def step_mapping_equals(context):
    output_path = context.data_dir / "entity_to_table_mapping.yml"
    assert output_path.is_file(), "mapping file was not generated"
    actual = _normalize_text(output_path.read_text(encoding="utf-8"))
    assert actual == _normalize_text(context.text), (
        f"mapping mismatch\n--- actual ---\n{actual}"
    )


@then('the generated mapping at "{relpath}" should equal:')
def step_mapping_at_equals(context, relpath: str):
    output_path = context.data_dir / relpath
    assert output_path.is_file(), f"mapping file was not generated at {relpath}"
    actual = _normalize_text(output_path.read_text(encoding="utf-8"))
    assert actual == _normalize_text(context.text), (
        f"mapping mismatch at {relpath}\n--- actual ---\n{actual}"
    )


@then("no mapping file should be generated at the data directory root")
def step_no_root_mapping(context):
    output_path = context.data_dir / "entity_to_table_mapping.yml"
    assert not output_path.exists(), (
        f"unexpected root mapping generated at {output_path}"
    )


@then('CLI stderr should contain "{fragment}"')
def step_stderr_contains(context, fragment: str):
    assert fragment in context.last_result.stderr, (
        f"stderr missing {fragment!r}\nstderr: {context.last_result.stderr}"
    )


@then('CLI stdout should contain "{fragment}"')
def step_stdout_contains(context, fragment: str):
    assert fragment in context.last_result.stdout, (
        f"stdout missing {fragment!r}\nstdout: {context.last_result.stdout}"
    )


@then('the plan for folder "{folder}" should list new tables {tables}')
def step_plan_new_tables(context, folder: str, tables: str):
    plan = json.loads(context.last_result.stdout)
    entry = next((f for f in plan["folders"] if f["folder"] == folder), None)
    assert entry is not None, f"folder {folder!r} not in plan: {plan}"
    expected = json.loads(tables)
    assert entry["new_tables"] == expected, (
        f"new_tables for {folder}: expected {expected}, got {entry['new_tables']}"
    )


@then('the plan for folder "{folder}" should preserve existing {mapping}')
def step_plan_existing(context, folder: str, mapping: str):
    plan = json.loads(context.last_result.stdout)
    entry = next((f for f in plan["folders"] if f["folder"] == folder), None)
    assert entry is not None, f"folder {folder!r} not in plan: {plan}"
    expected = json.loads(mapping)
    assert entry["existing"] == expected, (
        f"existing for {folder}: expected {expected}, got {entry['existing']}"
    )


@when("build_mapping CLI is run with DATA_DIR env var pointing to the data directory")
def step_run_with_env_var(context):
    env = dict(os.environ)
    env["DATA_DIR"] = str(context.data_dir)
    context.last_result = subprocess.run(
        ["uv", "run", str(_CLI)],
        text=True,
        capture_output=True,
        env=env,
    )
