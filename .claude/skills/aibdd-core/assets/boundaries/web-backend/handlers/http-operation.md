# Handler: http-operation

## Role

`http-operation` renders backend API operation invocation steps.

It belongs to:

- `sentence_part`: `http-operation`
- `keywords`: `Given`, `When`

## Trigger Contract

Use this handler when the sentence invokes a backend operation through the HTTP boundary. The operation contract determines HTTP method, path template, request inputs, and response verifier shape.

## Context Contract

Reads `context.api_client`, `context.jwt_helper`, and `context.ids`.

Writes `context.last_response` and optional request trace values into `context.memo`.

## Forbidden

- Do not assert response status or payload.
- Do not invent endpoint path or HTTP method.
- Do not rename request fields outside the operation contract.
- Do not hard-code ids when `context.ids` or bindings provide them.
- Do not call repository or service internals for E2E variant.
