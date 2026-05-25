# Artifact Partitioning — New Packing Model

> LOAD target: any AIBDD skill that reads or writes planning/truth artifacts.
> Rule: copy = error; reference = correct. Every fact has exactly one owner.

## Artifact Families

| Family | Path pattern | Owner | Purpose |
|---|---|---|---|
| Project config | `.aibdd/arguments.yml`, `specs/architecture/boundary.yml`, `specs/shared/dsl.yml` (preset seed) | `/aibdd-kickoff` | boundary-aware path, topology seed, and boundary shared DSL baseline |
| Discovery truth | `specs/packages/NN-*/activities/`, `features/`, `specs/plans/NNN-*/reports/impact-matrix.yml`, `specs/plans/NNN-*/reports/discovery-sourcing.md`, `specs/plans/NNN-*/spec.md` summary | `/aibdd-discovery` plus form skills | accepted external behavior and atomic rules |
| Boundary technical truth | `specs/boundary-map.yml`, `specs/contracts/`, `specs/data/`, `specs/test-strategy.yml` | `/aibdd-plan` + boundary state specifier skill | owner-scoped implementation truth |
| DSL truth | `specs/contracts/*.dsl.yml`, `specs/data/*.dsl.yml`, `specs/shared/dsl.yml` | `/aibdd-plan` (part-derived); kickoff seeds `specs/shared/dsl.yml` baseline | flat entry mapping truth for red-usable steps |
| Plan package work records | `specs/plans/NNN-*/plan.md`, `research.md`, `implementation/sequences/*.sequence.mmd`, `implementation/internal-structure.class.mmd` | `/aibdd-plan` | session-specific reasoning and implementation plan |

## Ownership Rules

### Boundary Truth

`/aibdd-plan` writes durable technical truth only in boundary-owned locations:

- `boundary-map.yml`
- `contracts/`（directory owned by `/aibdd-plan`; concrete operation contract file format is delegated by boundary profile, e.g. OpenAPI via `/aibdd-form-api-spec`）
- `data/`（directory owned by `/aibdd-plan`; concrete state file format is delegated by boundary profile, e.g. DBML via `/aibdd-form-entity-spec`）
- `test-strategy.yml`
- part-derived `contracts/*.dsl.yml` and `data/*.dsl.yml`
- boundary shared `dsl.yml` extensions beyond the kickoff preset seed

Plan-package files may reference these facts but must not duplicate them as the only source of truth.

### Discovery Truth

Discovery artifacts stay behavioral:

- activities model external flows and accepted paths
- feature files produced by Discovery are rule-only scaffolds unless a downstream examples skill owns Examples
- Discovery must not create contracts, data models, test strategy, DSL L4 mapping, or implementation classes

### DSL Truth

DSL entries are truth, not notes. Each flat entry must carry enough physical
mapping for RED:

- `target_part_path` to contract/data/code truth
- `handler` selecting reusable preset handler docs
- `param_bindings` for every `{key}` in `format`
- `datatable_bindings` for scenario-visible business inputs kept out of `format`

### Plan Package

Plan package artifacts are records and coordination surfaces:

- `plan.md`: chosen technical solution, deltas, risks, downstream handoff
- `research.md`: trade-offs and rejected alternatives
- `implementation/sequences/*.sequence.mmd`: external/internal call sequences（檔名規約見 `diagram-file-naming.md`）
- `implementation/internal-structure.class.mmd`: structure implied by sequences

They must not become shadow truth for contracts, data, test strategy, or DSL mappings.

## Deprecated Artifacts

The new packing model does not use `testability-plan.md` as a standalone product artifact. Physical testability is absorbed into `/aibdd-plan` and stored in boundary truth plus part-derived DSL mappings.

Legacy Speckit files such as `bdd-plan.md`, root-level `data-model.md`, or root-level `contracts/` must not be introduced by new AIBDD skills.

## Gate Criteria

`ARTIFACT_PARTITIONING` fails when any of the following is true:

- a plan-package file contains the only copy of a provider contract, state model, or test strategy
- `/aibdd-plan` hand-renders a state model in a format that the boundary profile says belongs to a state specifier skill
- `/aibdd-plan` hand-renders an operation contract in a format that the boundary profile says belongs to an operation contract specifier skill
- a DSL entry uses prose mapping instead of typed `target_part_path` and bindings
- Discovery writes technical truth
- `/aibdd-plan` writes behavior rules, Examples, tasks, product code, step definitions, or runtime fixtures
- a deprecated `testability-plan.md` is created by the new flow

## Cross References

- [`diagram-file-naming.md`](diagram-file-naming.md)
- [`physical-first-principle.md`](physical-first-principle.md)
- [`spec-package-paths.md`](spec-package-paths.md)
