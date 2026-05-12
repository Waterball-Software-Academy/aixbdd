from behave import then


@then("操作成功")
def step_then_success(context):
    assert context.last_response is not None, "No response received"
    resp = context.last_response.json()
    status_class = resp.get("__http", {}).get("status_class")
    assert status_class == "success", (
        f"Expected __http.status_class=success, got {status_class!r}; body={resp}"
    )
