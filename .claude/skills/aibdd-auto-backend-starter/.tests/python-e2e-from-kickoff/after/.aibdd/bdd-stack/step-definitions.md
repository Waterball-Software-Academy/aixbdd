# Step Definitions Runtime

## primary step definition root

`tests/features/steps`

## step definition glob

`tests/features/steps/**/*.py`

## shared step glob（若有）

`tests/features/steps/shared/**/*.py`

## handler layout

Generated feature-package steps should be grouped under:

```text
tests/features/steps/<function-package-or-domain>/
  aggregate_given/
  http_operation/
  success_failure/
  readmodel_then/
  aggregate_then/
  time_control/
  external_stub/
```

## matcher rules

- Use Behave decorators from `behave`: `@given`, `@when`, `@then`.
- The first argument is always `context`.
- Matchers are generated from exact DSL `L1` sentence patterns.
- Shared common Then steps may live outside handler folders only when they own the exact matcher.
- Shared common Then steps should rely on a reusable transport/result probe helper rather than each file inventing its own raw response-shape convention.

## forbidden

- Do not import production service internals in E2E step definitions.
- Do not create step files outside the configured globs.
- Do not generate raw locator or UI-oriented steps for this backend stack.
