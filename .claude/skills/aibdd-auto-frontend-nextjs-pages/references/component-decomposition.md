# 元件拆解策略

## 目標

將 `layout.html` 靜態原型拆解為 React 元件樹，同時**保證視覺保真**。

## 拆解流程

```
1. 掃描 layout.html 結構 → 識別 UI 區塊
2. 分類 UI 區塊 → Shell / Page / Domain / UI
3. 提取共用元件 → 跨頁面重複的區塊
4. 建立元件樹 → 確定 props 與資料流
5. 遷移樣式 → inline style → CSS Modules / Tailwind
```

## 步驟 1：識別 UI 區塊

掃描 `layout.html`，依 HTML 結構識別以下區塊類型：

| HTML 特徵 | UI 區塊類型 | 範例 |
|-----------|------------|------|
| `<nav>`, `<aside>`, 固定側欄 | Sidebar | 左側導航列 |
| `<header>`, 頂部列 | TopBar / Header | 頂部使用者資訊列 |
| `<table>`, `<thead>`, `<tbody>` | DataTable | 資料清單表格 |
| `<form>`, `<input>`, `<select>` | Form | 新增 / 編輯表單 |
| `<dialog>`, `.modal`, overlay 結構 | Modal / Dialog | 確認刪除對話框 |
| `.card`, 獨立資訊區塊 | Card | 統計卡片、摘要卡片 |
| `<button>`, `<a>` 操作區域 | ActionBar / Toolbar | 批次操作列 |
| 麵包屑 / 分頁器 | Navigation | Breadcrumb, Pagination |
| 空狀態插圖 / Loading 動畫 | StateDisplay | Empty, Loading, Error |

## 步驟 2：分類元件層級

將識別出的 UI 區塊分為四個層級：

### Shell 層（`src/app/(protected)/layout.tsx`）

全站共用的外殼結構，包含：
- Sidebar（側邊導航）
- TopBar（頂部列）
- Content area（內容區域佔位）

**判定規則**：在 layout.html 中**所有頁面都出現**的固定結構 → Shell 層。

### Page 層（`src/app/(protected)/**/page.tsx`）

每個路由對應的頁面元件，為該頁面的容器：
- 組合該頁面需要的 Domain 元件和 UI 元件
- 處理資料獲取（Server Component）或狀態管理（Client Component）
- 傳遞 props 給子元件

### Domain 層（`src/components/domain/`）

具有業務語意的複合元件：

```
RecordForm         — 記錄表單（新增 / 編輯共用）
RecordTable        — 記錄清單表格（含搜尋、篩選）
ProjectCard      — 專案摘要卡片
StageTimeline    — 階段進度時間軸
ImportDialog     — 匯入檔案對話框
DeleteConfirm    — 刪除確認對話框
```

**判定規則**：元件名稱含業務實體名詞（Record, Project, Item...）→ Domain 層。

### UI 層（`src/components/ui/`）

無業務語意的通用 UI 元件：

```
Button           — 按鈕（variant: primary / secondary / danger）
Input            — 文字輸入框
Select           — 下拉選擇
Table            — 通用表格容器
Modal            — 通用 Modal 容器
Toast            — 通知訊息
Pagination       — 分頁器
SearchBar        — 搜尋框
EmptyState       — 空狀態提示
LoadingSpinner   — 載入中動畫
```

**判定規則**：元件可在不同業務場景中複用，不含特定業務邏輯 → UI 層。

## 步驟 3：提取共用元件

掃描 layout.html 中**重複出現的 UI 模式**：

### 識別方式

1. **相同 HTML 結構**：兩個頁面區塊的 DOM 結構相似度 > 80%
2. **相同 CSS class**：使用相同的 class name 或相似的 inline style
3. **相同互動行為**：點擊、hover、展開等互動模式相同

### 提取原則

```
出現 1 次 → 保留在 Page 層，不提取
出現 2 次 → 提取為 Domain 元件（若含業務語意）或 UI 元件
出現 3+ 次 → 必須提取為 UI 元件
```

### 已知共用元件

以下元件已由 Walking Skeleton 提供，**不要重複建立**：

```
src/components/MSWProvider.tsx   — MSW 初始化
src/components/Sidebar.tsx       — 側邊導航（可能需要擴充導航項目）
src/components/TopBar.tsx        — 頂部列
src/components/Toast.tsx         — Toast 通知
```

擴充已有元件時，保留原有 API，新增 props 而非修改。

## 步驟 4：建立元件樹

產出每個頁面的元件組成圖：

```
/records（記錄清單頁）
├── (protected)/layout.tsx
│   ├── Sidebar
│   └── TopBar
└── page.tsx（RecordsPage）
    ├── SearchBar          ← UI 層
    ├── RecordTable        ← Domain 層
    │   ├── Table          ← UI 層
    │   └── Pagination     ← UI 層
    ├── ImportDialog       ← Domain 層
    │   └── Modal          ← UI 層
    └── DeleteConfirm      ← Domain 層
        └── Modal          ← UI 層
```

### Props 設計原則

1. **資料向下**：父元件獲取資料，透過 props 傳給子元件
2. **事件向上**：子元件透過 callback props 通知父元件（`onSubmit`, `onDelete`, `onSearch`）
3. **型別來自 Zod**：props 的型別直接使用 `src/lib/types/` 下的 Zod infer type

```typescript
// Domain 業務元件範例 (RecordTable.tsx)
interface RecordTableProps {
  records: RecordResponse[]        // 型別來自 Zod schema
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  isLoading: boolean
}
```

## 步驟 5：樣式遷移

### 遷移策略

從 layout.html 提取樣式，按以下優先順序遷移：

**1. Design Tokens → CSS 變數（`globals.css`）**

layout.html 中反覆出現的顏色、字體大小、間距等：

```css
/* globals.css */
:root {
  --color-primary: #3b82f6;
  --color-danger: #ef4444;
  --radius-md: 8px;
  --spacing-page: 24px;
}
```

**2. 元件樣式 → Tailwind classes（優先）或 CSS Modules**

```tsx
// Tailwind（優先）
<button className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary/90">

// CSS Modules（當 Tailwind 不足時）
import styles from './LeadTable.module.css'
<table className={styles.table}>
```

**3. 動態樣式 → inline style（僅限動態計算值）**

```tsx
// 唯一允許 inline style 的場景
<div style={{ width: `${progress}%` }}>
```

### 禁止項目

- 不使用 `styled-components` 或 `emotion`
- 不使用固定的 inline style objects（`style={{ color: 'red' }}`）
- 不使用全域 CSS class（除了 `globals.css` 中的 CSS 變數）

## 視覺保真驗證

拆解完成後，進行視覺對照：

1. 將 layout.html 在瀏覽器中開啟，截圖作為基準
2. 將拆解後的 React 頁面在 `npm run dev` 中開啟，截圖比對
3. 逐項檢查：
   - 字體大小、粗細、顏色一致
   - 間距、對齊、佈局一致
   - 圖示、圖片位置一致
   - 互動狀態（hover、focus、active）一致
4. 不一致的地方立即修正，不留到後續 Phase
