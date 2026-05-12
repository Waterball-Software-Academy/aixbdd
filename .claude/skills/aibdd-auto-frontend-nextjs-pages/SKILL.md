---
name: aibdd-auto-frontend-nextjs-pages
description: >
  前端 Next.js 頁面實作。基於已完成的 Walking Skeleton（MSW + API client）和 UI/UX
  consultant 產出的 layout.html 靜態原型，將靜態頁面轉換為動態 Next.js React 元件。
  當使用者要求實作前端頁面、將 layout.html 轉為 Next.js、或在已有 MSW 骨架的前端專案中
  開發功能頁面時，使用此 skill。需要 specs 目錄下的 activities 或 features 作為規格參考。
  可搭配 /aibdd-auto-frontend-msw-api-layer 所產生的 API 基礎建設。
user-invocable: true
---

# Next.js 頁面實作器

將靜態 HTML 原型 + 規格文件轉換為動態 Next.js 頁面。

**前提假設**：
- Walking Skeleton 已由 `/aibdd-auto-frontend-apifirst-msw-starter` 初始化完成（含 `app/(protected)/{{PRIMARY_ENTITY}}/page.tsx` **占位**、**next-intl**〔Cookie + `Accept-Language`，**URL 不含語系**〕與 **next-themes**／強調色切換、`features/smoke` + `npm run test:e2e`）
- **預設 UI 框架**（與 Kickoff 無關）：**左側導覽（Sidebar）+ 頂部列（TopBar）+ 主內容區**，簡約／偏 Apple 系統風之 **色系與字體權杖** 見 starter 的 [references/ui-shell-minimal.md](../aibdd-auto-frontend-apifirst-msw-starter/references/ui-shell-minimal.md)。落地新頁面時應延續同一 shell 與 token，除非規格明定改版型。
- MSW API layer 已由 `/aibdd-auto-frontend-msw-api-layer` 產生完成
- API client 函式（`src/lib/api/`）和 Zod schemas（`src/lib/types/`）已就位
- 管理頁預設行為（initial fetch、空白篩選語義、RSC manifest SOP）以 starter 參考檔為準：[../aibdd-auto-frontend-apifirst-msw-starter/references/admin-defaults.md](../aibdd-auto-frontend-apifirst-msw-starter/references/admin-defaults.md)

若 Activity 的預設落地頁**不是** `/{{PRIMARY_ENTITY}}`，應一併調整 `app/page.tsx` 的 `redirect`（`next/navigation`）、smoke feature/steps（或改測第一個真實頁），並回歸 `npm run test:e2e`。細節與 MSW 協作見 `/aibdd-frontend-e2e-cucumber-playwright`。

```
1. 參數載入        — 從 arguments.yml 讀取路徑配置
2. 規格校驗        — 確認 activities 或 features 至少擇一存在
3. 盤點頁面        — 從規格推導需要實作的頁面清單
4. 元件拆解        — 將 layout.html 拆解為 React 元件樹
5. 逐頁實作        — 將靜態 HTML 轉為動態 Next.js 頁面
6. 整合驗證        — 確保頁面間導航與資料流正確
```

## Phase 0：參數載入

從 `${SPECS_HOME}/arguments.yml` 讀取路徑配置：

| 參數 | 用途 | 範例值 |
|------|------|--------|
| `PROJECT_ROOT` | 前端專案根目錄 | `frontend/` |
| `SPECS_HOME` | 規格文件目錄 | `specs/` |
| `SRC_DIR` | 原始碼目錄 | `src` |
| `TYPES_DIR` | Zod schema 目錄 | `src/lib/types` |
| `API_CLIENT_DIR` | API client 目錄 | `src/lib/api` |

額外掃描的路徑（非參數，固定慣例）：

| 路徑 | 用途 |
|------|------|
| `${SPECS_HOME}/activities/*.activity` | Activity Diagram，推導頁面流程 |
| `${SPECS_HOME}/features/**/*.feature` | Feature Files，推導頁面功能細節 |
| `${SPECS_HOME}/activities/*.testplan.md` | 測試計畫（Optional），供驗證參考 |
| `${PROJECT_ROOT}/layout.html` 或 `${SPECS_HOME}/*.layout.html` | UI/UX 靜態原型 |

## Phase 1：規格校驗

**必要條件**：`activities/` 或 `features/` 至少擇一存在。

