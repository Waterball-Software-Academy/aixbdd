# Truth Ownership

## Owner-Scoped Truth

`/aibdd-plan` owns technical truth created from accepted Discovery behavior:

- Boundary topology and rule dispatch
- Provider operation contracts
- Domain entity, state, and persistence model truth
- Dependency-edge test double policy
- Local/shared DSL physical mappings

## Review Surface

Truth deltas are reviewed by Git diff on the actual truth files. The skill must not create shadow truth copies or delta documents.

## Owned Write Targets

- `specs/<boundary>/boundary-map.yml`
- `specs/<boundary>/contracts/**`（directory owner；operation contract format/serialization belongs to the resolved boundary operation contract specifier）
- `specs/<boundary>/data/**`（directory owner；state file format/serialization belongs to the resolved boundary state specifier）
- `specs/<boundary>/test-strategy.yml`
- `specs/<boundary>/shared/dsl.yml`
- `specs/<boundary>/packages/NN-*/dsl.yml`

## Read-Only Inputs

- `activities/**`
- rule-only `features/**`
- `actors/**` unless the architecture owner explicitly delegates a technical correction
- `specs/architecture/**`
- product code
- runtime tests

## Shadow Truth Definition

Shadow truth is an accepted technical decision stored only in a plan package while downstream skills are expected to read truth layer files. Contract, data, DSL, and test strategy decisions must never be shadow-only.

## State Specifier Delegation

`/aibdd-plan` owns the decision that a boundary needs state/entity truth or operation contract truth, but it does not own every serialization format. Before writing under `data/**` or `contracts/**`, it must resolve the target boundary type profile (`aibdd-core::boundary-profile-contract.md`).

- If the profile declares `state_specifier.skill`, `/aibdd-plan` delegates the state payload to that skill.
- For `web-service`, this means `/aibdd-form-entity-spec` writes DBML (`*.dbml`) under `DATA_DIR`.
- Hand-rendered YAML data models for `web-service` are ownership violations because they bypass the boundary state specifier.
- If the profile declares `operation_contract_specifier.skill`, `/aibdd-plan` delegates the endpoint / request / response payload to that skill.
- For `web-service`, this means `/aibdd-form-api-spec` writes OpenAPI (`*.yml`) under `CONTRACTS_DIR`.
- Hand-rendered ad hoc `operations:` YAML contracts for `web-service` are ownership violations because they bypass the boundary operation contract specifier.
