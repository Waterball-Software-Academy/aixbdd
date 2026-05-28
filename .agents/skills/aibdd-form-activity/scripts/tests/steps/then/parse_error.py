"""Step: assert decode failure produces specific ParseError shape (line + message)."""

from __future__ import annotations

from behave import then  # type: ignore[import-not-found]

from _shared.result_guard import require_result


@then("decode 失敗，ParseError 為:")
def step_assert_parse_error(context):
    require_result(context)
    result = context.parse_result
    assert result.ok is False, f"expected ok=False, got {result.ok}"
    assert context.table is not None, "expected an outline table after Then"
    expected = [(int(row["line"]), row["message"]) for row in context.table]
    actual = [(e.line, e.message) for e in result.errors]
    assert actual == expected, f"errors mismatch\n  expected: {expected}\n  actual:   {actual}"