```
掃描 ${SPECS_HOME}/activities/*.activity
掃描 ${SPECS_HOME}/features/**/*.feature

存在任一？
  ├─ 是 → 繼續 Phase 2
  └─ 否 → 中斷
         ├─ 預設：輸出錯誤訊息，請使用者提供 .activity 或 .feature 檔案
         └─ 使用者強行要求 → 根據 layout.html 的頁面結構腦補基礎規格
```

校驗細節見 [references/spec-validation.md](references/spec-validation.md)。

## Phase 2：盤點頁面

從規格文件推導需要實作的頁面清單。

### 從 Activity Diagram 推導

每個 `[STEP]` 綁定的 `.feature` 暗示一個使用者操作場景。
將相關操作歸類為頁面：

```
[STEP:1] {specs/features/{{MODULE}}/ActionA.feature}  → /{{MODULE}}/action-a 頁面
[STEP:2] {specs/features/{{MODULE}}/ActionB.feature}  → /{{MODULE}}/new 頁面（或清單頁的新增功能）
[STEP:5] {specs/features/{{MODULE}}/QueryList.feature}  → /{{MODULE}} 清單頁面
```

### 從 Feature Files 推導

每個 `Feature:` 對應一個功能模組。按 CRUD 語意歸類：
- `查詢/清單` → List 頁面
- `新增/建立` → Create 表單（或 List 頁面的 Modal）
- `編輯/更新` → Edit 表單（或 Detail 頁面的 inline editing）
- `刪除` → Delete 確認（通常是 Modal 或 Popconfirm）
- `詳情/檢視` → Detail 頁面

#### 管理頁預設模式（CRUD Console）

當規格包含 `查詢 + 新增 + 編輯 + 刪除`，且未指定特殊資訊架構時，預設採用「管理頁模式」：

1. **雙視圖切換**：同一資料集提供 `Card Grid` 與 `Table/List` 兩種視圖，讓使用者可在摘要瀏覽與精準比對間切換。
2. **卡片操作入口**：每張卡片右上角提供 `⋯`（overflow menu），至少含 `Edit`、`Delete`。
3. **新增/編輯雙模式**：提供 `Modal` 與 `Dedicated Page`（如 `/resource/new`、`/resource/[id]/edit`）兩種工作流；若規格未指定，至少先保留可切換能力。
4. **工具列一致性**：列表區上方固定包含 `Create`、Filter/Query controls、View mode toggle。
5. **可回歸測試的 selector**：保留穩定 `data-testid`（載入、清單、主要 CTA），避免 UI 重構破壞 E2E。

> Single source of truth: 管理頁通用預設規範請以 [starter admin-defaults](../aibdd-auto-frontend-apifirst-msw-starter/references/admin-defaults.md) 為主；本 skill 應與該檔保持一致，避免雙邊漂移。

#### 跨頁一致性（模組組群）

當同一模組群屬於同一管理工作流（例如列表、對帳、報表）時，必須同步套用一致規則，不可只改單頁：

1. **密度一致**：採用管理後台密度（緊湊間距、以表格/清單為主），避免單頁卡片化。
2. **留白一致**：左右間距與內容寬度需一致，避免某頁過窄導致視覺割裂。
3. **語意一致**：頁首用精簡標題，避免冗長導言文案佔版面。
4. **互動一致**：查詢列、主要 CTA、錯誤提示的位置模式一致。
5. **驗收一致**：修改任一頁時，至少人工檢查同群組頁面是否仍維持一致風格。
6. **預設可見資料**：管理頁清單進入頁面後應先顯示資料（無篩選），不要求使用者先按「查詢」才看到內容。

#### 管理頁預設查詢語義（必須遵守）

1. **Initial Load**：進入清單頁即自動載入資料（initial fetch）。
2. **Empty Filter Semantics**：空白篩選值代表「不過濾」，不是「條件缺失」。
3. **Backward Compatibility**：若後端仍回 `INVALID_QUERY`（舊契約要求必填），前端應有過渡策略（預設期間 fallback 或明確提示），且在 skill 交付說明標記為「compat mode」。
4. **Contract Alignment Priority**：最終目標是同步更新 API contract / backend / MSW，使空白篩選可合法查詢。
5. **No Silent Data Loss**：fallback 不可讓使用者誤以為看到全量資料；若進入 compat mode，應保留可追蹤訊號（log / TODO / 文檔備註其一）。

