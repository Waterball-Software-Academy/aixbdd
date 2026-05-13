# Handler: ui-readmodel-then

## Role

`ui-readmodel-then` renders verification of rendered UI values, labels, roles, attributes, or counts observable on the page DOM.

It belongs to:

- `sentence_part`: `ui-readmodel-then`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies a value, label, role, attribute, or count rendered on the page after the target operation. Includes scalar text, list / table collection items, and computed counts. Collection assertions MUST resolve through role semantics (`role=row`, `role=listitem`), not raw nth-child positional selectors.

## Context Contract

Reads `page`, the locator derived from `L4.source_refs.component` Story export, and the already-rendered DOM.

Writes no behavior state.

## Storybook Binding (I4)

`L4.source_refs.component` MUST point to the specific Story export owning the target element. For collection assertions, the bound Story export is the list / table / grid component story whose `args` define the row / item role and accessible name. Same component × different states → different Story exports.

## Playwright Surface

| Assertion | Playwright API |
|---|---|
| scalar text | `await expect(locator).toHaveText(value)` / `.toContainText(value)` |
| visibility | `await expect(locator).toBeVisible()` / `.toBeHidden()` |
| collection count | `await expect(page.getByRole('row' \| 'listitem')).toHaveCount(n)` |
| attribute | `await expect(locator).toHaveAttribute(name, value)` |
| value (input) | `await expect(locator).toHaveValue(value)` |

Locator query MUST come from the bound Story export — `getByRole` / `getByLabel` / `getByTestId` — never raw CSS or class selectors.

## Forbidden

- Do not re-trigger the operation or perform additional UI interaction.
- Do not assert mock-store state through DOM — use `mock-state-then` when the mutation is not rendered.
- Do not assert URL state through this handler — use `url-then`.
- Do not infer text content, role, or attribute names outside `L4.assertion_bindings`.
- Do not use raw CSS class selectors or nth-child positional selectors when role / label / test-id is available.
- Do not bind to the component file alone — Story export is mandatory.
- Do not check schema conformance of the underlying response — that is layer-level (I2).
- Do not assert through `page.evaluate(() => document.querySelector(...).textContent)`; use `locator.toHaveText` instead.
