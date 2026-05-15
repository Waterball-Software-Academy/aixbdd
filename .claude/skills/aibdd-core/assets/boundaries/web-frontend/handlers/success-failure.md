# Handler: success-failure

## Role

`success-failure` renders verification of the success-or-failure feedback class surfaced to the user.

It belongs to:

- `sentence_part`: `success-failure`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies the result class of the previously invoked operation — success, failure, or a specific error category — observed through a feedback surface (toast, inline error, banner, status pill). The exact surface comes from `L4.assertion_bindings.surface`.

## Context Contract

Reads `page` and the locator derived from the feedback component's Story export (when the surface is a project-owned component) or directly from ARIA roles (when the surface is a native `role=alert` / `role=status`). Reads the already-rendered DOM, not a new interaction.

Writes no behavior state.

## Storybook Binding (I4)

When the feedback element is a project-owned component (toast wrapper, banner component), `L4.source_refs.component` MUST point to the Story export representing the feedback state. Native ARIA roles used directly on `page` (`page.getByRole('alert')`, `page.getByRole('status')`) do not require a Story binding, but MUST match the role declared in `L4.assertion_bindings.surface`.

## Schema Gate (I2) Interaction

The OpenAPI response that drove the feedback was already Zod-validated by the variant's mock layer when the call dispatched. This handler MUST NOT re-validate response schema; it only verifies the user-visible feedback class.

## Playwright Surface

Primary calls:

- `await expect(page.getByRole('alert' | 'status')).toBeVisible()`
- `await expect(locator).toContainText(reason)` (when reason text is bound)
- `await expect(locator).toHaveAttribute('data-state', value)` (when surface declares a state attribute)

The locator is derived from `L4.assertion_bindings.surface` plus optional Story export reference.

## Forbidden

- Do not re-trigger the operation (no `ui-action`-style verbs in the body).
- Do not inspect response payload fields unrelated to success or failure — that is `ui-readmodel-then`.
- Do not assert persisted mock-store state — that is `mock-state-then`.
- Do not redeclare OpenAPI schema validation; the mock layer already enforces it (I2).
- Do not convert this handler into readmodel verification on the same UI surface.
- Do not bind to the component file alone for project-owned feedback surfaces — Story export is mandatory.
- Do not assert outcome class through DOM text alone when an ARIA role / state attribute exists.
