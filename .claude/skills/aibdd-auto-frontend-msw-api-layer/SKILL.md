---
name: aibdd-auto-frontend-msw-api-layer
description: 前端 Stage 1：從 api.yml + discovery features 產出 Zod Schemas、Fixtures、MSW Handlers、API Client 函式。
user-invocable: true
---

# 角色

資料層建構者。從規格產出型別安全的 API 層，讓後續的 Gherkin 測試和元件實作都能直接引用。

---

# Entry 條件

啟動時先讀取 `specs/arguments.yml`，解析以下路徑變數（括號為 new-starter 的預設值）：

| 變數 | 說明 | new-starter 預設 | 無 src/ 專案範例 |
|------|------|---------|--------|
| `SRC_DIR` | 原始碼基礎目錄 | `src` | `""` (空) |
| `TYPES_DIR` | Zod schema 目錄 | `${SRC_DIR}/lib/types` | `lib/types` |
| `API_CLIENT_DIR` | API client 目錄 | `${SRC_DIR}/lib/api` | `lib/api` |
| `MSW_DIR` | MSW mock 目錄 | `${SRC_DIR}/mocks` | `mocks` |
| `HANDLERS_DIR` | MSW handlers 目錄 | `${MSW_DIR}/handlers` | `mocks/handlers` |

> 若 `arguments.yml` 不存在這些變數，詢問使用者後繼續。

---

# 輸入

| 來源 | 用途 |
|------|------|
| `${SPECS_ROOT_DIR}/api/api.yml` | schemas → Zod types、endpoints → handlers + client、error codes → 錯誤模擬、enums → 固定資料值 |
| `${SPECS_ROOT_DIR}/features/**/*.feature` | Given 步驟中的具體實體資料 → 寫實的 fixtures（後端 Given 提到的每個值都必須出現在 fixtures） |

---

# 已有基礎建設（勿覆寫）

以下檔案已存在，本階段只在標記處補充，不重建（路徑使用上方解析的變數）：

- `${API_CLIENT_DIR}/client.ts` — `apiClient<T>()`（exported）、`ApiClientError`（exported）
- `${API_CLIENT_DIR}/index.ts` — barrel re-export（在註解處補上新的 re-export）
- `${TYPES_DIR}/index.ts` — barrel re-export（在註解處補上新的 re-export）
- `${MSW_DIR}/browser.ts` — `setupWorker` + `initMocks()`
- `${HANDLERS_DIR}/index.ts` — handler 彙總（在註解處補上新的 handler）

---

# 產出物

## 1. Zod Schemas + 型別（`${TYPES_DIR}/{resource}.schema.ts`）

對 `api.yml` 中每個 `components/schemas`：
- 產生 Zod schema（enum 用 `z.enum()`，物件用 `z.object()`）
- 用 `z.infer<>` 推導 TypeScript 型別並 export
- 在 `${TYPES_DIR}/index.ts` 補上 re-export

## 2. 固定資料（`${MSW_DIR}/fixtures.ts`）

- 從 `@/lib/types` import 型別
- 產生 `mock{Entity}[]` 陣列，使用**來自 features 的具體資料**（不隨意編造）
- discovery features 的 Given 步驟中提到的每個實體/值都必須存在

## 3. MSW Handlers（`${HANDLERS_DIR}/{resource}.ts`）

對 `api.yml` 中每個端點：
- 產生一個 `http.{method}()` handler
- 正常路徑：回傳 fixtures，支援查詢參數篩選
- 錯誤路徑：對 api.yml 中**每個** error response code，加入對應分支
- 匹配 `client.ts` 的回應封套格式（`{ success, data }` 或 `{ success, error }`）
- 在 `${HANDLERS_DIR}/index.ts` 補上新增的 handler

## 4. API 客戶端函式（`${API_CLIENT_DIR}/{resource}.ts`）

對 `api.yml` 中每個端點：
- 產生型別化的非同步函式（命名 = `operationId`）
- 使用 `apiClient<T>()` from `${API_CLIENT_DIR}/client`
- 回傳型別與 Zod schema 推導一致
- 在 `${API_CLIENT_DIR}/index.ts` 補上 re-export

---

# 輸出結構

```
${TYPES_DIR}/
│   ├── {resource}.schema.ts   ← Zod schemas + z.infer 型別
│   └── index.ts               ← 補上 re-export（已有）
${API_CLIENT_DIR}/
│   ├── {resource}.ts          ← API 客戶端函式
│   └── index.ts               ← 補上 re-export（已有）
${MSW_DIR}/
│   ├── fixtures.ts            ← 型別化的模擬資料（已有空殼）
│   └── handlers/
│       ├── {resource}.ts      ← 按資源分的 handlers
│       └── index.ts           ← 補上 handler 彙總（已有空殼）
```

---

# 規則

- Fixtures 資料**必須來自** `${SPECS_ROOT_DIR}/features/` 的具體範例，不得憑空編造
- 每個 `api.yml` error response **必須**在 handler 中有對應分支
- Handler URL pattern 必須完全匹配 `api.yml` 的 path（含 path params）
- 不產生任何 UI 元件，此階段只處理資料層
- 不覆寫「已有基礎建設」中的檔案，僅在標記處補充
- **產出後校驗**：完成 Mock 生成或更新後，必須執行 `scripts/check-consistency.ts`，確保與 Feature 檔案 100% 同步。
- **後端掛鉤驗證**：產出的 Fixtures 必須與 `backend/app/models` 的字段類型進行邏輯比對（透過 aibdd-auto-migration-sync 協作）。
- **路徑自動探索 (Convention Mode)**：所有生成文件的路徑必須遵循 `aibdd-core` 中的 **路徑搜索啟發式 (Path Heuristics)**。優先尋找現有的 `src/mocks` 資料夾，嚴禁在不確認環境下建立冗餘目錄。

---

# 完成條件

- 所有 `api.yml` schemas 均有對應的 Zod schema 檔案
- 所有 `api.yml` endpoints 均有對應的 handler 和 client 函式
- 所有 error codes 均有 handler 分支
- `fixtures.ts` 的資料可追溯至 `features/` 的具體 Given 步驟
- **通過 `test:consistency` 校驗**：產出物必須通過一致性守衛，標記為 `STABILITY SECURED`。
- **全棧對齊**：所有 Zod 型別均與後端 API 響應結構一致，且無缺失字段。
