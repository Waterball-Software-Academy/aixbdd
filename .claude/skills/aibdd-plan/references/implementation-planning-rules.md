# Implementation Planning Rules

## Plan Package Scope

Implementation planning artifacts are session artifacts. They live in the plan package and do not become boundary truth unless separately promoted by an architecture owner.

## Sequence Diagrams

Each major path gets a sequence diagram:

- happy path: `implementation/sequences/<slug>.happy.sequence.mmd`
- alternative path: `implementation/sequences/<slug>.alt.sequence.mmd`
- error path: `implementation/sequences/<slug>.err.sequence.mmd`

（Sequence 檔名副檔名 SSOT：`aibdd-core::diagram-file-naming.md`。）

Sequence diagrams identify actor, boundary entry operation, internal collaborator, provider contract calls, state changes, and response verifier candidates.

## Internal Structure

`implementation/internal-structure.class.mmd` is the structural union of all sequence diagrams. It exists so `/aibdd-tasks` can point GREEN tasks at concrete classes/modules/operations without re-planning.

## Traceability

Every implementation target should trace back to at least one activity path, rule-only feature rule, provider contract, or boundary-map dispatch default/override.

## Forbidden Content

Implementation planning must not include product code patches, test step definitions, or task queue status.
