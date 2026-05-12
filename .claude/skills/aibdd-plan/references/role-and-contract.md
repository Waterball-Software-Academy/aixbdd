# `/aibdd-plan` Role and Contract

## Role

`/aibdd-plan` is the technical planning orchestrator for one accepted Discovery scope. It converts behavior truth into owner-scoped technical truth, implementation planning artifacts, and red-usable DSL mappings.

## Required Inputs

- `.aibdd/arguments.yml`
- Current plan package with `spec.md` and `reports/discovery-sourcing.md`
- Target boundary truth root
- Target function package with `activities/` and rule-only `features/`
- Existing `boundary-map.yml`, `contracts/`, `data/`, `shared/dsl.yml`, package `dsl.yml`, and `test-strategy.yml`
- Target boundary type profile (`aibdd-core::boundary-profile-contract.md`) so contract/state formats are delegated to the correct specifier skill
- Current code skeleton index

## Outputs

Truth outputs:

- `specs/<boundary>/boundary-map.yml`
- `specs/<boundary>/contracts/`（operation contract files written by the boundary operation contract specifier, e.g. `/aibdd-form-api-spec` for `web-service`）
- `specs/<boundary>/data/`（state files written by the boundary state specifier, e.g. `/aibdd-form-entity-spec` for `web-service`）
- `specs/<boundary>/test-strategy.yml`
- `specs/<boundary>/shared/dsl.yml`
- `specs/<boundary>/packages/NN-*/dsl.yml`

Plan-package outputs:

- `specs/<NNN-plan>/plan.md`
- `plan.md` MUST include an `Impacted Feature Files` section for downstream phase scope
- when called by `/aibdd-reconcile`, `plan.md` SHOULD also include a `Reconciliation Context` section with trigger / earliest / cascade / archive pointer
- `specs/<NNN-plan>/research.md`
- `specs/<NNN-plan>/implementation/sequences/*.sequence.mmd`
- `specs/<NNN-plan>/implementation/internal-structure.class.mmd`
- `specs/<NNN-plan>/reports/aibdd-plan-quality.md`

## Non-Goals

- It does not draft Discovery behavior truth.
- It does not add Spec-by-Example scenarios or Examples.
- It does not generate RED/GREEN/REFACTOR tasks.
- It does not write product code, step definitions, or fixtures.
- It does not invoke or depend on `/aibdd-test-plan`.

## Completion Contract

The skill is complete when technical truth, implementation planning artifacts, and DSL truth form a traceable graph from Discovery rules to downstream `/aibdd-spec-by-example-analyze` inputs, and `plan.md` exposes a stable impacted-feature list that downstream optional planners can consume.
