# Variant: python-e2e

## Role

`python-e2e` renders web-backend preset handlers into Python Behave step definitions for API-level end-to-end tests.

This variant only defines rendering mechanics. It does not classify sentence parts and does not select handlers.

## Runtime Contract

- Language: Python 3.11+
- BDD framework: Behave
- HTTP client: FastAPI `TestClient`
- Persistence access: SQLAlchemy session and repositories
- App access: imported FastAPI `app`
- Context object: Behave `context`
- Time control: project-owned runtime instruction configured clock adapter
- External resources: project-owned runtime instruction configured stub registry

## Required Context Fields

Initialized before each test case:

```python
context.last_error = None
context.last_response = None
context.ids = {}
context.memo = {}
context.db_session = session_factory()
context.api_client = TestClient(app)
context.jwt_helper = JwtHelper()
context.repos = SimpleNamespace()
context.clock = TestClock()
context.external_stubs = ExternalStubRegistry()
```

## Step File Layout

Directories under `steps/<function-package-or-domain>/` map one-to-one to handlers in [`handler-routing.yml`](../handler-routing.yml) (hyphen in handler name -> snake_case folder).

```text
${PY_TEST_FEATURES_DIR}/
  environment.py
  helpers/
  steps/
    <function-package-or-domain>/
      aggregate_given/
      http_operation/
      success_failure/
      readmodel_then/
      aggregate_then/
      time_control/
      external_stub/
```

One generated step pattern should map to one `.py` file unless an existing shared common step already owns the exact matcher. Shared matchers outside the seven preset handlers are project-specific and are not part of this preset SSOT.

## Behave Matcher Contract

- Use `@given`, `@when`, or `@then` according to the Gherkin keyword.
- First function argument is always `context`.
- Additional arguments are derived from `L1` placeholders.
- Integer placeholders use `:d`.
- Float placeholders use `:f`.
- Quoted string placeholders remain quoted in the matcher.

## Forbidden

- Do not infer endpoint path outside operation contracts.
- Do not infer request or response field names outside L4 bindings.
- Do not call application service internals from E2E steps.
- Do not make a second HTTP call in Then handlers.
- Do not assert response payload in `http-operation`.
- Do not use repository access in `readmodel-then`.
- Do not use HTTP access in `aggregate-given` or `aggregate-then`.
- Do not sleep or read wall-clock time in `time-control`.
- Do not make real external calls in `external-stub`.

## Legal Red Expectation

A generated step definition is a valid red step only when:

- the matcher is generated from exact `L1`;
- all request/assertion values come from L4 bindings;
- the preset tuple resolves to this variant;
- the code can run far enough to expose missing product implementation or behavioral mismatch.

Missing truth is not a legal red; it must stop before rendering.
