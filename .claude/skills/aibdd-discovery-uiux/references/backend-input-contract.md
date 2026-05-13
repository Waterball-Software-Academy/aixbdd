# Backend Input Contract

> 純 declarative — 規範 sibling backend boundary 的 spec artifacts 怎麼被 `aibdd-discovery-uiux` 消費。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 1。

---

## §1 BE 路徑解析規則

| 變數 | 來源 | 解析結果 |
|---|---|---|
| `UIUX_BACKEND_BOUNDARY_ID` | `${workspace_root}/.aibdd/arguments.yml` 頂層欄位 | 必填字串；指向 sibling backend boundary 的 id |
| `SPECS_ROOT_DIR` | `kickoff_path_resolve.py` 展開後 | `${workspace_root}/specs` |
| `$be_specs_dir` | `${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}` | sibling BE boundary 根目錄 |
| `$be_packages_dir` | `${$be_specs_dir}/packages/` | BE function package 根 |
| `$be_contracts_dir` | `${$be_specs_dir}/contracts/` | OpenAPI / GraphQL / 事件 schema |
| `$be_shared_dir` | `${$be_specs_dir}/shared/` | DSL / actor / common types |
| `$be_architecture_dir` | `${$be_specs_dir}/architecture/` | boundary.yml / component-diagram |

> **invariant**：sibling BE boundary 不得是當前 FE boundary 本身（即 `UIUX_BACKEND_BOUNDARY_ID != TLB.id`）。

---

## §2 必填輸入檔型

| 類別 | Glob | 形狀 | 缺檔處理 |
|---|---|---|---|
| BE features | `${$be_packages_dir}/**/*.feature` | Gherkin rule-only 或含 Examples | STOP — 引導使用者先在 BE 端跑 `/aibdd-discovery` |
| BE activities | `${$be_packages_dir}/**/activities/*.activity` | Activity DSL | STOP — 引導使用者先在 BE 端跑 `/aibdd-discovery` |
| BE contracts | `${$be_contracts_dir}/**/*.yml` ∨ `${$be_contracts_dir}/**/*.yaml` | OpenAPI 3.x / AsyncAPI / GraphQL schema / 自訂事件 schema | 缺檔不致命，但會降低 has-ui / no-ui 分類精度；記入 sourcing report |
| BE shared DSL | `${$be_shared_dir}/dsl.yml` ∨ `${$be_shared_dir}/dsl.md` | shared DSL L1-L4 | 缺檔不致命；無法 cross-reference `be_operation_binding.dsl_ref` |
| BE boundary metadata | `${$be_architecture_dir}/boundary.yml` | boundary spec | 缺檔不致命；用於 actor / role 推導 |

---

## §3 OpenAPI 解析慣例

| 概念 | OpenAPI 對應 | FE skill 用途 |
|---|---|---|
| BE operation | `paths.<route>.<method>.operationId`（或 method+route fallback） | operation_inventory 主鍵 |
| Operation actors | `security` 子段 + tags + `x-actors` 擴充欄位 | has-ui / no-ui 分類 input |
| Request shape | `requestBody.content.<mediaType>.schema` | UI form field 候選 |
| Response shape | `responses.<status>.content.<mediaType>.schema` | UI render content 候選 |
| Side effects | description + `x-side-effects` 擴充欄位 | side-effect feedback（toast / route）候選 |

> **fallback**：若 OpenAPI 缺 `operationId`，組合 `<method>:<path>` 作為 operation id；同樣方式適用於 GraphQL（`<root>:<fieldName>`）。

---

## §4 BE activity 解析慣例

| 概念 | `.activity` 對應 | FE skill 用途 |
|---|---|---|
| Activity actor | header `actor:` | actor whitelist filter（end-user / admin / system） |
| Action node | numbered step body | UI verb mapping 與 anchor 候選來源 |
| Decision node | `DECISION` block | userflow 分支與 error/edge state 推導來源 |
| Terminal node | `END` / `RETURN` | userflow terminal 對應 |

---

## §5 缺欄補齊優先序

當 BE truth 內部不一致或缺欄時的補齊順序：

1. OpenAPI / contracts 內的 explicit 標注（`x-actors` / `security`）
2. BE `.activity` 的 actor header
3. BE `.feature` 的 Background actor declaration
4. BE shared DSL 的 actor catalog

任一層級可填則停止往下找；全部缺則進 Seam A clarify-loop。

---

## §6 不在本檔範疇

- 任何「如何讀檔」「如何 walk glob」的 SOP — 屬 SKILL.md Phase 1 §5
- 任何「has-ui / no-ui 分類規則」 — 屬 [`be-to-fe-mapping.md`](be-to-fe-mapping.md)
- 任何「Rule 句型」 — 屬 [`verification-semantics-presets.md`](verification-semantics-presets.md)
- 任何「coverage 完整性」 — 屬 [`userflow-rule-coverage.md`](userflow-rule-coverage.md)