### 產出：頁面清單

```
盤點結果：
1. /{{MODULE}}              — 清單頁（建立、查詢、刪除）
2. /{{MODULE}}/[id]         — 詳情頁（編輯、狀態設定）
3. /{{MODULE}}/[id]/items   — 子項清單頁（匯入、新增、查詢、刪除）
4. /{{MODULE}}/[id]/items/[itemId] — 子項詳情頁（編輯）
```

## Phase 3：元件拆解

將 `layout.html` 拆解為 React 元件樹。詳細策略見 [references/component-decomposition.md](references/component-decomposition.md)。

核心原則：

1. **視覺保真**：拆解後的元件渲染結果必須與原始 `layout.html` 視覺一致。不能「變醜」。
2. **CSS 遷移**：將 layout.html 的 inline styles 和 `<style>` 區塊轉為 CSS Modules 或 Tailwind classes。
3. **語意化拆解**：按 UI 職責拆分（Header、Sidebar、Content、Table、Form、Modal）。
4. **共用元件提取**：多頁面重複出現的 UI 區塊提取為 `src/components/` 下的共用元件。

### 元件目錄結構

```
src/
├── app/
│   ├── layout.tsx                  ← Root：Intl + Theme + MSW
│   ├── page.tsx                    ← `/` redirect
│   ├── api/locale/route.ts         ← 手動切換語系（Cookie）
│   ├── (protected)/
│   │   ├── layout.tsx              ← Sidebar + TopBar shell
│   │   ├── {{MODULE}}/
│   │   │   ├── page.tsx            ← 模組清單
│   │   │   └── [id]/
│   │   │       ├── page.tsx        ← 模組詳情
│   │   │       └── sub-items/
│   │   │           ├── page.tsx    ← 子項清單
│   │   │           └── [subId]/
│   │   │               └── page.tsx ← 子項詳情
│   │   └── ...
│   └── (public)/                   ← 可選公開頁
├── components/
│   ├── ui/                         ← 通用 UI 元件（Button, Input, Modal, Table...）
│   └── domain/                     ← 業務元件（LeadForm, ProjectCard...）
```

## Phase 4：逐頁實作

對每個頁面，執行以下步驟。詳細模式見 [references/spec-driven-patterns.md](references/spec-driven-patterns.md)。

### 步驟 4A：讀取頁面規格

1. 找到該頁面對應的 `.feature` 檔案
2. 從 `Background:` data table 提取資料結構（→ 表格欄位、表單欄位）
3. 從 `When` 步驟提取使用者操作（→ 按鈕、表單提交、導航）
4. 從 `Then` 步驟提取預期回饋（→ Toast、redirect、UI 狀態變化）
5. 從 `Rule:` 提取驗證規則（→ 表單驗證、條件渲染）

### 步驟 4B：對接 API client

從 `src/lib/api/` 引入已有的 API client 函式：

```typescript
// 已由 msw-api-layer 產生
import { listItems, createItem, deleteItem } from '@/lib/api/{{MODULE}}'
import type { ItemResponse, CreateItemRequest } from '@/lib/types/{{MODULE}}.schema'
```

- **不要重新實作 API 呼叫**。直接使用已有的 API client 函式。
- **不要重新定義型別**。直接使用已有的 Zod schema 推導的 TypeScript type。
- **路徑參數編碼**：URL path 內嵌的識別碼（例如 `entry_number`、`id`）必須以 **`encodeURIComponent(...)`** 包一層再拼進路徑，避免代號含 `/`、`#`、空白等字元時請求落到錯誤路由或變成 404。
- **DELETE／單筆路由與執行中後端一致**：若 `DELETE`／`PUT`／`GET` 單筆回傳 **404**，先比對執行中服務的 **`GET /openapi.json`**（或 `/docs`）是否已有 `/api/.../{param}` 對應方法；若 OpenAPI 僅有 collection 層級（例如只有 `GET`/`POST` `/api/journal-entries`、沒有 `{entry_number}`），代表 **容器映像或本機 uvicorn 程序過舊**，應 **`docker compose build api && docker compose up -d api`** 或重啟載入最新 `app/api/*` 的後端，不是再加前端 workaround。刪除失敗的 Toast 應引導「重啟／重建後端」，避免寫成「功能未實作」造成誤解。

### 步驟 4C：實作頁面元件

