# i18n and theme (Walking Skeleton contract)

Technical reference for the API-First MSW starter. Worker-facing; keep in sync with `templates/`.

## Internationalization (`next-intl`, **no locale in URL**)

- **No path-based locales**: Routes stay `/products`, `/`, etc. There is **no** `app/[locale]` segment and **no** `next-intl` locale-prefixed navigation helpers.
- **Default locale**: On the first visit without `NEXT_LOCALE` cookie, the active locale is resolved from the **`Accept-Language`** header (see `locale-negotiation.ts`). Middleware mirrors this by setting the cookie so behavior is stable across navigations.
- **Persistence**: Cookie name **`NEXT_LOCALE`** (`path: /`, long-lived). `getRequestConfig` resolves locale as: valid cookie → else `Accept-Language` negotiation → `defaultLocale` (`zh-TW`).
- **Manual switch**: `POST /api/locale` with `{ "locale": "zh-TW" | "en" }` sets the cookie; the UI calls `router.refresh()` so Server Components re-render with new messages.
- **Messages**: JSON under `messages/{locale}.json`. Add namespaces as features grow.
- **Login page test account**: The login screen reads **dev credentials from i18n**, not hardcoded in TSX. Use `login.testAccount.{title,usernameLabel,username,passwordLabel,password,note}` so `admin` / `admin` (or other values) stay in JSON and match backend `AUTH_DEV_USERNAME` / `AUTH_DEV_PASSWORD`.
- **Top bar appearance**: Locale, theme toggle, and accent are **siblings in the TopBar flex row** (`AppearanceToolbar` root uses `display: contents`). Locale and accent each use **Globe** + `<select>` and **Palette** + `<select>` inside a small `rounded-md border` chip (`inline-flex h-8 gap-1`); select uses `.ui-toolbar-minimal-select--with-icon` (no inner border). **User menu** trigger has **no border** (`border-0`), generous `py-2 pl-3 pr-2`, `rounded-lg`, hover `bg-muted/45`; avatar is `h-6 w-6` with fill only (no ring). CJK names use a person glyph; Latin uses initials. Dropdown may show name + `memberRole`.
- **Server vs client**: Prefer `getTranslations` in Server Components; `useTranslations` / `useLocale` in Client Components. Root layout uses `getLocale()` + `getMessages()` and passes `locale` to `NextIntlClientProvider`.
- **Navigation**: Use **`next/link`** and **`redirect` from `next/navigation`** for app routes (no locale segment to preserve).

## Theme (`next-themes` + Tailwind v4)

- **Light/dark**: `ThemeProvider` sets `class` on `<html>` (`dark` for dark mode). `globals.css` defines `@custom-variant dark` for Tailwind `dark:` utilities.
- **Semantic colors**: Prefer `@theme` tokens (`bg-background`, `text-foreground`, `border-border`, `text-primary`, `text-muted-foreground`) backed by CSS variables in `globals.css`.
- **Accent palettes**: `data-accent` on `<html>` (`ocean`, `amber`; default clears the attribute). Persisted via `localStorage` key `app-accent` in `AppearanceToolbar`.
- **Hydration**: Root layout sets `suppressHydrationWarning` on `<html>` for theme class switching.

## E2E notes

- Smoke still expects `/` → `/products` and `data-testid="smoke-landing-heading"`; URLs **do not** include a locale prefix.
- Optional scenarios may assert `data-testid`: `locale-switcher`, `theme-switcher`, `palette-switcher`, `appearance-toolbar`.
