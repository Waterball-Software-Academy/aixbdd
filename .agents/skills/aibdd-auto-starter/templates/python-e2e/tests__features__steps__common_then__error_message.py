from behave import then


@then('錯誤訊息應為 "{msg}"')
def step_error_message_should_be(context, msg):
    response = getattr(context, "last_response", None)
    assert response is not None, "No response captured"
    payload = response.json()
    actual = payload.get("message") or payload.get("detail") or payload.get("error", {}).get("message")
    assert actual == msg, f"Expected message {msg!r}, got {actual!r}"
