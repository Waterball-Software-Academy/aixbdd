# Handler: aggregate-then

## Role

`aggregate-then` renders persisted backend state verification.

It belongs to:

- `sentence_part`: `aggregate-then`
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
