# Batch Gates — Step 4 驗證清單

每個 Batch 寫入完成後，執行對應的 Gate。Gate 失敗時**立即修復**，不繼續下一個 Batch。

## Gate A — 基礎建設

- [ ] `npm install` 成功，無 peer dependency 衝突
- [ ] `package.json` 含 `next-intl`、`next-themes`、`cross-env`、`start-server-and-test`、`test:e2e` / `test:cucumber` / `start:e2e-server` scripts
- [ ] `next.config.mjs` 以 `createNextIntlPlugin('./${SRC_DIR}/i18n/request.ts')` 包裝，且仍包含 `rewrites()`（`/api/:path*`）
- [ ] `.env.development` 與 `.env.example` 皆包含 `BACKEND_URL`
- [ ] `postcss.config.mjs` 存在，且 `plugins` 含 `@tailwindcss/postcss`
- [ ] `src/app/globals.css`（或 `${SRC_DIR}/app/globals.css`）含 `@import "tailwindcss";`（Tailwind v4，見 [官方 Next.js 指南](https://tailwindcss.com/docs/installation/framework-guides/nextjs)）
- [ ] `tsconfig.json` 的 `exclude` 含 `${STEPS_DIR}`、`support`、`dist-test`（避免 `tsc --noEmit` 混編譯 E2E）
- [ ] 無殘留 `{{PLACEHOLDER}}`
- [ ] `src` 目錄有 `middleware.ts`（首次造訪依 `Accept-Language` 寫入 `NEXT_LOCALE`；matcher 排除 `/api`、`/_next`、含副檔名靜態資源）
- [ ] `${SRC_DIR}/i18n/routing.ts`、`locale-negotiation.ts`、`request.ts` 存在且 `request.ts` 載入 `messages/{locale}.json`

## Gate B — App Shell

- [ ] `npm run dev` 能啟動（port **3001** 可連線；`package.json` 的 `dev` script 須含 `--port 3001`）
- [ ] **URL 不含語系前綴**：訪問 `/` 產生 redirect 到 `/products`（路徑中無 `/en`、`/zh-TW` 等 locale 段）
- [ ] `${SRC_DIR}/app/(protected)/products/page.tsx` 存在且含 `data-testid="smoke-landing-heading"`（供 smoke E2E）
- [ ] `${SRC_DIR}/app/api/locale/route.ts` 存在（POST 切換語系 Cookie）
- [ ] `${SRC_DIR}/app/layout.tsx` 包裹 `ThemeProvider` → `NextIntlClientProvider`（含 `locale`）→ `MSWProvider`
- [ ] `body` 已使用語意化 Tailwind（例如 `bg-background`、`text-foreground`），且 `globals.css` 含 `@custom-variant dark` 與 `@theme` 權杖

## Gate C — 共用元件

- [ ] 所有元件檔案的 import path 正確（相對路徑或 `@/` alias）
- [ ] `TopBar` 含 `AppearanceToolbar`（語系改為 `fetch('/api/locale')` + `router.refresh()`，非 URL 切換）
- [ ] `tsc --noEmit` 針對這些元件無型別錯誤

## Gate D — API Client + Types

- [ ] `client.ts` 的 `BASE_URL` 讀取自 `process.env.NEXT_PUBLIC_API_BASE_URL`
- [ ] `apiClient` 函式從 `api/index.ts` 正確 re-export
- [ ] Mock 開啟時 MSW 攔截；Mock 關閉時 rewrite proxy 到 `BACKEND_URL`

## Gate E — MSW 骨架

- [ ] `browser.ts` export `initMocks` 函式
- [ ] `handlers/index.ts` export 空的 `handlers` 陣列（由後續 worker 填入）
- [ ] `MSWProvider` 的 dynamic import path 與 `browser.ts` 位置一致，且 destructure `{ initMocks }`（非 `startMSW` 或其他別名）
- [ ] `MSWProvider` 使用 `useState(!shouldMock)` 模式（**不是** `useState(false)`），確保 production build 直接渲染 children
- [ ] `MSWProvider` 在 `worker.start()` 後寫入 `document.documentElement.dataset.mswReady = 'true'`，供 E2E `gotoAndWaitMSW` 等待
- [ ] `MSWProvider` 回傳非 ready 時為 `<div data-msw-provider="loading" suppressHydrationWarning />`（不是 `return null`，避免 hydration mismatch）

## Gate F — 測試骨架與範例 E2E

- [ ] `cucumber.js` 的 `paths`、`require` 指向 `${FRONTEND_FEATURES_DIR}`、`support/hooks.ts`、`${STEPS_DIR}/**/*.steps.ts`；`timeout` 建議 `60000`
- [ ] `support/world.ts`、`support/hooks.ts`、`support/route-helpers.ts`、`support/parse-helpers.ts` 已寫入
- [ ] `${FRONTEND_FEATURES_DIR}/smoke/app.feature` 與 `${STEPS_DIR}/smoke.steps.ts` 已寫入（內建 smoke，非業務規格）
- [ ] `support/world.ts` 的 `AppWorld` 含 `baseUrl: string`（constructor 讀取 `process.env.BASE_URL ?? 'http://localhost:3001'`）
- [ ] `support/world.ts` 的 `AppWorld` 含 `gotoAndWaitMSW(path: string)` 方法（`page.goto` + `waitForFunction(mswReady)`）
- [ ] `steps/smoke.steps.ts` 的 `Given I open the app root` 使用 `this.gotoAndWaitMSW('/')` 而**非**裸 `page.goto()`
- [ ] `cucumber.js` 的 `format` 使用 `['progress', ...]`（**不可**用 `progress-bar`，Windows 非 TTY 會崩潰）
- [ ] `npx cucumber-js --dry-run` 至少 1 scenario、不報錯
- [ ] `npx playwright install chromium` 已執行（首次）
- [ ] `npm run test:e2e` 通過（啟動 3001 + MSW + smoke scenario）
