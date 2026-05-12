# SSOT 三角

本 skill 的所有產出都建立在這三條 SSOT 之上。**三角缺一不可**——任一缺漏就 fail-stop，不准強行猜內容。

## 三角定義

| 角 | 名稱 | 路徑變數（arguments.yml key） | 預設路徑 | 角色 |
|---|---|---|---|---|
| 🎨 | **設計 SSOT** | `UIUX_PEN_FILE` + `UIUX_PREVIEW_DIR` | `specs/frontend/uiux/user-journey.pen` + `specs/frontend/uiux/preview/` | 提供 frame 清單（含 node ID）、reusable component 對映表、PNG 截圖檔名 |
| 📜 | **API 契約 SSOT** | `API_SPEC_FILE` + `BACKEND_CONTRACTS_DIR` | `specs/backend/api.yml` + `specs/backend/contracts/` | 提供 endpoint × method × path × request schema × response schema × operation_id |
| 🧪 | **行為樣本 SSOT（參考用）** | `BACKEND_FEATURE_FILES_GLOB` | `specs/backend/packages/**/features/*.feature` | 提供 Scenario / Example / Outline 表格作為 MSW fixture 設計**靈感來源**，**非嚴格 1:1 對映** |

## 路徑解析優先序

1. **第一順位**：`.aibdd/arguments.yml` 內顯式設定的 key（`UIUX_PEN_FILE` / `API_SPEC_FILE` / `BACKEND_FEATURE_FILES_GLOB` 等）
2. **第二順位**：上表「預設路徑」欄
3. 三條任一不存在就 STOP，回報「三角 SSOT 缺漏」訊息

## frame 提取規則（從 .pen JSON）

讀 `.pen` 解析為 JSON 後，從 `document.children` 取 type==frame 的 top-level node。**排除**以下：

- `name` 以 `"Design System"` 開頭的 frame（那是元件展示間，不是使用者畫面）
- `placeholder == true` 的 frame（未完成設計）

每個保留的 frame 抽出：

```yaml
node_id: <pen node id>
name: <frame name, e.g. "01 Lobby">
width: <number>
height: <number>
preview_png: <UIUX_PREVIEW_DIR>/<derived filename>.png
```

PNG 檔名推導規則：
- 若 `${UIUX_PREVIEW_DIR}` 中存在以 frame name 前綴 + kebab-case 的 PNG（例：`01-lobby.png` 對應 frame `"01 Lobby"`），優先採用
- 否則 fallback 為 `<node_id>.png`
- 都不存在就在 task 內標 `(no preview, regenerate via export)`，**不要中斷整個流程**

## operation 提取規則（從 OpenAPI）

讀 `${API_SPEC_FILE}` 解析為 OpenAPI 文件後，flatten `paths` × `methods`。每個 operation 抽出：

```yaml
operation_id: <operationId, e.g. upsertRoomPlayerByCode>
method: <GET | POST | PUT | PATCH | DELETE>
path: <path template, e.g. /room-codes/{roomCode}/players/{playerId}>
request_schema_ref: <#/components/schemas/...>
response_schema_ref: <#/components/schemas/...>
feature_file_hint: <best-guess feature file by op-id-token-overlap, may be null>
```

`feature_file_hint` 是「猜一下」哪份 feature file 最相關（用 operation_id 跟 feature file 名稱做 token overlap），**僅供 task 文案標 hint 用，不會被當成硬綁定**。

## 三角整合的限制

- **設計 SSOT 不寫 API**：`.pen` 裡不會告訴你 endpoint 是什麼。
- **契約 SSOT 不寫 UI**：`api.yml` 不會告訴你哪一個畫面打哪一支 API。
- **樣本 SSOT 不是契約**：`feature` 檔的 Examples 是「行為樣本」，**不是** request/response schema 來源。schema 永遠從 contract 讀，**不從 feature 反推**。

整合三者的 mapping 是 Phase 2 SYNTHESIZE 的工作，不在這份 reference 內展開。
