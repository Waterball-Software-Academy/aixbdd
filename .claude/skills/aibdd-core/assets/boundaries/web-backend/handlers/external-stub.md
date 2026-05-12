# Handler: external-stub

## Role

`external-stub` renders setup for backend-visible external resources.

It belongs to:

- `sentence_part`: `external-stub`
- `keywords`: `Given`

## Trigger Contract

Use this handler when the sentence controls an external resource that backend code observes during the scenario.

External resources can include APIs, queues, caches, file systems, email senders, or another backend-facing dependency when test strategy truth declares a controllable stub surface.

## Context Contract

Reads `context.external_stubs` or the variant's configured registry, and `context.memo` for fixture values produced by earlier steps.

Writes stubbed external resource behavior and optional captured traces into `context.memo`.

## Forbidden

- Do not make real external network calls.
- Do not invent provider fields outside provider contract or test strategy truth.
- Do not hide missing provider truth behind permissive wildcard stubs.
- Do not use this handler for backend-owned persisted state; use `aggregate-given` instead.
