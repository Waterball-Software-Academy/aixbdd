# Technical Truth Rules

## Boundary Map

`boundary-map.yml` records boundary-level technical routing decisions that cannot be safely inferred from package structure:

- topology of boundary-owned modules and provider dependencies
- default dispatch inference contract from package structure, feature files, activity anchors, contract operation ids, and package DSL
- explicit dispatch overrides only when the default inference is wrong
- dependency edges from consumer to provider
- persistence ownership decisions
- testability anchor references used by DSL entries

Do not enumerate every atomic rule in `boundary-map.yml`. Per-rule ownership is implied by `packages/NN-*/features/*.feature`, package-local `dsl.yml`, and `contracts/**/*.yml#operations.*`. A rule gets an explicit override only for cross-boundary ownership, shared operations, non-standard modules, or a planning gap.

## Provider Contracts

Provider contracts describe operation surfaces. They may cover internal provider boundaries or third-party providers such as payment platforms, AWS services, Redis, mail providers, or webhook sources.

Contract content is truth. It belongs under `contracts/` and should include stable operation ids, request fields, response fields, errors, side effects, and source refs. The concrete contract format is selected by the target boundary profile.

For `web-service`, the boundary profile declares:

- operation contract format: `openapi`
- operation contract specifier skill: `/aibdd-form-api-spec`

Therefore `/aibdd-plan` must produce the endpoint / request / response reasoning payload and delegate serialization to `/aibdd-form-api-spec`. It must not hand-render ad hoc `operations:` YAML contracts for `web-service`.

## Data and State Truth

Data truth describes boundary-owned entities, persistence shape, state transitions, and the state subset that acceptance tests are allowed to verify. It belongs under `data/`, but the concrete file format is selected by the target boundary profile.

For `web-service`, the boundary profile declares:

- state format: `dbml`
- state specifier skill: `/aibdd-form-entity-spec`

Therefore `/aibdd-plan` must produce the entity/state reasoning payload and delegate serialization to `/aibdd-form-entity-spec`. It must not hand-render YAML state models for `web-service`.

## Test Strategy

`test-strategy.yml` records boundary-level testing decisions and dependency-edge test double policy.

Every mockable consumer-provider edge has a strategy entry. Same-boundary internal collaborators are not provider edges and must not be mocked through DSL.

## External Boundary Surface

External dependency planning includes:

- provider contract truth
- test double policy
- stub lifecycle and reset behavior
- payload and response source refs
- failure-mode coverage when the behavior depends on provider failure
