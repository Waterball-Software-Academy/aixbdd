"""Impact-matrix v2 BDD step definitions.

Lib-level steps call the library directly (fast). CLI-level steps run
impact_matrix_cli.py as a subprocess to lock the stdout JSON contract.
A mutating op that breaches an invariant raises MatrixError; the lib-level
When steps catch it and stash the violations for the Then step.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from behave import given, then, when

from lib.impact_matrix import (
    MatrixError,
    add_spec,
    init_matrix,
    load_matrix,
    read_impacts,
    remove_impact,
    repo_root_from_module,
    transit_status,
    write_impact,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[3]
_CLI = _SCRIPTS_DIR / "cli" / "impact_matrix_cli.py"

# id-targeting mutations that share the (impact_id, spec_path, status) signature
_STATUS_OPS = {"add-spec": add_spec, "transit-status": transit_status}


def _normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _snapshot(context) -> None:
    context.matrix_before = (
        context.matrix_path.read_text(encoding="utf-8")
        if context.matrix_path.exists()
        else None
    )


def _capture_violations(context, fn) -> None:
    _snapshot(context)
    try:
        fn()
    except MatrixError as exc:
        context.last_violations = exc.violations


def _run_cli(context, argv: list[str]) -> None:
    _snapshot(context)
    # the subprocess inherits IMPACT_MATRIX_TEST_IDS from os.environ when a
    # scenario declared an id sequence; there is no CLI-facing force flag.
    proc = subprocess.run(
        ["python3", str(_CLI), "--matrix", str(context.matrix_path), *argv],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
        env=dict(os.environ),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


def _resolve_subject(context, subject: str):
    if subject == "read result":
        return context.last_read
    if subject == "violations":
        return [v.as_dict() for v in context.last_violations]
    if subject == "CLI report":
        return context.last_json
    raise KeyError(f"unknown assertion subject: {subject!r}")


# --- Given ------------------------------------------------------------------


@given("an impact matrix at the default test path")
def step_default_matrix(context):
    context.matrix_path.parent.mkdir(parents=True, exist_ok=True)


@given("a matrix file with content:")
def step_matrix_with_content(context):
    context.matrix_path.parent.mkdir(parents=True, exist_ok=True)
    context.matrix_path.write_text(context.text, encoding="utf-8")


@given('the impact id sequence is "{ids}"')
def step_id_sequence(context, ids: str):
    os.environ["IMPACT_MATRIX_TEST_IDS"] = ids


# --- When (lib level) -------------------------------------------------------


@when("impact init runs")
def step_init(context):
    _capture_violations(context, lambda: init_matrix(context.matrix_path))


@when("impact write runs with payload:")
@given("impact write runs with payload:")
def step_write(context):
    payload = json.loads(context.text)
    _capture_violations(
        context,
        lambda: write_impact(
            context.matrix_path,
            owner=payload["owner"],
            quotes=payload["quotes"],
            rationale=payload["rationale"],
            spec_paths=payload["specs"],
            impact_id=payload.get("id"),
        ),
    )


@when('impact {op} runs with id "{impact_id}" spec "{spec}" status "{status}"')
def step_status_op(context, op: str, impact_id: str, spec: str, status: str):
    fn = _STATUS_OPS[op]
    _capture_violations(
        context,
        lambda: fn(
            context.matrix_path, impact_id=impact_id, spec_path=spec, status=status
        ),
    )


@when('impact transit-status runs with id "{impact_id}" status "{status}"')
def step_transit_impact(context, impact_id: str, status: str):
    _capture_violations(
        context,
        lambda: transit_status(context.matrix_path, impact_id=impact_id, status=status),
    )


@when('impact remove runs for whole impact "{impact_id}"')
def step_remove_impact(context, impact_id: str):
    _capture_violations(
        context, lambda: remove_impact(context.matrix_path, impact_id=impact_id)
    )


@when('impact remove runs with id "{impact_id}" spec "{spec}"')
def step_remove_spec(context, impact_id: str, spec: str):
    _capture_violations(
        context,
        lambda: remove_impact(context.matrix_path, impact_id=impact_id, spec_path=spec),
    )


@when("impact read runs")
def step_read_all(context):
    context.last_read = read_impacts(load_matrix(context.matrix_path))


@when("impact read runs with query:")
def step_read_query(context):
    query = json.loads(context.text)
    context.last_read = read_impacts(
        load_matrix(context.matrix_path),
        impact_id=query.get("id"),
        owners=query.get("owners"),
        impact_status=query.get("impact_status"),
        spec_status=query.get("spec_status"),
        spec_path=query.get("spec_path"),
    )


# --- When (CLI level) -------------------------------------------------------


@when("the CLI runs init")
def step_cli_init(context):
    _run_cli(context, ["init"])


@when("the CLI runs with payload:")
def step_cli_payload(context):
    payload = json.loads(context.text)
    _run_cli(context, payload["argv"])


# --- Then -------------------------------------------------------------------


@then("the impact matrix YAML equals:")
def step_yaml_equals(context):
    actual = context.matrix_path.read_text(encoding="utf-8")
    assert _normalize_text(actual) == _normalize_text(context.text), (
        f"\n--- actual ---\n{actual}\n--- expected ---\n{context.text}"
    )


@then("the {subject} should equal:")
def step_subject_equals(context, subject: str):
    actual = _canonical_json(_resolve_subject(context, subject))
    expected = _canonical_json(json.loads(context.text))
    assert actual == expected, f"\n--- actual ---\n{actual}\n--- expected ---\n{expected}"


@then("the matrix file is unchanged")
def step_matrix_unchanged(context):
    after = (
        context.matrix_path.read_text(encoding="utf-8")
        if context.matrix_path.exists()
        else None
    )
    assert after == context.matrix_before, (
        f"\n--- before ---\n{context.matrix_before}\n--- after ---\n{after}"
    )


@then("the CLI exit code is {code:d}")
def step_cli_exit(context, code: int):
    assert context.last_result.returncode == code, (
        f"exit={context.last_result.returncode} stderr={context.last_result.stderr}"
    )
