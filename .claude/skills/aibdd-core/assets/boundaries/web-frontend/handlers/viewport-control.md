# Handler: viewport-control

## Role

`viewport-control` renders browser viewport sizing or named device profile control.

It belongs to:

- `sentence_part`: `viewport-control`
- `keywords`: `Given`, `When`

## Trigger Contract

Use this handler when the sentence sets viewport dimensions or selects a named device profile defined by the project test strategy. Given usage is prerequisite setup; When usage is a deliberate mid-scenario change to verify responsive behavior.

## Context Contract

Reads `page` (for runtime resize), `test` (for `test.use({ viewport })` when scoped at file level), and `test-strategy.yml#viewport_profiles` for named profiles.

Writes viewport state on `page`. Does not mutate scenario memo or mock store.

## Playwright Surface

- Width × height: `await page.setViewportSize({ width, height })`.
- Named device profile: `test.use({ viewport: profileResolvedByVariant })` at file scope, or `page.setViewportSize(...)` at step scope.

The variant decides which surface is used based on whether the binding is width/height or a named profile id.

## Forbidden

- Do not invent named device profiles outside `test-strategy.yml#viewport_profiles`.
- Do not hard-code viewport dimensions when the sentence parameterizes a named profile.
- Do not use this handler to drive layout-conditional component selection — selection still flows through Story export bindings.
- Do not couple viewport changes with implicit reload; reloads require an explicit `ui-action` navigation step.
- Do not mutate `page.viewportSize()` through `page.evaluate` or `window.resizeTo`.
