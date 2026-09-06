# Rule 1 - `techstack.md` 必須呈現高層技術堆疊總覽，而不是逐條重寫 research 決策

- Level: `MUST`
- `techstack.md` 的責任是總結本次 feature 最終採用的技術堆疊與主要工具分層，不是逐條重寫 `research.md` 中的 `Decision`、`Rationale` 與 `Alternatives considered`。
- 若某段內容已進入詳細取捨、逐條替代方案或長段理由說明，應保留在 `research.md`，而不是複製到 `techstack.md`。
- `techstack.md` 應讓後續規劃或實作能快速看懂「這次最後採用了哪些技術」。

## Good Example

- 這個例子是好的，因為它只保留最終採用結果與用途，不重寫詳細研究過程。

````md
### 後端

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| HTTP 框架 | `Express` | API 路由與伺服器處理 |
| 上傳處理 | `multer` | 多檔照片上傳 |
````

## Bad Example

- 這個例子是壞的，因為它把 `research.md` 的細部研究理由整段搬進來。

````md
### 後端

- `Express`：最小且成熟的 HTTP API 框架，優於 Koa、Fastify 與 Hono，因為...
- `multer`：選它而不是其他方案，理由如下...
````

# Rule 2 - `techstack.md` 必須包含高層分類、技術清單與用途欄位

- Level: `MUST`
- `techstack.md` 必須至少包含 `技術堆疊總覽` 與 `本次開發不引入的技術`。
- `技術堆疊總覽` 內的每個分類都必須使用相同欄位的表格，至少包含 `類別`、`採用技術`、`用途` 三欄。
- 若某個高層分類沒有內容，可刪除整個區段；但保留的分類必須維持相同欄位結構。

## Good Example

- 這個例子是好的，因為它保留了固定欄位與高層分類。

````md
## 技術堆疊總覽

### 前端

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 建置工具 | `Vite` | 本地開發與前端建置 |
````

## Bad Example

- 這個例子是壞的，因為它缺少固定欄位，後續難以穩定比對。

````md
## 技術堆疊總覽

- `Vite`
- `Express`
- `Prisma`
````

# Rule 3 - `techstack.md` 應只列最終採用與明確排除的技術

- Level: `SHOULD`
- `techstack.md` 應聚焦本次 feature 最終採用的技術，以及明確決定本次不引入的技術。
- 不應把尚未拍板、僅短暫評估過、或已被排除但沒有進入最終邊界的候選方案混進採用清單。
- 若某個技術只是研究過但未採用，應優先留在 `research.md` 的 `Alternatives considered`，除非它屬於明確的「本次不引入的技術」。

## Good Example

- 這個例子是好的，因為它只列最終採用與明確排除項。

````md
## 本次開發不引入的技術

- `React` 或其他前端框架
- 第三方拖放套件（如 `SortableJS`）
````

## Bad Example

- 這個例子是壞的，因為它把尚未拍板的評估項也塞進採用清單。

````md
### 前端

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| UI 技術 | `React?` / `原生 JavaScript?` | 還在考慮 |
````

# Rule 4 - `techstack.md` 的 `測試與驗證` 必須看得見各端 BDD techstack

- Level: `MUST`
- `測試與驗證` 不可只列一個通用測試框架。每個已確認存在的端，都要寫出該端的 BDD techstack 與用途。
- 測試策略沒被使用者改判時，各端應寫成 E2E，不得把「完整瀏覽器 E2E」或後端 E2E 列進 `本次開發不引入的技術`。
- 前端 webapp 的 runner 與後端 API 的 runner 分列。用途要寫它跑的是哪一端的 Gherkin，以及打的是畫面還是 API／權威狀態。

## Good Example

- 這個例子是好的，因為各端 BDD techstack 都看得到，而且預設是 E2E。

````md
### 測試與驗證

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 前端 BDD techstack | `Playwright` | webapp E2E，跑前端 Gherkin |
| 後端 BDD techstack | `behave` | 後端 E2E，跑後端 Gherkin，驗 API 與權威狀態 |
````

## Bad Example

- 這個例子是壞的，因為看不出各端 runner，還把 E2E 排除掉。

````md
### 測試與驗證

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| API 測試 | `vitest` | 測試執行框架 |
| 手動驗證 | `quickstart.md` | 前端操作 |

## 本次開發不引入的技術

- 完整瀏覽器 E2E 測試框架
````

# Rule 5 - `techstack.md` 的分類與列舉粒度應服務後續 handoff

- Level: `SHOULD`
- `techstack.md` 的分類應以後續規劃或實作最容易接手的高層視角組織，例如前端、後端、資料與媒體處理、測試與驗證。
- 若某個分類只有 1 列但仍能清楚表達責任，可保留；若某些列其實屬於同一用途，應避免過度切碎。
- 目標是快速建立全局 stack 視圖，而不是把所有 dependency 原封不動做成套件清單。

## Good Example

- 這個例子是好的，因為分類與粒度都服務後續 handoff。

````md
### 測試與驗證

| 類別 | 採用技術 | 用途 |
| --- | --- | --- |
| 前端 BDD techstack | `Playwright` | webapp E2E |
| 後端 BDD techstack | `behave` | 後端 E2E |
````

## Bad Example

- 這個例子是壞的，因為它把可讀的技術總覽退化成原始 dependency dump。

````md
dependencies:
- vite
- express
- multer
- prisma
- exifr
- sharp
````
