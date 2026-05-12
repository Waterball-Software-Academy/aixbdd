# Admin Defaults (Starter Contract)

This reference defines default behavior for admin pages (for example: records, reports, settings) generated after the walking skeleton.

## 1) Data visibility by default

- Admin list pages MUST load data on initial render.
- Users should not be forced to click `Query/Search` before seeing any rows.

## 2) Empty filter semantics

- Empty filter input means **no filter** (show all), not invalid query.
- Frontend API client, backend endpoint, and MSW handlers must share the same semantics.

## 3) Cross-page consistency

- Pages in the same admin group must keep consistent:
  - content density
  - horizontal spacing
  - information hierarchy
  - placement of query actions and feedback

## 4) Recommended RSC structure

For pages with heavy client hooks (`useState`, `useEffect`, `useRouter`, `useSearchParams`):

- Keep `app/**/page.tsx` as a thin server wrapper.
- Move interactive logic into a dedicated client component (`*Client.tsx` or `*View.tsx`).

## 5) React Client Manifest error SOP

When you see:
`Could not find the module "...#<name>" in the React Client Manifest`

use this sequence:

1. Verify `page.tsx` is a Server Component, and it imports the Client Component correctly.
2. This error usually occurs when you switch a component from named export to default export (or vice-versa), and Next.js caches the old manifest.
3. **Delete the `.next` directory** and restart the dev server.
4. If it still fails, rename the client component file (e.g., append `View`) and update the import.
5. Check sibling admin pages for the same anti-pattern.

## 6) Backward compatibility mode

If existing backend still enforces required query params and returns `INVALID_QUERY`:

- Use a temporary frontend compatibility fallback (documented clearly).
- Plan contract alignment as follow-up; do not keep fallback as final architecture.

## 7) Running backend route parity (Docker / stale process)

If `DELETE`, `PUT`, or item-scoped `GET` returns **404** while the repo already defines routes under `app/api/*`:

- Inspect **`GET /openapi.json`** on the running server. If paths like `/api/<resource>/{id}` are missing while the codebase includes them, the **running image or process is stale** (common with Docker `api` service not rebuilt after router changes).
- Remediation: rebuild and restart the API container, e.g. `docker compose build api && docker compose up -d api`, or restart local `uvicorn` so it loads the current `app/` tree.
- **Do not** treat this as “feature not implemented” in UI copy; the fix is operational (reload routes).

## 8) API client path segments

Encode dynamic identifiers in URL paths with **`encodeURIComponent`** before concatenation (e.g. `entry_id` that may contain reserved characters). Query strings continue to use `URLSearchParams` as usual.

## 9) Overflow menu (`⋯`) dismiss behavior

Do not rely on native `<details>` alone for row action menus: clicks outside the menu often do not close it consistently.

- Use **controlled open state** (e.g. `openMenuId: string | null`).
- On **`pointerdown`** (capture phase on `document`), if the event target is **not** inside a marked root (e.g. `[data-row-actions-menu]`), set open state to closed.
- When opening a **modal** or **navigating** to a dedicated edit route, **clear** the menu state first so the menu does not stay open behind the overlay.

## 10) Modal overlay click-to-dismiss

For full-screen dimmed overlays, attach **`onClick`** on the backdrop to close the dialog; on the **panel** (card), call **`stopPropagation`** on `click` so clicks inside the form do not dismiss the modal.

## 11) Destructive delete confirmation

- **Never** call `DELETE` from a row menu item click alone. Open a **confirmation dialog** first (title, body, Cancel, Confirm).
- **Confirm** runs the destructive action; **Cancel** closes without side effects.
- Prefer **`role="alertdialog"`** for delete confirmations when the message is critical.
- Keep stable **`data-testid`** on confirm/cancel buttons for Playwright/Cucumber flows.
