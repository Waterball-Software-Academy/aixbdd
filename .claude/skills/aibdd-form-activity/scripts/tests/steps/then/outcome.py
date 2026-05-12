"""Step: bare decode success/failure assertions for benchmark scenarios.

These do not inspect activity payload or ParseError table — just gate ok-ness.
Detailed shape/message contracts live in steps/then/activity_table.py and
steps/then/parse_error.py.
"""

from __future__ import annotations

from behave import then  # type: ignore[import-not-found]

from _shared.result_guard import require_result


@then("decode 成功")
def step_assert_decode_ok(context):
    require_result(context)
    result = context.parse_result
    assert result.ok is True, f"expected ok=True, got ok={result.ok} errors={result.errors}"


@then("decode 失敗")
def step_assert_decode_fail(context):
    require_result(context)
    result = context.parse_result
    assert result.ok is False, f"expected ok=False, got ok={result.ok}"
