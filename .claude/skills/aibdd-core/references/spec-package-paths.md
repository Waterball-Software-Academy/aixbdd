# Spec Package Paths

AIBDD skills 的 **spec 檔案路徑慣例 SSOT**。路徑模型以 **`/aibdd-kickoff` 產物** 為準（見 `aibdd-kickoff/references/convention-mapping.md`），**不是** PF-13 扁平 `specs/features` 單根目錄。

---

## Ground truth

1. **`${SPECS_ROOT_DIR}`** — 規格工作區根（例：`specs`）。內含 `arguments.yml`、plan package、`architecture/boundary.yml`、依 kickoff 展開的 boundary truth 子樹。
2. **`${BOUNDARY_YML}`** — 唯一 boundary 清單；下游以 **kickoff 建立的該 boundary** 的 `id` 替換 arguments 中的 `<boundary>`。
3. **`TRUTH_FUNCTION_PACKAGE` / `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR`** — **非 kickoff ground truth**。Kickoff-only `arguments.yml` 可省略或僅以註解佔位；必須在 **`/aibdd-discovery`** 完成 sourcing 並選定 `NN-<功能模組描述>` 後 **late-bind**，才視為已定錨。
4. **Placeholder 展開** — `arguments.yml` 內的值可含 `${VAR}`；必須迭代展開至穩定，再替換 `<boundary>`。

---

## Resolved directory variables（canonical）

下列變數名與 `arguments.yml` 一致；**實體路徑** = 展開後的字串（相對於 repo / 專案根）。

| Variable | Composition rule（與 kickoff 對照） |
|---|---|
| `${PLAN_PACKAGES_DIR}` | `${SPECS_ROOT_DIR}` |
| `${CURRENT_PLAN_PACKAGE}` | `${PLAN_PACKAGES_DIR}/<NNN-slug>` |
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
| `${TRUTH_BOUNDARY_ROOT}` | `${SPECS_ROOT_DIR}/<boundary>` → `<boundary>` = `boundaries[0].id`（kickoff 單一 boundary 契約） |
| `${TRUTH_BOUNDARY_SHARED_DIR}` | `${TRUTH_BOUNDARY_ROOT}/shared` |
| `${TRUTH_BOUNDARY_PACKAGES_DIR}` | `${TRUTH_BOUNDARY_ROOT}/packages` |
| `${ACTORS_DIR}` | `${TRUTH_BOUNDARY_ROOT}/actors` |
| `${CONTRACTS_DIR}` | `${TRUTH_BOUNDARY_ROOT}/contracts` — boundary operation contract directory; concrete file format is chosen by the boundary type profile's operation contract specifier |
| `${DATA_DIR}` | `${TRUTH_BOUNDARY_ROOT}/data` — boundary state truth directory; concrete file format is chosen by the boundary type profile's state specifier |
| `${BOUNDARY_SHARED_DSL}` | `${TRUTH_BOUNDARY_SHARED_DIR}/dsl.yml` |
| `${TEST_STRATEGY_FILE}` | `${TRUTH_BOUNDARY_ROOT}/test-strategy.yml` |

**Plan-cycle late-bind（`/aibdd-discovery` 寫入 `arguments.yml` 後才可機械解析）**

| Variable | Composition rule |
|---|---|
| `${TRUTH_FUNCTION_PACKAGE}` | `${TRUTH_BOUNDARY_PACKAGES_DIR}/NN-<功能模組描述>` |
| `${ACTIVITIES_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/activities` |
| `${FEATURE_SPECS_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/features` |
| `${BOUNDARY_PACKAGE_DSL}` | `${TRUTH_FUNCTION_PACKAGE}/dsl.yml` |
| `${TRUTH_TEST_PLAN_DIR}` | `${TRUTH_FUNCTION_PACKAGE}/test-plan` |

Legacy boundary-root behavior folders are not canonical. Accepted behavior truth（Activity / Discovery rule-only feature）**僅能在** **`TRUTH_FUNCTION_PACKAGE` late-bind 之後**，落於對應的 **`FEATURE_SPECS_DIR`** / **`ACTIVITIES_DIR`**；boundary shared DSL 仍由 **`${TRUTH_BOUNDARY_SHARED_DIR}`** 承載。

---

## Rules

- **禁止**把 `${SPECS_ROOT_DIR}/features`、`${SPECS_ROOT_DIR}/activities`、或 boundary root `features/` 當成 normative Discovery 落點。
- **`FEATURE_SPECS_DIR` / `ACTIVITIES_DIR`** 僅在目標 **`TRUTH_FUNCTION_PACKAGE`** 已定錨並寫回 `arguments.yml` 後，才對 script gate／formulation delegation 視為必填。
- Skills **必須**能讀 `${BOUNDARY_YML}`（或等價的已解析 `TRUTH_BOUNDARY_ROOT`），才能決定檔案寫入與 quality gate 掃描路徑。
- **Acceptance / Behave** 可執行 `.feature` 路徑由 **`BDD_CONSTITUTION_PATH`** 與 `PY_TEST_FEATURES_DIR` 定義（通常 `tests/features/`），與上表 Discovery 規格路徑分離。
- Boundary operation contract truth 的**目錄**固定由 `${CONTRACTS_DIR}` 決定；operation contract truth 的**格式與 formulation skill** 由 `aibdd-core::boundary-profile-contract.md` 解析 boundary `type` 後決定（例如 `web-service` → OpenAPI via `/aibdd-form-api-spec`）。Planner 不得假設 `${CONTRACTS_DIR}` 內一定是 ad hoc `operations:` YAML。
- Boundary state truth 的**目錄**固定由 `${DATA_DIR}` 決定；state truth 的**格式與 formulation skill** 由 `aibdd-core::boundary-profile-contract.md` 解析 boundary `type` 後決定（例如 `web-service` → DBML via `/aibdd-form-entity-spec`）。Planner 不得假設 `${DATA_DIR}` 內一定是 YAML。

---

## Cross-reference

- Mermaid diagram 檔名副檔名（`*.class.mmd` / `*.sequence.mmd`）：[`diagram-file-naming.md`](diagram-file-naming.md)
- Boundary profile / state specifier：[`boundary-profile-contract.md`](boundary-profile-contract.md)
- 欄位預設值與占位符語意：`aibdd-kickoff::references/convention-mapping.md`
- Feature 檔名軸（§5.1）與 bdd-stack 憲法樹：`${BDD_CONSTITUTION_PATH}`（專案內預設 `.aibdd/bdd-stack/project-bdd-axes.md`）；runner／step／fixture 細節見 `.aibdd/bdd-stack/*.md`
