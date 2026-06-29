---
name: aibdd-form-api-spec
description: >
  從推理包翻譯為 OpenAPI。負責 OpenAPI 語法規章 + 歸檔。
  切檔策略（單檔 / per-resource / per-module / per-boundary）由 Planner 透過 DELEGATE 參數指定，
  本 skill 不自決。不做跨 boundary 決策。
user-invocable: false
---

## §1 角色

Formulation skill。綁定 DSL = OpenAPI 3.x。被 `aibdd-service-contract-analysis` 與 `/aibdd-plan`（透過 boundary operation contract specifier）DELEGATE。

---

## §2 入口契約

接收推理包：

| 項目 | 內容 |
|------|------|
| M/D/C 變更集 | EndpointGroup / InteractionMode / ModuleSlice 的增刪改 |
| Axis 單位對應 | 推理包中每個 endpoint → OpenAPI path/method 的具體對應 |
| 退出狀態 | Reason 步是否完整通過 |
| `slice_list` | Planner 指定的切檔清單：每個 slice 的 `target_path` + `scope`（包含哪些 endpoint groups）。`target_path` 為 caller 提供之**相對於 `${CONTRACTS_DIR}` 的檔案路徑**。`target_path` 內**不得**含 `<<NN-functional-module>>` 借位子層；`${CONTRACTS_DIR}` 在 SSOT 已是 flat directory（見 `aibdd-core::ssot/spec-package-paths.md`），functional module 借位只允許出現在 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 子樹。`type` 亦不出現於 path — 由 `${BOUNDARY_YML}` `type` 欄位 SSOT。 |

**缺項**：推理包不完整或 `slice_list` 未指定 → 回退呼叫 Planner 補齊（白話文回報「推理包不完整」）。

---

## §3 Formulate SOP

1. **讀取 format reference**：`references/format-reference.md`（OpenAPI 3.x **語法合法**範例、狀態碼、型別）
2. **讀取行為 / 封裝規約**：`references/patterns/command-resource.md`（狀態遷移、命令封裝、讀模型、後端裁定邊界）
3. **讀取反模式**：`references/patterns/anti-patterns.md`（對照自查）
4. **依 slice_list 展開**：每個 slice 產出一個 OpenAPI 文件；共用 schema 放 `common.api.yml`
5. **填入 path + method**：從推理包的 endpoint → RESTful path + HTTP method 映射（命名細節見 `patterns/rest-naming.md`）
6. **錯誤與切檔**：`patterns/error-schema.md`、`patterns/modular-layout.md`
7. **$ref 跨檔引用**：依切檔策略寫入正確的 `$ref` 引用
8. **寫檔前 ASSERT**：每個 slice 的 `target_path` 不得含 `<<NN-functional-module>>` 借位子層；任一違反 → STOP 並回退 Planner 補正（白話文回報「target_path 違反 `${CONTRACTS_DIR}` flat 規約」）。
9. **寫檔**：依 slice 的 `target_path` 逐一寫出（落點＝`${CONTRACTS_DIR}` ⊕ `target_path`）。

---

## §4 DSL 最佳實踐

### 領域與狀態（優先於「路徑長相」）
- **禁止**將核心狀態遷移或規則裁定下放給客戶端 request body，除非推理包明示為測試／示意且與正式 API 分離（見 `command-resource.md`）。
- **避免**僅切狀態的 endpoint；**偏誤**：同一使用者意圖合併為單一命令，並以 **snapshot／GET** 滿足讀模型（細節見 `command-resource.md`、`anti-patterns.md`）。

### REST 命名
- path: 名詞複數或從屬資源（見 `patterns/rest-naming.md`）
- method: CRUD 與命令型 `POST`（見 `command-resource.md`）
- operationId: `<verb><Resource>` camelCase（`createOrder`）；**path 仍保持名詞導向**
- tag: 等於 EndpointGroup.group_id

### Error schema
- 統一使用 `ErrorResponse { message, code }`（見 `patterns/error-schema.md`）
- 放在 `common.api.yml#/components/schemas/ErrorResponse`

### 模組化 layout
- 切檔策略由 Planner 決定；本 skill 配合落地（見 `patterns/modular-layout.md`）
- `$ref` 引用語法嚴格遵循 OpenAPI 3.x 規範
- 每個 slice 的 `info.title` 反映 scope

---

## §5 匯報

以白話文 1–3 句匯報（依 `aibdd-core::planner-contract.md` §REPORT 匯報；不輸出 JSON / YAML）：

> Form API Spec 完成。產出 N 個 OpenAPI 檔案。

---

## §6 參考

- **references/format-reference.md**：合法 `responses` 形狀、狀態碼對照、型別推斷
- **references/patterns/command-resource.md**：狀態遷移、業務封裝、讀模型、命令型 POST 資源化
- **references/patterns/anti-patterns.md**：RPC 氣味、純狀態 API、204+無讀模型、誤放後端裁量欄
- **references/patterns/rest-naming.md**：path / method / operationId
- **references/patterns/error-schema.md**：`ErrorResponse` 與 4xx 分工
- **references/patterns/modular-layout.md**：common.api.yml、相對 `$ref`、slice `info`
