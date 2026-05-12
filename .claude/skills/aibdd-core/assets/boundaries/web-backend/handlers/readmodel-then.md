# Handler: readmodel-then

## Role

`readmodel-then` renders response payload verification from the previously captured backend response.

It belongs to:

- `sentence_part`: `readmodel-then`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies data returned by the backend API response, including read model projections represented in the response payload.

## Context Contract

Reads `context.last_response`.

Writes no behavior state.

## Forbidden

- Do not call API again.
- Do not query repository or database.
- Do not infer response field names outside the contract.
- Do not verify operation success unless the DSL entry explicitly binds that assertion.
