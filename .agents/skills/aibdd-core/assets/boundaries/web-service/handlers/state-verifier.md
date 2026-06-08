# Handler: state-verifier

## Role

`state-verifier` renders persisted backend state verification of a single
entity's own column values.

For relationship (foreign-key) verification between two entities, use
[`state-relationship-verifier`](state-relationship-verifier.md) instead.

It belongs to:

- `part`: `state-verifier`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies backend-owned persisted state after an operation.

## Context Contract

Reads `context.db_session`, `context.repos`, and `context.ids`.

Writes no behavior state.

## Forbidden

- Do not call backend API.
- Do not read `context.last_response` as the assertion source.
- Do not mutate persisted state.
- Do not infer entity fields outside data truth.
