---
name: aibdd-form-api-spec
description: >
  從推理包翻譯為 OpenAPI (.yml)。負責 OpenAPI 語法規章 + 歸檔。
  切檔策略（單檔 / per-resource / per-module / per-boundary）由 Planner 透過 DELEGATE 參數指定，
  本 skill 不自決。不做跨 boundary 決策。
user-invocable: false
---

## §1 角色

Formulation skill。綁定 DSL = OpenAPI 3.x (.yml)。被 `aibdd-service-contract-analysis` 與 `/aibdd-plan`（透過 boundary operation contract specifier）DELEGATE。

---

## §2 入口契約

接收推理包：

| 項目 | 內容 |
|------|------|
| M/D/C 變更集 | EndpointGroup / InteractionMode / ModuleSlice 的增刪改 |
| Axis 單位對應 | 推理包中每個 endpoint → OpenAPI path/method 的具體對應 |
| CiC 記號清單 | 便條紙（GAP / ASM / BDY / CON）+ 錨點 |
| 退出狀態 | Reason 步是否完整通過 |
| `slice_list` | Planner 指定的切檔清單：每個 slice 的 `target_path`（依 boundary v2 composition path，如 `<function_module>/<boundary-id>/api.yml` 或 `<function_module>/<boundary-id>/api/<resource>.yml`；`type` 不出現於 path — 由 boundary.yml `type` 欄位 SSOT）+ `scope`（包含哪些 endpoint groups） |

**缺項**：推理包不完整或 `slice_list` 未指定 → 回退呼叫 Planner 補齊（白話文回報「推理包不完整」）。

---

## §3 Formulate SOP

1. **讀取 format reference**：`references/format-reference.md`（OpenAPI 3.x 語法）
2. **依 slice_list 展開**：每個 slice 產出一個 OpenAPI YAML；共用 schema 放 `common.yml`
3. **填入 path + method**：從推理包的 endpoint → RESTful path + HTTP method 映射
4. **套用 patterns**：讀 `references/patterns/`（rest-naming / error-schema / modular-layout）
5. **$ref 跨檔引用**：依切檔策略寫入正確的 `$ref` 引用
6. **保留 CiC**：推理包中的便條紙 inline 到 OpenAPI 的 `x-cic` extension 或 `description`
7. **寫檔**：依 slice 的 `target_path` 逐一寫出

---

## §4 DSL 最佳實踐

### REST 命名
- path: 名詞複數（`/api/v1/orders`）
- method: CRUD → HTTP mapping（GET / POST / PUT / PATCH / DELETE）
- operationId: `<verb><Resource>` camelCase（`createOrder`）
- tag: 等於 EndpointGroup.group_id

### Error schema
- 統一使用 `ErrorResponse { message, code }`
- 放在 `common.yml#/components/schemas/ErrorResponse`

### 模組化 layout
- 切檔策略由 Planner 決定；本 skill 配合落地
- `$ref` 引用語法嚴格遵循 OpenAPI 3.x 規範
- 每個 slice 的 `info.title` 反映 scope

---

## §5 匯報

以白話文 1–3 句匯報（依 `aibdd-core::planner-contract.md` §REPORT 匯報；不輸出 JSON / YAML）：

> Form API Spec 完成。產出 N 個 OpenAPI .yml 檔案。{若有便條紙則加「尚有 N 張便條紙待釐清」；無則省略}

---

## §6 參考

- **format-reference.md**：OpenAPI 3.x 核心 / schema / security / $ref
- **patterns/rest-naming.md**：path / method / status code 最佳實踐
- **patterns/error-schema.md**：error response 統一結構
- **patterns/modular-layout.md**：多檔組織 / $ref / lint
- **anti-patterns.md**：path 動詞化 / 不一致錯誤格式 / $ref 失效
