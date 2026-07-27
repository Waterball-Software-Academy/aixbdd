"""BDD step definitions for aibdd-api-plan check_summary_unique.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

_CHECK_CLI = Path(__file__).resolve().parents[2] / "check_summary_unique.py"


def _resolve_python() -> str:
    # behave 可能跑在缺 prance/ruamel 的隔離環境（例：uvx），且該環境的
    # python3 會排在 PATH 最前面；逐一探測 PATH 上的 python3，取第一個
    # 裝有 checker 依賴者，對齊 SOP EXECUTE command 實際用到的直譯器。
    override = os.environ.get("AIBDD_API_PLAN_TEST_PYTHON")
    if override:
        return override
    seen: set[str] = set()
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path_dir) / "python3"
        if not candidate.is_file() or str(candidate) in seen:
            continue
        seen.add(str(candidate))
        probe = subprocess.run(
            [str(candidate), "-c", "import prance, ruamel.yaml"],
            capture_output=True,
        )
        if probe.returncode == 0:
            return str(candidate)
    return sys.executable


_PYTHON = _resolve_python()


@given('a contract file at "{relative_path}" with content:')
def step_contract_file(context, relative_path):
    target = context.contracts_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")


@when("check_summary_unique is run")
def step_run_check(context):
    context.last_result = subprocess.run(
        [_PYTHON, str(_CHECK_CLI), str(context.contracts_dir)],
        capture_output=True,
        text=True,
    )
    assert context.last_result.stdout.strip(), (
        f"checker produced no stdout (exit {context.last_result.returncode}); "
        f"stderr: {context.last_result.stderr}"
    )
    context.last_json = json.loads(context.last_result.stdout)


@then("CLI exit code is {code:d}")
def step_exit_code(context, code):
    result = context.last_result
    assert result.returncode == code, (
        f"expected exit {code}, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@then("JSON ok is {expected}")
def step_json_ok(context, expected):
    expected_bool = expected == "true"
    actual = context.last_json.get("ok")
    assert actual is expected_bool, f"expected ok={expected_bool}, got {actual!r}"


@then('a violation "{check}" with detail containing "{fragment}"')
def step_violation_contains(context, check, fragment):
    violations = context.last_json.get("violations", [])
    matched = [
        v for v in violations if v.get("check") == check and fragment in v.get("detail", "")
    ]
    assert matched, (
        f"no violation check={check!r} containing {fragment!r}; "
        f"violations: {json.dumps(violations, ensure_ascii=False)}"
    )


@then("violations are empty")
def step_no_violations(context):
    violations = context.last_json.get("violations", [])
    assert violations == [], f"expected no violations, got: {violations}"
