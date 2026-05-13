# Handler: ui-action

## Role

`ui-action` renders user interaction with the rendered UI through a Playwright locator.

It belongs to:

- `sentence_part`: `ui-action`
- `keywords`: `Given`, `When`

## Trigger Contract

Use this handler when the sentence drives a user-visible interaction — click, fill, select, upload, keyboard press, drag, or programmatic navigation history. `L4.callable_via` resolves to exactly one UI driver verb. Given usage is prerequisite multi-step setup; When usage is the scenario's target operation.

## Context Contract

Reads `page`, the locator derived from `L4.source_refs.component` Story export args, and the route-scoped state established by an earlier `route-given`.

Writes outgoing requests to the variant's mock layer (when the interaction triggers a fetch) and DOM state observable to subsequent Then steps. This handler MUST NOT own assertion bindings.

## Storybook Binding (I4)

`L4.source_refs.component` MUST point to a specific Story export (e.g., `Button.stories.ts::Primary`). Locator derivation rule:

1. Parse Story export `args` to determine accessible name / role / test-id.
2. Step definition uses `page.getByRole(role, { name })` matching that accessible name.
3. Same component in different states (Primary / Loading / Disabled) binds to different Story exports.

Stories without explicit accessible-name args MUST NOT be bind targets; this is a missing-truth stop, not a legal red.

When the Story uses a design-system library component, the AI MUST verify the resulting role and accessible-name match library docs via `${PROJECT_SLUG}-sb-mcp` MCP tools BEFORE writing the locator.

## Playwright Surface

Allowed verbs (one per step body):

| Verb | Playwright API |
|---|---|
| click | `locator.click()` |
| fill | `locator.fill(value)` |
| select | `locator.selectOption(value)` |
| upload | `locator.setInputFiles(path)` |
| press | `page.keyboard.press(key)` |
| drag | `locator.dragTo(target)` |
| navigate-history | `page.goBack()` / `page.goForward()` / `page.reload()` |

Locator query MUST come from the bound Story export — `getByRole` / `getByLabel` / `getByTestId` / explicit `name=` — never raw CSS or class selectors.

## Forbidden

- Do not use raw CSS class selectors or nth-child positional selectors when role / label / test-id is available.
- Do not assert anything in this handler (no `expect(...)` in the step body).
- Do not import component files directly from `src/components/**` — interact only through the rendered DOM.
- Do not invent action verbs outside the allowed set above.
- Do not bind to a component file path alone — Story export is mandatory.
- Do not infer endpoint, field name, or id outside L4 bindings.
- Do not chain two driver verbs in one step body — one step renders one interaction.