1. 從 `layout.html` 對應區塊提取 HTML 結構
2. 將靜態 HTML 轉為 React JSX
3. 用 `useState` / `useEffect` / React Server Components 實現動態行為
4. 從 API client 獲取資料（Server Component: 直接 await / Client Component: useEffect）
5. 實作使用者操作的 handler（form submit、button click）
6. 加入 Loading / Empty / Error 狀態處理

RSC 穩定性要求（Next.js App Router）：
- 若頁面需要大量 client hooks（`useState/useEffect/useRouter/useSearchParams`），建議採用 **Server Wrapper + Client Component**：
  - `app/.../page.tsx` 保持薄層 wrapper（server）
  - 將互動邏輯移至 `...Client.tsx`（`'use client'`）
- 這能降低 `React Client Manifest` 解析錯配風險（例如 `.../page.tsx#default`）。

RSC manifest error 修復 SOP（新增）：
這通常是 Next.js App Router 處理 Server/Client Component 邊界時的 bundler cache bug。如果看到 `Could not find the module "...#{{ENTITY}}Client" (或 #default) in the React Client Manifest` 或遇到由 `_error.js` / `_app.js` 導致的連續 `500 Internal Server Error` 錯誤：
1. **停止 Dev Server 並清除快取**：此問題多半無法透過修改程式碼自癒，**必須**終止終端機，執行 `rm -rf .next`（或手動刪除 `.next` 資料夾），然後重新啟動 `npm run dev`。
2. **統一匯出慣例**：對於從 `page.tsx` 引入的頁面級 Client Component，建議統一改回 **`export default function XxxClient()`**，並在 `page.tsx` 用預設匯入 `import XxxClient from './XxxClient'`。
   - 不要再頻繁於 `export default` 與 named export 間切換，這極易觸發此 bug。
3. 若錯誤仍在，再考慮將檔案重新命名並更新匯入路徑，然後再次刪除 `.next` 並重啟。
4. **檢查編譯錯誤**：執行一次 `npm run build`，這通常會捕捉到導致 500 錯誤的潛在 TypeScript Error（例如前面提到的 `<select readOnly>` 不支援），確保沒有隱藏的錯誤導致開發伺服器崩潰。

（與 starter 版本對齊： [admin-defaults.md](../aibdd-auto-frontend-apifirst-msw-starter/references/admin-defaults.md)）

若是「管理頁模式」，額外要求：
- Grid 與 List 共用同一資料來源與查詢條件（避免視圖切換後狀態不一致）
- **Delete 必須有明確確認**：預設 **Modal／dialog**（含標題、說明、取消／確認），**禁止**從選單一鍵直接呼叫刪除 API；`window.confirm` 僅在規格明定時可用。確認後再呼叫 API，並保留 `data-testid` 供 E2E（例如 `*-delete-confirm`、`*-delete-cancel`）。
- Edit 動作必須能回寫資料層（MSW/真後端皆可驗）
- 在 `Modal` 與 `Dedicated Page` 兩種模式間切換時，不得丟失當前篩選條件
- 清單預設執行一次載入（initial fetch），且「空白篩選值」代表不過濾（顯示全部）
- 錯誤提示預設使用右下角 toast（`<Toast />`，`bottom-4 right-4`），避免頁內紅框破壞後台密度
- **`⋯` overflow 選單**：勿僅依賴原生 `<details>`（點擊頁面其他處不一定關閉）。應以 **受控狀態**（例如 `openMenuId`）搭配 **`document` `pointerdown` capture** 偵測點擊是否在選單根節點（`data-*` 標記）外，於外部點擊時關閉；**開啟 Modal／導向獨立頁** 前也應關閉選單，避免選單浮在彈窗上或殘留開啟狀態。
- **Modal 遮罩**：全螢幕半透明層點擊應可關閉對話框；內容區 **`onClick` `stopPropagation`**，避免按鈕／表單操作誤觸關閉。

### 步驟 4D：樣式遷移與防禦性實作（React / TS Strictness）

從 layout.html 遷移樣式與結構時，除了視覺外，必須確保符合 React 與 TypeScript 規範，避免 500 編譯錯誤：

