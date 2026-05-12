# Artifact Partitioning — New Packing Model

> LOAD target: any AIBDD skill that reads or writes planning/truth artifacts.
> Rule: copy = error; reference = correct. Every fact has exactly one owner.

## Artifact Families

| Family | Path pattern | Owner | Purpose |
|---|---|---|---|
| Project config | `.aibdd/arguments.yml`, `specs/architecture/boundary.yml` | `/aibdd-kickoff` | boundary-aware path and topology seed |
| Discovery truth | `specs/<boundary>/packages/NN-*/activities/`, `features/`, `reports/discovery-sourcing.md`, `spec.md` summary | `/aibdd-discovery` plus form skills | accepted external behavior and atomic rules |
| Boundary technical truth | `specs/<boundary>/boundary-map.yml`, `contracts/`, `data/`, `test-strategy.yml` | `/aibdd-plan` + boundary state specifier skill | owner-scoped implementation truth |
| DSL truth | `specs/<boundary>/packages/NN-*/dsl.yml`, `specs/<boundary>/shared/dsl.yml` | `/aibdd-plan` | L1-L4 red-usable mapping truth |
| Plan package work records | `plan.md`, `research.md`, `implementation/sequences/*.sequence.mmd`, `implementation/internal-structure.class.mmd` | `/aibdd-plan` | session-specific reasoning and implementation plan |

## Ownership Rules

### Boundary Truth

`/aibdd-plan` writes durable technical truth only in boundary-owned locations:

- `boundary-map.yml`
- `contracts/`（directory owned by `/aibdd-plan`; concrete operation contract file format is delegated by boundary profile, e.g. OpenAPI via `/aibdd-form-api-spec`）
- `data/`（directory owned by `/aibdd-plan`; concrete state file format is delegated by boundary profile, e.g. DBML via `/aibdd-form-entity-spec`）
- `test-strategy.yml`
- local package `dsl.yml`
- boundary shared `dsl.yml`

Plan-package files may reference these facts but must not duplicate them as the only source of truth.

### Discovery Truth

Discovery artifacts stay behavioral:

- activities model external flows and accepted paths
- feature files produced by Discovery are rule-only scaffolds unless a downstream examples skill owns Examples
- Discovery must not create contracts, data models, test strategy, DSL L4 mapping, or implementation classes

### DSL Truth

DSL entries are truth, not notes. Each entry must carry enough physical mapping for RED:

- source refs to contract/data/boundary/test-strategy truth
- `surface_kind` and `callable_via`
- parameter bindings for every L1 placeholder
- assertion bindings for expected response/state values
- preset handler reference when using reusable backend patterns

### Plan Package

Plan package artifacts are records and coordination surfaces:

- `plan.md`: chosen technical solution, deltas, risks, downstream handoff
- `research.md`: trade-offs and rejected alternatives
- `implementation/sequences/*.sequence.mmd`: external/internal call sequences（檔名規約見 `diagram-file-naming.md`）
- `implementation/internal-structure.class.mmd`: structure implied by sequences

They must not become shadow truth for contracts, data, test strategy, or DSL mappings.

## Deprecated Artifacts

The new packing model does not use `testability-plan.md` as a standalone product artifact. Physical testability is absorbed into `/aibdd-plan` and stored in boundary truth plus DSL L4 mappings.

Legacy Speckit files such as `bdd-plan.md`, root-level `data-model.md`, or root-level `contracts/` must not be introduced by new AIBDD skills.

## Gate Criteria

`ARTIFACT_PARTITIONING` fails when any of the following is true:

- a plan-package file contains the only copy of a provider contract, state model, or test strategy
- `/aibdd-plan` hand-renders a state model in a format that the boundary profile says belongs to a state specifier skill
- `/aibdd-plan` hand-renders an operation contract in a format that the boundary profile says belongs to an operation contract specifier skill
- a DSL entry uses prose L4 mapping instead of typed source refs and bindings
- Discovery writes technical truth
- `/aibdd-plan` writes behavior rules, Examples, tasks, product code, step definitions, or runtime fixtures
- a deprecated `testability-plan.md` is created by the new flow

## Cross References

- [`diagram-file-naming.md`](diagram-file-naming.md)
- [`physical-first-principle.md`](physical-first-principle.md)
- [`spec-package-paths.md`](spec-package-paths.md)
