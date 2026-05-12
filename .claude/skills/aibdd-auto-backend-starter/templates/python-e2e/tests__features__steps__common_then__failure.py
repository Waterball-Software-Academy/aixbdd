from behave import then


@then('操作失敗，violation_type 為 "{violation_type}"')
def step_then_failure_with_violation(context, violation_type):
    assert context.last_response is not None, "No response received"
    resp = context.last_response.json()
    status_class = resp.get("__http", {}).get("status_class")
    assert status_class == "failure", (
        f"Expected __http.status_class=failure, got {status_class!r}; body={resp}"
    )
    actual_type = resp.get("error", {}).get("violation_type")
    assert actual_type == violation_type, (
        f"Expected violation_type='{violation_type}', got '{actual_type}'"
    )
