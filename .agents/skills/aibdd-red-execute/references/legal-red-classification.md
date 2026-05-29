# Legal Red Classification

Legal red means the test environment is healthy and the remaining failure proves
a behavioral gap.

## Legal Red Types

- `value_difference`: the runner reached the intended assertion and observed an
  actual value different from the expected value.
- `expected_exception`: the scenario expects an exception or failure outcome, but
  the product did not produce it.

## False Red Types

These failures are not legal red:

- compile error, syntax error, import error, or runner load error
- missing step, skipped Scenario, or invisible runtime feature
- fixture/helper load failure outside the behavior under test
- step definition body containing `pass`, empty body, placeholder throw, or
  `RED-PENDING`
- DSL entry missing, ambiguous, or invented during Red
- datatable shape mismatch against `datatable_bindings`
- dynamic ID alias that cannot resolve to declared Scenario or fixture truth
- preset handler that cannot resolve to core boundary assets
- handler forbidden surface in generated step-def body
- direct import of production internals instead of using the DSL surface
- renderer-inferred endpoint, field, id, or default value not present in truth
