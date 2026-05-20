# Spec Package Paths

AIBDD skills 的 **spec 檔案路徑慣例 SSOT**。路徑模型以 **`/aibdd-kickoff` 產物** 為準（見 `aibdd-kickoff/assets/templates/arguments.template.yml`、`.java-e2e.yml`、`.nextjs-playwright.yml` 三檔；變數預設值與占位符語意逐字寫在 template 註解中）。

One specs root = one boundary。`${SPECS_ROOT_DIR}` 就是該 boundary 的 truth root。`${BOUNDARY_YML}` 內的 `id` 為語意 tag，不對應 filesystem 子目錄。

---

## Ground truth

1. **`${SPECS_ROOT_DIR}`** — 規格工作區根（例：`specs`），同時是 boundary truth root。內含 `architecture/boundary.yml`、`boundary-map.yml`、`contracts/`、`data/`、`shared/`、`packages/`、`plans/`、`test-strategy.yml`。
2. **`${BOUNDARY_YML}`** — 單一 boundary 宣告（top-level `id` / `level` / `role` / `type` / `description`，非 array）；`id` 用作 component diagram / package metadata 的語意 tag，不用於展開檔案系統路徑。
3. **`TRUTH_FUNCTION_PACKAGE` / `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` / `TRUTH_TEST_PLAN_DIR` / `BOUNDARY_PACKAGE_DSL`** — 借位（slot）形態；kickoff 寫入 `<<NN-functional-module>>` slot literal，runtime 同時存在多個 functional module instance，yaml 不指任一 active。各 skill 由 caller-context 取得當前 functional module slug，`/aibdd-discovery` 只在 filesystem 建 `NN-<slug>/` 目錄，不改寫 yaml。
4. **`CURRENT_PLAN_PACKAGE`** — 借位（slot）形態；kickoff 寫入 `<<NNN-plan-slug>>` slot literal，runtime 同時存在多個 plan package instance。caller 在呼叫 plan / tasks / implement 等 skill 時透過 CLI arg 或 caller payload 指定當前 plan slug，arguments.yml 不追蹤 active。
5. **符號類型** — `${VAR}` 是 interpolation（一對一可 resolve）；`<<X>>` 是 slot literal（一對多並存，不可 resolve），須由 caller-context override 才能用。Interpolation 必須迭代展開至穩定；slot literal 不展開、由 caller 提供具體值。

---

## Resolved directory variables（canonical）

下列變數名與 `arguments.yml` 一致；**實體路徑** = 展開後的字串（相對於 repo / 專案根）。

| Variable | Composition rule（與 kickoff 對照） |
|---|---|
| `${PLAN_PACKAGES_DIR}` | `${SPECS_ROOT_DIR}/plans` |
| `${CURRENT_PLAN_PACKAGE}` | `${PLAN_PACKAGES_DIR}/<<NNN-plan-slug>>` — 借位（slot），由 caller-context 提供 slug |
| `${PLAN_SPEC}` | `${CURRENT_PLAN_PACKAGE}/spec.md` |
| `${PLAN_MD}` | `${CURRENT_PLAN_PACKAGE}/plan.md` |
| `${PLAN_REPORTS_DIR}` | `${CURRENT_PLAN_PACKAGE}/reports` |
| `${PLAN_COVERAGE_REPORT_DIR}` | `${PLAN_REPORTS_DIR}/coverage` |
| `${PLAN_IMPLEMENTATION_DIR}` | `${CURRENT_PLAN_PACKAGE}/implementation` |
| `${PLAN_SEQUENCE_DIR}` | `${PLAN_IMPLEMENTATION_DIR}/sequences` |
| `${PLAN_INTERNAL_STRUCTURE}` | `${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd` |
| `${CLARIFY_DIR}` | `${CURRENT_PLAN_PACKAGE}/clarify` |
| `${TRUTH_ARCHITECTURE_DIR}` | `${SPECS_ROOT_DIR}/architecture` |
| `${BOUNDARY_YML}` | `${TRUTH_ARCHITECTURE_DIR}/boundary.yml` |
| `${BOUNDARY_MAP_FILE}` | `${SPECS_ROOT_DIR}/boundary-map.yml`（由 `/aibdd-plan` 寫） |
| `${TRUTH_BOUNDARY_ROOT}` | `${SPECS_ROOT_DIR}` |
| `${TRUTH_BOUNDARY_SHARED_DIR}` | `${TRUTH_BOUNDARY_ROOT}/shared` |
| `${TRUTH_BOUNDARY_PACKAGES_DIR}` | `${TRUTH_BOUNDARY_ROOT}/packages` |
| `${CONTRACTS_DIR}` | `${TRUTH_BOUNDARY_ROOT}/contracts` — boundary operation contract directory; concrete file format is chosen by the boundary type profile's operation contract specifier |
| `${DATA_DIR}` | `${TRUTH_BOUNDARY_ROOT}/data` — boundary state truth directory; concrete file format is chosen by the boundary type profile's state specifier |
| `${BOUNDARY_SHARED_DSL}` | `${TRUTH_BOUNDARY_SHARED_DIR}/dsl.yml` |
| `${TEST_STRATEGY_FILE}` | `${TRUTH_BOUNDARY_ROOT}/test-strategy.yml` |

