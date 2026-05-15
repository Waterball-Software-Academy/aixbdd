# Handler: time-control

## Role

`time-control` renders browser-visible test-clock control for time-dependent UI behavior.

It belongs to:

- `sentence_part`: `time-control`
- `keywords`: `Given`, `When`

## Trigger Contract

Use this handler when the sentence fixes, advances, or otherwise controls the time the browser observes. The time-control surface is provided by the variant — for `nextjs-playwright` this is `page.clock` (Playwright ≥ 1.45).

## Context Contract

Reads `page.clock` (or variant-equivalent test-clock adapter), scenario memo for named instants, and the `test-strategy.yml` entry that declares how browser-visible time is controlled.

Writes browser-visible clock state and optional named instants into scenario memo.

## Playwright Surface

- Install fake clock at a fixed instant: `await page.clock.install({ time })`.
- Advance time: `await page.clock.fastForward(ms)` or `await page.clock.runFor(ms)`.
- Pin to a specific moment without freezing: `await page.clock.setFixedTime(date)`.

Choice of surface comes from `L4.callable_via`; step definitions MUST NOT mix multiple `page.clock` modes within one step.

## Forbidden

- Do not use wall-clock time directly in assertions or step bodies.
- Do not `await page.waitForTimeout(...)` or `setTimeout` to simulate time passing.
- Do not invent a clock adapter outside test-strategy truth.
- Do not control the dev-server-side time; this handler only controls browser-visible time.
- Do not mix `page.clock.fastForward` with real waits in the same step.
- Do not skip `page.clock.install` before `fastForward` / `runFor` — those calls require an installed clock.
