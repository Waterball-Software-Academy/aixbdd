# Planning — Reconcile Relevance

## Owned Truth

`/aibdd-plan` owns the technical truth and planning artifacts derived from accepted Discovery truth:

- `boundary-map.yml`
- operation contracts under `contracts/`
- state / entity truth under `data/`
- `test-strategy.yml`
- local / shared `dsl.yml`
- `plan.md`, `research.md`, and implementation diagrams

If a trigger changes those truths while the accepted behavior rules remain intact, Plan is the
earliest valid reconcile start.

## Classify As Plan

Choose `aibdd-plan` as earliest when the trigger implies any of the following:

- API request / response schema is missing, wrong, or newly required
- data model, table ownership, persistence fields, or entity relationships must change
- dependency edges, provider boundaries, or test-double policy must change
- DSL bindings, presets, handlers, default bindings, or aggregate-given builders must change
- implementation sequence diagrams or internal structure planning must change for the same accepted behavior
- `plan.md` needs a new technical narrative because the plan package's accepted behavior stayed the same but the technical realization changed

## Classify As Not Plan

Do **not** choose Plan when the trigger is only about:

- user-visible flow, actor legality, or atomic rule wording
- feature-rule partition changes
- example rows, Scenario Outline examples, coverage rows, or clause phrasing for an already accepted rule

Those belong to `aibdd-discovery` or `aibdd-spec-by-example-analyze`.

## Mixed Trigger Rule

If the trigger needs both a Discovery change and a Plan change, Discovery wins because Plan may only
plan from already accepted behavior truth.

If the trigger needs both a Plan change and an example refactor caused by that plan change, Plan wins
because Spec-by-Example only consumes Plan truth.

## Fallback Rule

If the trigger says \"something is wrong in the API / schema / DSL / data model\" without asking to
change behavior truth, classify it as Plan.