**Function package 借位（kickoff 以 slot literal 寫入；caller-context 在 invoke skill 時提供具體 slug；`/aibdd-discovery` 不改寫 yaml）**

| Variable | Composition rule |
|---|---|
| `${TRUTH_FUNCTION_PACKAGE}` | `${TRUTH_BOUNDARY_PACKAGES_DIR}/<<NN-functional-module>>` |
| `${ACTIVITIES_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/activities` |
| `${FEATURE_SPECS_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/features` |
| `${BOUNDARY_PACKAGE_DSL}` | `${TRUTH_FUNCTION_PACKAGE}/dsl.yml` |
| `${TRUTH_TEST_PLAN_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/test-plan` |

Accepted behavior truth（Activity / Discovery rule-only feature）落於 caller-context override 過的 **`FEATURE_SPECS_DIR`** / **`ACTIVITIES_DIR`**；boundary shared DSL 仍由 **`${TRUTH_BOUNDARY_SHARED_DIR}`** 承載。

---

## Rules

- 禁止把 `${SPECS_ROOT_DIR}/features`、`${SPECS_ROOT_DIR}/activities` 當成 normative Discovery 落點。Function-level features／activities 僅落在 `${TRUTH_FUNCTION_PACKAGE}/features|activities`。
- 禁止在路徑中插入 `boundary.id` 子目錄層；`${TRUTH_BOUNDARY_ROOT}` 直接展開為 `${SPECS_ROOT_DIR}`。
- `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` 從 caller-context 取得當前 functional module slug 後展開借位；script gate／formulation delegation 在收到 caller-context 提供的 slug 後才視為已定錨。
- Skills 必須能讀 `${BOUNDARY_YML}`（或等價的已解析 `TRUTH_BOUNDARY_ROOT`），才能決定檔案寫入與 quality gate 掃描路徑。
- **Acceptance / Behave** 可執行 `.feature` 路徑由 **`BDD_CONSTITUTION_PATH`** 與 `PY_TEST_FEATURES_DIR` 定義（通常 `tests/features/`），與上表 Discovery 規格路徑分離。
- Boundary operation contract truth 的**目錄**固定由 `${CONTRACTS_DIR}` 決定；operation contract 的**格式與 formulation skill** 以 `${BOUNDARY_YML}` 所宣告 `type` 對應之 `aibdd-core/assets/boundaries/<type>/profile.yml` 內 `operation_contract_specifier` 為準（例：`web-service` → OpenAPI，經 `/aibdd-form-api-spec`）。Planner 不得假設 `${CONTRACTS_DIR}` 內一定是 ad hoc `operations:` YAML。
- Boundary state truth 的**目錄**固定由 `${DATA_DIR}` 決定；state 的**格式與 formulation skill** 以上述同檔之 `state_specifier` 為準（例：`web-service` → DBML，經 `/aibdd-form-entity-spec`）。Planner 不得假設 `${DATA_DIR}` 內一定是 YAML。

---

## Cross-reference

- Mermaid diagram 檔名副檔名（`*.class.mmd` / `*.sequence.mmd`）：[`diagram-file-naming.md`](diagram-file-naming.md)
- Boundary profile（`operation_contract_specifier`／`state_specifier`）與同目錄 `step-classification.yml`、`plugin-contract.md`：見 `aibdd-core` SKILL.md §2 ASSETS（`assets/boundaries/<type>/`）
- 欄位預設值與占位符語意：`aibdd-kickoff::assets/templates/arguments.template.yml`（python_e2e）、`.java-e2e.yml`、`.nextjs-playwright.yml`；每個 key 旁邊的 `#` 註解即為 SSOT 說明。
- Feature 檔名軸（§5.1）與 bdd-stack 憲法樹：`${BDD_CONSTITUTION_PATH}`（專案內預設 `.aibdd/bdd-stack/project-bdd-axes.md`）；runner／step／fixture 細節見 `.aibdd/bdd-stack/*.md`