1. **防禦性 HTML 到 JSX 轉換**：
   - 屬性替換：`class` 轉 `className`，`for` 轉 `htmlFor`。
   - **`readOnly` 在 select 上的錯誤**：標準 HTML/React 中，`<select>` **不支援** `readOnly`，會導致 TypeScript Type Error ( `Property 'readOnly' does not exist on type...` ) 並阻斷建置。若需讓 select 無法操作，請使用 `disabled` 搭配 `onChange={() => {}}`，或純粹使用 `defaultValue` 而不綁定 state。
   - **Controlled Inputs**：若使用 `value={...}`，必須綁定 `onChange`，否則會噴 React Warning；若只是僅供顯示／測試的唯讀欄位，應改用 `defaultValue` 或加上 `readOnly` (input) / `disabled` (select)。

2. **樣式優先順序**：
   - **Tailwind CSS classes**（`/aibdd-auto-frontend-apifirst-msw-starter` 產出的 Walking Skeleton **已預設** Tailwind CSS v4：`globals.css` 為 `@import 'tailwindcss'`，並含 `postcss.config.mjs`）
   - **語意化色票**（`bg-background`、`text-foreground`、`border-border`、`text-primary`、`dark:`）— 與 **next-themes** 及 `globals.css` 內 CSS 變數／`data-accent` 一致，避免硬編 slate 色階導致深色模式失效
   - **CSS Modules**（`page.module.css`）
   - **globals.css 中的 `@theme` / CSS 變數**（Tailwind v4 design tokens）

Walking Skeleton 預設為 **簡約、偏 Apple 系統風**（系統字體、中性色、細邊界、留白、側欄／頂欄層次）。從 `layout.html` 落地時請對齊該基線，細節見 starter 的 [references/ui-shell-minimal.md](../aibdd-auto-frontend-apifirst-msw-starter/references/ui-shell-minimal.md)。

若專案已帶 starter 的 `globals.css` foundation classes，優先重用：`.ui-surface`、`.ui-input`、`.ui-select`、`.ui-btn-primary`、`.ui-btn-secondary`，避免每頁自行發明按鈕／表單樣式造成漂移。

管理後台列表工具列 CTA 風格補充（與近期 UI 調整對齊）：
- **`新增` 與「查詢清單」／`查詢`**：同一視覺層級時，兩者皆使用 **`ui-btn-secondary`**（與 `globals.css` foundation 一致），避免一顆 compact、一顆標準高造成同列不一致。
- 規格若未要求強調主 CTA，`新增` 不預設使用 `ui-btn-primary` 大面積實心按鈕。
- TopBar / Sidebar 的圖示／下拉仍維持 compact（`h-8` 等），與內容區次要 CTA 的 `h-10` secondary 可並存。

**篩選列與查詢按鈕版面（通用管理頁面）**：
- **查詢類按鈕（「查詢清單」「查詢」）須與篩選欄位同一列**，不要單獨放在下一整列；典型做法：`grid grid-cols-1 gap-2 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]`（欄位數可增減，最後一欄 `auto` 留給按鈕）。
- **報表與列表頁的單一表單原則**：如報表類型、會計期間、查詢 按鈕，應統一包在**同一個** `<form onSubmit={...}>` 中，避免將 `submit` 按鈕拆成獨立的 `<form>` 或區塊，導致佈局斷行或按鈕掉到下一列。
- 按鈕欄外層使用 **`flex flex-col justify-end`**，讓按鈕與 `ui-input` / `ui-select` **底緣對齊**（與標題列＋輸入的兩行結構視覺一致）。
- **小螢幕**維持 `grid-cols-1` 直向堆疊；查詢按鈕可用 `w-full`，避免過窄難點。
- 僅供測試／隱藏狀態的控制項（如 `journal-view-mode`）**不要**佔用可見 grid 欄位，改放在 grid 外的 `hidden` 區塊，並注意上述 `disabled` 取代 `readOnly` 的 React 限制。

內容寬度、間距與溢位控制（防禦性排版）：
- `(protected)/layout.tsx` 的主內容區採 `w-full` 基線；**不使用** `mx-auto + max-w-*` 強行收窄內容。
- 頁面根容器**禁止**用 `-mx-*`（negative margin）去「抵銷」layout padding，這會導致水平溢出與滾輪。
- 後台頁根容器預設使用 `w-full space-y-2~2.5`（緊湊模式），由 layout 統一控制 `px-*`。
- `(protected)/layout.tsx` 垂直基線使用 `py-4 sm:py-6`，避免預設 `py-6 sm:py-8` 造成留白過大。
- **表格寬度**：所有具有 `.overflow-x-auto` 包裝的表格，必須加上 `min-w-[480px]` 或適當的最小寬度，避免在小螢幕上欄位被過度擠壓而破壞內容可讀性。

