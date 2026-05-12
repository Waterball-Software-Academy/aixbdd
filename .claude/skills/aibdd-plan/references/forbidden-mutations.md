# Forbidden Mutations

`/aibdd-plan` must not mutate artifacts outside its responsibility.

## Forbidden Plan-Layer Artifacts

The new packing model does not use the old fixed Speckit handoff files as primary outputs:

- legacy quickstart handoff documents
- plan-package data model shadow files
- plan-package contract shadow directories
- decision logs
- handoff summaries as truth
- truth delta folders

## Forbidden Truth Mutations

- Discovery-owned `activities/`
- Discovery-owned rule-only `features/`
- Spec-by-Example scenarios or Examples
- actor catalog changes without explicit architecture-owner delegation
- architecture truth not scoped to this plan

## Forbidden Runtime Mutations

- product code
- runtime tests
- step definitions
- fixtures
- task queues
- RED/GREEN/REFACTOR task evidence

## Forbidden Behavior

- Re-planning Discovery behavior.
- Weakening quality gates after failure.
- Creating DSL entries with summary-only L4.
- Inventing same-boundary mocks.
- Requiring `/aibdd-test-plan` for completion.
