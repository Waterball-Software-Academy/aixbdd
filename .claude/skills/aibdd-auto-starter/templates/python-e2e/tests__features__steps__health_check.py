"""Starter smoke steps for HealthCheck.feature — not product BDD."""

from behave import then, when


@when("I request the health endpoint")
def step_request_health_endpoint(context):
    context.last_response = context.api_client.get("/health")


@then("the health check response is OK")
def step_health_check_response_ok(context):
    assert context.last_response is not None, "No response received"
    assert context.last_response.status_code == 200, (
        f"Expected HTTP 200, got {context.last_response.status_code}"
    )
    assert context.last_response.json() == {"status": "ok"}, (
        f"Expected {{'status': 'ok'}}, got {context.last_response.json()}"
    )
