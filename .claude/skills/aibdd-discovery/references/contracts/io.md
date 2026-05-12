# Discovery — I/O Contract

本 Planner 的 reads / writes / config 精確定義。Planner 只透過這裡宣告的 artifact 與世界溝通。

> **路徑規約（SSOT）**：以 **`/aibdd-kickoff` 產出的 `.aibdd/arguments.yml` + `architecture/boundary.yml`** 為準。  
> **`TRUTH_FUNCTION_PACKAGE` / `${FEATURE_SPECS_DIR}`**：僅在未 early-bind kickoff legacy 情形下才不存在於 `arguments.yml`；`/aibdd-discovery` Phase 2 必須將其 **late-bind** 後再行 Activity / formulation。  
> **禁止**假設 Discovery artifacts 落在 `${SPECS_ROOT_DIR}/activities`、`${SPECS_ROOT_DIR}/features`、boundary root `features/`，或任何舊扁平根下。

## §Reads

| 來源 | 內容 | 必要性 |
|------|------|-------|
| User raw input | 需求 idea（text / 截圖 / 現有文件引用） | 必要 |
| `aibdd-core::spec-package-paths.md` | kickoff boundary-aware 路徑慣例（LOAD） | 必要 |
| `aibdd-core::atomic-rule-definition.md` | Atomic rule 判定準則（LOAD） | 必要 |
| `aibdd-core::report-contract.md` | Planner 匯報與 user-facing message style 規範（LOAD） | 必要 |
| `${AIBDD_ARGUMENTS_PATH}` | 路徑變數與 `${BOUNDARY_YML}` 指標 | 必要 |
| `${BOUNDARY_YML}`（由 arguments 展開） | 唯一 kickoff boundary 的 `id` / scope | 必要 |
| `${TRUTH_BOUNDARY_ROOT}/actors/` | target boundary actor catalog truth | 有才讀 |
| `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml` | target boundary topology / rule dispatch / dependency / persistence truth | 有才讀 |
| `${TRUTH_BOUNDARY_ROOT}/contracts/` | provider operation contract truth | 有才讀 |
| `${TRUTH_BOUNDARY_ROOT}/data/` | domain entities / persistence / state truth | 有才讀 |
| `${TRUTH_BOUNDARY_ROOT}/shared/dsl.yml` | boundary shared DSL mapping truth（YAML registry） | 有才讀 |
| `${TRUTH_BOUNDARY_ROOT}/test-strategy.yml` | dependency edge test strategy truth | 有才讀 |
| `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/activities/*${ACTIVITY_EXT}` | existing accepted Activity truth across function packages | 有才讀 |
| `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/features/**/*.feature` | existing accepted rule / behavior truth across function packages | 有才讀 |
| `${TRUTH_FUNCTION_PACKAGE}/dsl.yml` | target function package local DSL truth | 有才讀 |
| `${SPECS_ROOT_DIR}/.actors.yml` | Actor allow-list / block-list 覆寫（與 `check_actor_legality.py` 一致） | 有才讀 |

## §Writes（一律透過 DELEGATE）

| artifact pattern | DELEGATE 目標 skill | 備註 |
|------------------|----------------------|------|
| `${ACTIVITIES_DIR}/*${ACTIVITY_EXT}` | `/aibdd-form-activity` | Activity Diagrams |
| `${FEATURE_SPECS_DIR}/<sub-domain>/*.feature` | `/aibdd-form-feature-spec` | Rules only、`@ignore`、無 Examples |

## §Writes（Discovery 自身）

| artifact pattern | Owner | 備註 |
|------------------|-------|------|
| `${PLAN_REPORTS_DIR}/discovery-sourcing.md` | `/aibdd-discovery` | evidence matrix + impact scope report；只放 pointer / evidence pointer / reason / confidence / impact scope / gap / use_in_discovery |
| `${PLAN_SPEC}` | `/aibdd-discovery` | `Discovery Sourcing Summary` + report pointer；不得放完整 matrix、truth copy、delta / diff |

## §Config

路徑變數由 **`${AIBDD_ARGUMENTS_PATH}`** 宣告；Planner **不得**在 plugin 層硬編替代值取代 kickoff。機械展開可委派：

`python3 .claude/skills/aibdd-discovery/scripts/kickoff_path_resolve.py <AIBDD_ARGUMENTS_PATH_abs>` → JSON：`behavior_paths_bound`、`features_dir` / `activities_dir`（可為未綁定的 `null`）、plan paths、truth roots。未綁定時 script gate **跳過 scan**。

| 參數 | 來源 | 說明 |
|------|------|------|
| `${AIBDD_ARGUMENTS_PATH}` | `arguments.yml` | project config SSOT；預設 `${AIBDD_CONFIG_DIR}/arguments.yml` |
| `${SPECS_ROOT_DIR}` | `arguments.yml` | 規格根 |
| `${BOUNDARY_YML}` | `arguments.yml` | 指向 `boundary.yml` |
| `${CURRENT_PLAN_PACKAGE}` | `arguments.yml` / command payload / environment | 本次 plan session package |
| `${PLAN_SPEC}` | `arguments.yml`（展開後） | 本次 `spec.md` |
| `${PLAN_REPORTS_DIR}` | `arguments.yml`（展開後） | 本次 reports directory |
| `${TRUTH_BOUNDARY_ROOT}` | `arguments.yml`（展開後） | target boundary truth root |
| `${TRUTH_BOUNDARY_PACKAGES_DIR}` | `arguments.yml`（展開後） | boundary functional packages root |
| `${TRUTH_FUNCTION_PACKAGE}` | `arguments.yml` / bind script 寫回後機械解析 | target functional package truth root |
| `${ACTIVITIES_DIR}` | bind 後 | accepted Activity truth 目錄（`${TRUTH_FUNCTION_PACKAGE}/activities`） |
| `${FEATURE_SPECS_DIR}` | bind 後 | accepted rule / behavior truth 目錄（`${TRUTH_FUNCTION_PACKAGE}/features`） |
| `${BOUNDARY_SHARED_DSL}` | `arguments.yml`（展開後） | boundary shared DSL truth |
| `${BOUNDARY_PACKAGE_DSL}` | `arguments.yml`（展開後） | target package local DSL truth |
| `${ACTIVITY_EXT}` | `arguments.yml` | Activity 副檔名；Discovery 強制 `.activity` |
| `${BDD_CONSTITUTION_PATH}` | `arguments.yml` | Project BDD constitution（filename axes 的 SSOT） |
| `${FEATURE_FILENAME_CONVENTION}` | **無預設**（必由 Step 0 從 `${BDD_CONSTITUTION_PATH}` §5.1 `filename.convention` 讀出） | Operation Partition 套到檔名 schema 的決定值。允許 enum：`NN-prefix-then-title` / `kebab-all-lower` / `snake_case` / `PascalCase` / `free-form:<regex>` |
| `${FEATURE_TITLE_LANGUAGE}` | **無預設**（必由 Step 0 從 `${BDD_CONSTITUTION_PATH}` §5.1 `filename.title_language` 讀出） | 檔名 title 部分的語言。允許 enum：`zh-Hant` / `zh-Hans` / `en` / `ja` / `ko` / `mixed` / `custom:<iso-code>` |

`${FEATURE_FILENAME_CONVENTION}` / `${FEATURE_TITLE_LANGUAGE}` **不可** fall back 到 plugin-level default（依 `${BDD_CONSTITUTION_PATH}` §5.1：Skill 嚴禁對這些選擇有意見或補預設值）。Step 0 讀不到 → STOP 走 `/clarify-loop` 補齊 §5.1 後從 Step 0 重跑。
