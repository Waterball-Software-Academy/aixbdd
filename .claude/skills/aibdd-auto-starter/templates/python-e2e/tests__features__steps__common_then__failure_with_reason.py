from behave import then


@then('操作失敗，原因為 "{reason}"')
def step_operation_failed_with_reason(context, reason):
    response = getattr(context, "last_response", None)
    assert response is not None, "No response captured"
    payload = response.json()
    status_class = payload.get("__http", {}).get("status_class")
    assert status_class == "failure", (
        f"Expected __http.status_class=failure, got {status_class!r}; body={payload}"
    )
    actual = payload.get("error", {}).get("reason") or payload.get("detail")
    assert actual == reason, f"Expected reason {reason!r}, got {actual!r}"
