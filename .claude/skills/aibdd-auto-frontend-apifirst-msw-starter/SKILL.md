---
name: aibdd-auto-frontend-apifirst-msw-starter
description: Frontend API-First Walking Skeleton 初始化。負責建立純淨的 Next.js 14 + MSW + Cucumber + Playwright 前端骨架，包含全域主題、i18n 與 API Client 基礎設施。
user-invocable: true
---

## I/O

| 方向   | 內容 |
| ------ | --- |
| Input  | 專案根目錄路徑 + `arguments.yml` 參數 |
| Output | 完整的 Frontend Walking Skeleton 基礎架構 |

## 角色

基礎架構建構器。負責搭建穩定的前端骨架，不包含特定的 UI 元件庫或業務邏輯頁面。

---

## 執行流程與 Batch 說明

本技能專注於 Batch A、B、D、E、F 的基礎結構交付。
**Batch C (共用元件)** 的進階內容應配合 `aibdd-auto-frontend-ui-library` 技能使用。
**業務頁面**（如列表、詳情）應配合 `aibdd-auto-frontend-nextjs-pages` 技能使用。

### Batch A — 基礎建設
- `package.json`, `tsconfig.json`, `next.config.mjs`
- `i18n` 基礎設施
- `middleware.ts`

### Batch B — App Shell (基礎)
- `layout.tsx`, `page.tsx` (落地頁跳轉)
- `globals.css` (包含基底 @theme 與 utility，**依設計參數套用色彩 token**)
- `layout.tsx` (Protected Area Wrapper)

### Batch D — API Client & Types
- `client.ts`, `index.ts` (API 核心)

### Batch E — MSW 骨架
- `browser.ts`, `handlers/index.ts`

### Batch F — 測試骨架
- Cucumber hooks, World, Playwright 整合。

---

## Mock 資料最佳實踐 (Mock Data Best Practices)

- **覆蓋率**：Mock 資料應涵蓋完整的業務範圍。例如：會計期間應預先定義當前年度的所有月份（如 `2026-01` 至 `2026-12`），以避免前端組件因找不到期間而報錯。
- **一致性**：`fixtures.ts` 應作為單一事實來源 (Source of Truth)，供所有 Handlers 使用。
- **持久化模擬**：建議在 `handlers/store.ts` 中建立記憶體內的資料副本，以支援開發過程中的增刪改查模擬。

---

## 已知陷阱與修正模式

> 以下為在真實專案中踩過的坑，**執行此 skill 前必讀**，避免重工。

### ⚠️ 陷阱 1 — MSWProvider 的 `useState(false)` 破壞 production build

**症狀**：`npm run build` 成功，但 production 頁面是空白（無內容）。

**根本原因**：  
`useState(false)` 在 SSR / Static Generation 階段讓 `children` 永遠不渲染（`useEffect` 不在 server 執行），導致靜態 HTML 是空的。

**正確模式**（已更新到 `src__components__MSWProvider.tsx` 樣板）：
```tsx
const shouldMock = process.env.NEXT_PUBLIC_MOCK_API === 'true'
// 關鍵：production 時 shouldMock=false → ready=true → children 直接渲染
const [ready, setReady] = useState(!shouldMock)
```
完整實作參見 `templates/src__components__MSWProvider.tsx`。

---

### ⚠️ 陷阱 2 — MSW Service Worker 啟動時序（`ERR_CONNECTION_REFUSED`）

**症狀**：E2E 步驟中 `page.goto('/login')` 後立即填表單送出，API call 失敗：  
`net::ERR_CONNECTION_REFUSED POST /api/auth/login`

**根本原因**：  
MSW Service Worker 是**非同步啟動**的。`MSWProvider` 的 `useEffect` 在 React hydration 後才執行，但 Cucumber steps 可能在 SW ready 之前就觸發互動。

**修正**：  
1. `MSWProvider` 在 `worker.start()` 後寫入 `document.documentElement.dataset.mswReady = 'true'`
2. E2E steps 用 `gotoAndWaitMSW()` 取代直接 `page.goto()`

```ts
async function gotoAndWaitMSW(page: Page, baseUrl: string, path: string) {
  await page.goto(`${baseUrl}${path}`)
  await page.waitForFunction(
    () => document.documentElement.dataset.mswReady === 'true',
    { timeout: 20_000 }
  )
}
```

---

### ⚠️ 陷阱 3 — 跨頁導航 MSW store 重置（in-memory state lost）

**症狀**：在頁面 A 新增資料 → `page.goto()` 到頁面 B → 資料消失，handler 回傳空陣列。

