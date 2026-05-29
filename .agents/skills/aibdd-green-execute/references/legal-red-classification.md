# Legal Red Classification

Green may start only from Red evidence that is still legal when rerun.

## Legal Red Types

- `value_difference`
- `expected_exception`

The environment must be healthy: runner loads, features are visible, steps are
defined, fixtures load, imports compile, and failure reaches intended behavior.

## Invalid Red For Green

Green stops and routes back to Red when rerun shows:

- all target feature files already green before product-code change
- missing step, skipped Scenario, or invisible runtime feature
- import, compile, fixture, or runner load error
- step body still empty, `pass`, or placeholder pending throw
- red handoff target set mismatch
- failure no longer classified as legal red

Green does not repair Red artifacts. It edits product code only after legal red
is proven again.
