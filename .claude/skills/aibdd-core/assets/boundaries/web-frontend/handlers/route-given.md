# Handler: route-given

## Role

`route-given` renders browser navigation to a target application route as a scenario precondition.

It belongs to:

- `sentence_part`: `route-given`
- `keywords`: `Given`, `Background`

## Trigger Contract

Use this handler when the sentence places the browser on a specific application route before the scenario's target operation. Route shape (segments, query string, hash) comes from `L4.source_refs.route` resolved against the project route map. Auth-required routes MUST declare an explicit precondition step — this handler does not silently inject authentication.

## Context Contract

Reads `page`, `baseURL` (from `playwright.config.ts`), the route map entry in `L4.source_refs.route`, and any earlier scenario memo for route segment / query values.

Writes browser location state. Does not mutate scenario memo, mock store, or fixture closure.

## Playwright Surface

Primary call: `await page.goto(url)`. The `url` value is resolved by the variant's route-navigator from `L4.callable_via` plus parameter bindings; `baseURL` resolution is delegated to Playwright config — step bodies MUST NOT concatenate `baseURL` manually.

## Forbidden

- Do not invent route literals outside the project route map.
- Do not concatenate raw URL strings — resolve through `L4.callable_via` and Playwright `baseURL`.
- Do not silently inject auth state; auth-required routes require an explicit precondition step.
- Do not assert on response status, page content, or URL after navigation (those belong to `ui-readmodel-then` / `url-then`).
- Do not use this handler to assert URL state.
- Do not call `page.goto` again inside an unrelated Then step to "re-land" the page.
