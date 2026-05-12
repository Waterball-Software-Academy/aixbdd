# Handler: success-failure

## Role

`success-failure` renders operation result verification for status, error, or exception outcome.

It belongs to:

- `sentence_part`: `success-failure`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies only whether the previously invoked operation succeeded or failed.

## Context Contract

Reads `context.last_response` and optionally `context.last_error`.

Writes no behavior state.

## Forbidden

- Do not call API again.
- Do not inspect response payload fields unrelated to success or failure.
- Do not verify persisted state.
- Do not convert this handler into readmodel verification.