**根本原因**：  
`page.goto()` 觸發全頁重載，JavaScript bundle 重新執行，module-scope 變數（handlers 的 in-memory array）被清空。

**修正**：使用 `sessionStorage` 持久化 store。  
詳細模式見 `references/msw-store-persistence.md`（在 `apifirst-msw-starter` skill 的 references 目錄）。

---

### ⚠️ 陷阱 4 — `sessionStorage.clear()` 清除 MSW store

**症狀**：E2E 步驟模擬「登出」後，後續步驟中 MSW handlers 回傳空資料。

**根本原因**：  
`sessionStorage.clear()` 清除所有 key，包含 `__msw_store__`。

```ts
// ❌ 錯誤 — 毀掉 MSW store
await page.evaluate(() => sessionStorage.clear())

// ✅ 正確 — 只清 auth 相關 key
await page.evaluate(() => {
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
})
```

---

### ⚠️ 陷阱 5 — Windows 上 Port 衝突（IPv6 `::1`）

**症狀**：Next.js 看起來成功啟動在 `3000`，但 Playwright 的請求得到 `ERR_CONNECTION_REFUSED` 或得到不相關的回應。

**根本原因**：  
Windows 上 `localhost` 可能解析為 IPv6 `[::1]`。若有其他服務（如 VS Code 擴充功能、DevTools proxy）佔用 `[::1]:3000`，Next.js 在 `0.0.0.0:3000` 的監聽不衝突，但請求卻被路由到錯誤的 process。

**修正**：明確指定 port 3001（starter 預設值），並確保所有設定一致：
- `package.json`: `"dev": "next dev --port 3001"` 和 `"start:e2e-server": "... next dev --port 3001"`
- `support/world.ts`: `baseUrl = process.env.BASE_URL ?? 'http://localhost:3001'`
- `test:cucumber` script: `BASE_URL=http://localhost:3001`

---

### ⚠️ 陷阱 6 — Cucumber `progress-bar` formatter 在 Windows PowerShell 崩潰

**症狀**：`npm run test:e2e` 輸出：  
`Error: Cannot use progress-bar formatter in non-TTY environment`

**根本原因**：  
Windows PowerShell pipe 不是 TTY。`progress-bar` formatter 需要 TTY。

**修正**：`cucumber.js` 改用 `progress`（不是 `progress-bar`）：
```js
format: ['progress', 'html:e2e-report/index.html']
```

---

## 前端設計風格參數讀取（arguments.yml）

> **執行 Batch B 前必讀此節**，確保登入頁套用正確的設計模板。

執行時從 `specs/arguments.yml` 讀取三個設計參數：

| 參數                    | 選項值                               | 設計行為                       |
| ----------------------- | ------------------------------------ | ------------------------------ |
| `FRONTEND_AUTH_LAYOUT`  | `split` / `centered`                 | 登入／註冊頁是否含左側視覺面板 |
| `FRONTEND_DESIGN_STYLE` | `dark` / `light`                     | globals.css 全局色彩 token     |
| `FRONTEND_ACCENT_COLOR` | `teal` / `indigo` / `blue` / `amber` | CSS accent 主色                |

### 對應模板選擇規則

| FRONTEND_AUTH_LAYOUT | FRONTEND_DESIGN_STYLE | 使用模板 / 設計方向                                                                       |
| -------------------- | --------------------- | ----------------------------------------------------------------------------------------- |
| `split`              | `dark`                | `templates/src__app__public__login__LoginForm.tsx.template` + 深色 token（`#0a0f1e`）    |
| `split`              | `light`               | 同 split 結構，token 換成淺色底色（`#f8fafc`）                                            |
| `centered`           | `dark`                | 去掉左側面板，只保留右側表單，深色背景                                                    |
| `centered`           | `light`               | 去掉左側面板，只保留右側表單，淺色背景                                                    |

### globals.css 色彩 token 對照

```css
/* dark + teal（預設） */
--app-bg: #0a0f1e; --app-surface: #111827; --app-accent: #00d4b1;

/* dark + indigo */
--app-bg: #0f0e1a; --app-surface: #16152a; --app-accent: #818cf8;

/* light + blue */
--app-bg: #f8fafc; --app-surface: #ffffff; --app-accent: #3b82f6;

/* light + indigo */
--app-bg: #f5f3ff; --app-surface: #ffffff; --app-accent: #6366f1;
```

若 `arguments.yml` 未設定這三個參數，**預設使用 split + dark + teal**。