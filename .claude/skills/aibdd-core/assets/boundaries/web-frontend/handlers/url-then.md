# Handler: url-then

## Role

`url-then` renders verification of URL state — pathname, query string parameters, or hash fragment — after the target operation.

It belongs to:

- `sentence_part`: `url-then`
- `keywords`: `Then`

## Trigger Contract

Use this handler when URL is the load-bearing observable for the scenario outcome (post-submit navigation to a detail page, shareable filter state encoded in query parameters, hash-routed sub-view). When the same outcome is observable through visible UI elements, prefer `ui-readmodel-then`. URL aspect (`pathname | searchParams.{key} | hash`) comes from `L4.assertion_bindings`.

## Context Contract

Reads `page.url()` (or variant equivalent) and `L4.source_refs.route` for the expected path shape, including any dynamic segment patterns declared in the route map.

Writes no behavior state.

## Playwright Surface

| URL aspect | Playwright API |
|---|---|
| pathname (literal or regex) | `await expect(page).toHaveURL(re)` |
| query param value | `expect(new URL(page.url()).searchParams.get(k)).toBe(value)` |
| hash fragment | `expect(new URL(page.url()).hash).toBe('#frag')` |

Pathname assertions allow segment-parameterized matching via regex derived from the route map dynamic segment declarations.

## Forbidden

- Do not assert path literals outside the project route map.
- Do not hard-code dynamic segment values when the route map declares parameterized segments — match via regex derived from the route map.
- Do not navigate the browser in a Then step (no `page.goto`).
- Do not use this handler to verify route-correlated UI content; that is `ui-readmodel-then`.
- Do not bypass `page.url()` by reading `window.location` through `page.evaluate` when the variant accessor is available.
- Do not concatenate `baseURL` manually in the expected URL; let Playwright resolve it through `toHaveURL`.