登入頁（public）版面補充：
- 若需求為品牌展示頁，允許採用 **split layout**（左視覺、右表單）。
- 左側可用粒子/光暈動效，但需提供小螢幕降級策略（mobile 隱藏或簡化）。
- 右側表單若未被要求卡片式，可直接採平面排版，避免額外容器造成視覺負擔。

**禁止**：inline style objects（除非是動態計算值）。

### 步驟 4E：文案與導航（多語系）

- **可見文案**：優先從 `messages/{locale}.json` 以 `getTranslations` / `useTranslations` 取字，**不**在 JSX 內寫死長句（與 starter 一致）。
- **導航語系**：導航名稱（Sidebar / Topbar Breadcrumbs）請使用 `useTranslations('nav')` 取字，避免使用錯誤的 domain（例如 `sidebar.journal` 其實不存在）。
- **Breadcrumbs**：頂部麵包屑直接顯示目前頁面名稱即可，不需硬編碼系統名稱（如 `{{PROJECT_TITLE}} / ...`）。
- **路由**：頁面路徑使用 **`next/link`**、`redirect` / `useRouter` from **`next/navigation`**（**URL 不含語系**，無需 locale 前綴）。
- **預設語系**：由 **`Accept-Language` + `NEXT_LOCALE` Cookie** 決定；手動切換沿用 starter 的 `POST /api/locale` + `router.refresh()` 模式。
- **新語系**：在 `src/i18n/routing.ts` 的 `locales` 與 `locale-negotiation.ts` 的協商規則中擴充，並新增對應 `messages/*.json`。
- **Shell 行為**：保留 starter 的側欄收合與 TopBar 使用者區（`UserMenu`）互動，不要在頁面中破壞其狀態與可用性。

## Phase 5：整合驗證

完成所有頁面後，驗證整體：

1. **導航連貫性**：從 Activity Diagram 的 STEP 序列驗證頁面間跳轉
2. **資料流一致性**：頁面 A 建立的資料能在頁面 B 正確顯示
3. **狀態同步**：操作（新增、刪除）後清單即時更新
4. **錯誤處理**：API 錯誤正確顯示（Feature 的 Error Scenario）
5. **Test Plan 對照**（若有）：每個測試步驟的預期結果可達成

管理頁額外驗證：
6. **視圖一致性**：同筆資料在 Grid/List 呈現的核心欄位一致
7. **操作一致性**：`⋯` 選單可在 Grid 與 List 都觸發 Edit/Delete；點擊選單外或開啟 Modal 後選單應關閉；**Delete 必須先經確認彈窗**再送 API
8. **模式一致性**：Modal 與 Dedicated Page 兩種新增/編輯流程都可完成同一業務結果
9. **跨頁一致性**：同群組頁面（如 ModuleA/ModuleB/Reports）在密度、留白、資訊層級上無明顯漂移
10. **預設載入一致性**：清單頁首次進入即有資料（或可解釋的空態），不出現「先按查詢才有資料」的反直覺流程
11. **契約一致性**：Frontend API client、MSW handlers、backend endpoint 對「可選查詢條件」的語義一致
12. **單筆／刪除路由**：若規格含刪除或依 ID 讀寫，確認執行中後端 OpenAPI 已暴露對應 `DELETE`/`PUT`/`GET` path（避免舊映像導致 404）。


## 注意事項

- **MSW 已就位**：開發階段所有 API 呼叫會被 MSW 攔截，返回 fixtures 資料。不需要真實後端。
- **不修改 MSW 層（預設）**：不要隨意在 `src/mocks/` 手改行為。若契約或 endpoint 變更，應透過 **`/aibdd-auto-frontend-msw-api-layer`** 重新產出或依專案流程對齊；與真後端整合時，MSW 與 `api.yml` 必須與後端路由一致。
- **真後端 404 與映像**：整合 Docker 時，API 映像未重建會導致路由落後程式庫；見步驟 **4B** 的 OpenAPI 檢查與重建指令。
- **視覺品質不能退化**：拆解後的 React 元件渲染結果必須與 layout.html 視覺一致或更好。
- **繁體中文產出**：所有 TODO 註解和文件使用繁體中文，但程式碼中的變數名和函式名使用英文。
