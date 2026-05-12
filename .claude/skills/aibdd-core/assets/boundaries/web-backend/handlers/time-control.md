# Handler: time-control

## Role

`time-control` renders boundary-visible time control for backend behavior.

It belongs to:

- `sentence_part`: `time-control`
- `keywords`: `Given`, `When`

## Trigger Contract

Use this handler when the sentence fixes, advances, or otherwise controls the time observed by backend code.

## Context Contract

Reads `context.clock` or the variant's configured time-control adapter, plus `context.memo` for named time values.

Writes backend-visible test time and optional named instants into `context.memo`.

## Forbidden

- Do not use wall-clock time directly.
- Do not sleep to simulate time passing.
- Do not invent a clock adapter outside test strategy truth.
- Do not mutate persisted domain state except through the declared time-control surface.
