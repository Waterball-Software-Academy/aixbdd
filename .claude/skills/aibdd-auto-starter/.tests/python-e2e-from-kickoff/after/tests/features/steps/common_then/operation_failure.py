from behave import then


@then("操作失敗")
def step_then_operation_failure(context):
    assert context.last_response is not None, "No response received"
    resp = context.last_response.json()
    status_class = resp.get("__http", {}).get("status_class")
    assert status_class == "failure", (
        f"Expected __http.status_class=failure, got {status_class!r}; body={resp}"
    )
