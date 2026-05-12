# UI shell: minimal, Apple-inspired

Technical cues for pages and components built on the Walking Skeleton. **Not** a pixel-perfect copy of Apple products—use as a **consistency baseline**.

---

## Default app shell framework (layout chrome)

The starter ships **one fixed layout model**—there is **no** separate “design picker” in tooling (e.g. kickoff); workers extend this shell in place.

| Region | Role | Template file (output path) |
|--------|------|------------------------------|
| **Left sidebar** | Primary navigation area (nav items filled later) | `components/Sidebar.tsx` → `${SRC_DIR}/components/Sidebar.tsx` |
| **Top bar** | Single-line workspace title + appearance controls + user menu (logout inside dropdown) — **sidebar toggle is in `Sidebar`, not TopBar** | `components/TopBar.tsx` |
| **Main** | Page content; generous padding, reading width optional | `(protected)/layout.tsx` wraps `<main>` around `{children}` |

**Structure** (classic dashboard pattern):

```
┌─────────────┬──────────────────────────────────┐
│  Sidebar    │  TopBar (sticky, frosted)        │
│  (fixed w)  ├──────────────────────────────────┤
│             │  Main (scrollable content)       │
│             │                                  │
└─────────────┴──────────────────────────────────┘
```

- Implemented as a **horizontal flex**: sidebar `shrink-0`, right column `flex-1 flex-col` with `TopBar` + `main`.
- **Appearance / i18n** live in **TopBar** (`AppearanceToolbar`) by default—not in the sidebar.
- Sidebar is **collapsible** by default (`app-sidebar-collapsed` in `localStorage`), toggled from TopBar.
- User area (`UserMenu`) provides profile stub + login/logout button baseline for worker extension.
- Sidebar nav items should include **icon + label** (collapsed state keeps icon-only affordance).
- User area should be a **clickable dropdown panel**; logout action should live inside the panel.

**Color and typography** are **token-based** in `app/globals.css` (`:root`, `html.dark`, optional `data-accent`), surfaced via Tailwind semantic classes (`bg-background`, `bg-sidebar`, `text-foreground`, …).

---

## Principles

- **Typography**: System stack (`-apple-system`, `SF Pro` fallbacks, `Segoe UI`, sans-serif). Prefer **tight tracking** on large titles, **relaxed line height** on body (~1.5–1.6). Avoid decorative display fonts unless the product spec requires them.
- **Color**: Neutral surfaces (light grays / dark grays), **one** primary accent (`text-primary` / `--app-primary`). No rainbow chrome; use `muted-foreground` for secondary text.
- **Layout**: Generous padding (`px-6`–`px-10`, `py-8`+ on main content), `max-w-*` for reading width where appropriate. Avoid cramped edge-to-edge forms unless mobile-first demands it.
- **Chrome**: Thin separators (`border-border` / low-opacity hairlines), optional **frosted** top bar (`backdrop-blur` + translucent `bg-background/80`). Sidebar slightly different surface (`bg-sidebar`) from main.
- **Iconography**: Use compact line icons for nav and actions; avoid plain single-letter placeholders in production views.
- **Controls**: Rounded corners at **md** scale (`--app-radius-md` / `lg`), compact height (~32px) for selects and toolbar controls. Focus rings: subtle `ring-primary/30`, not thick outlines.
- **Motion**: Prefer **short** transitions; avoid bouncy or playful animation unless specified.

---

## Changing the shell (without a separate “framework selector”)

If the product needs a **different** chrome (e.g. **top-only** nav, **collapsible** sidebar, **double top bar**):

1. Edit **`app/(protected)/layout.tsx`** (or introduce a client `AppShell` wrapper) to change the flex/grid structure.
2. Keep using **semantic tokens** from `globals.css` so palette and dark mode stay coherent.
3. Update **E2E** selectors (`data-testid` on `sidebar`, `topbar`, etc.) if layout DOM changes.

Do **not** add parallel ad-hoc color scales in random components—extend `@theme` / CSS variables instead.

---

## Tailwind alignment

Reuse semantic tokens from `globals.css`: `bg-background`, `bg-sidebar`, `text-foreground`, `text-muted-foreground`, `border-border`, `text-primary`, `dark:` variants.

## Foundation utility classes

Starter `globals.css` also defines reusable component classes; feature pages should prefer these to avoid style drift:

- `.ui-surface`: standard card/container surface
- `.ui-input`: standard text/date input
- `.ui-select`: standard select control
- `.ui-btn-primary`: primary action button
- `.ui-btn-secondary`: secondary/neutral action button

---

## Recent baseline updates

Keep these decisions aligned with `aibdd-auto-frontend-nextjs-pages/SKILL.md` to prevent style drift:

1. **RSC client export convention**  
   For `...Client.tsx` used as page wrappers, prefer **default export/import** (`export default function XClient`, `import XClient ...`). Do not switch between default and named exports frequently, as this triggers the "Could not find the module in the React Client Manifest" Next.js bundler bug. If this bug occurs, you MUST stop the dev server, delete the `.next` folder, and restart.

2. **Admin list toolbar CTAs (Add + Load list / Query)**  
   When **Add** and **Load list** / **Query** sit in the same mental group, use **`ui-btn-secondary`** from `globals.css` for both so height and border treatment match.  
   Do not use large filled primary buttons unless spec explicitly requires strong emphasis.

3. **Filter row: keep query on the same row (md+)**  
   Place filters **on the same row** as the **Load list / Query** button at `md` breakpoints and up (e.g. CSS grid: `minmax(0,1fr)` columns + `auto` for the action). This applies to **Record Management** (filters + query), **Reporting** (report type + conditions in a **single** `<form>`), and similar. Wrap the button column in `flex flex-col justify-end` so the button baseline-aligns with inputs. On small screens, stack (`grid-cols-1`); full-width button is fine. Hidden test-only controls should not consume a visible grid column—move them outside the grid in a `hidden` wrapper.

4. **Login public page layout**  
   Split layout (left visual, right form) is allowed as a baseline variant.  
   Left side can include particle/glow effects with mobile fallback (hide/simplify on small screens).  
   Right-side form can be flat (no mandatory outer card wrapper) when minimal UI is requested.
