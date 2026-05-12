# Handler: aggregate-given

## Role

`aggregate-given` renders persisted backend state setup.

It belongs to:

- `sentence_part`: `aggregate-given`
- `keywords`: `Given`, `Background`

## Trigger Contract

Use this handler when the sentence describes boundary-owned persisted state that must exist before the target operation.

## Context Contract

Reads `context.db_session`, `context.repos`, and `context.ids`.

Writes persisted test state and `context.ids` for natural keys required by later operation or verification steps.

## Forbidden

- Do not call backend API.
- Do not invent entity fields outside data truth.
- Do not use dict-only objects when the variant requires ORM/entity instances.
- Do not omit required state identity fields.
