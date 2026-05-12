# BDD Analysis — I/O Contract

本 Planner 的 reads / writes / config 精確定義。Planner 只透過這裡宣告的 artifact 與世界溝通。

> **路徑規約**：本 skill 是 `/aibdd-plan` output consumer。所有 runtime paths 必須由
> `.claude/skills/aibdd-plan/scripts/python/resolve_plan_paths.py <arguments.yml>` 展開，
> 不得猜測舊 flat features 目錄或自行建立 DSL 檔。

## §Reads

| 來源 | 內容 | 必要性 |
|------|------|-------|
| `aibdd-core::spec-package-paths.md` | spec package 路徑慣例（LOAD） | 必要 |
| `aibdd-core::atomic-rule-definition.md` | Atomic rule 判定準則（LOAD） | 必要 |
| `aibdd-core::report-contract.md` | Planner 匯報與 user-facing message style 規範（LOAD） | 必要 |
| `${FEATURE_SPECS_DIR}/**/*.feature` | atomic rule 骨架（含 `@ignore`、無 Examples） | 必要 |
| `${BOUNDARY_PACKAGE_DSL}` | package DSL：`L1` canonical step 模板 + `L4` physical mapping（SSOT） | 必要，只讀 |
| `${BOUNDARY_SHARED_DSL}` | boundary shared DSL registry（同樣提供合併後的 `L1` 句型池） | 有才讀，只讀 |
| `${CONTRACTS_DIR}/**/*.{yml,yaml}` | OpenAPI operation contract truth | 必要（web-service boundary） |
| `${DATA_DIR}/**/*.dbml` | DBML persistence/state truth | 有才讀，只讀 |
| `${TEST_STRATEGY_FILE}` | dependency edges / external stub / runner strategy | 必要，只讀 |
| `${PLAN_REPORTS_DIR}/aibdd-plan-quality.md` | 上游 plan gate 結果 | 必要 |
| `${CURRENT_PLAN_PACKAGE}/implementation/**` | implementation diagrams for context | 有才讀，只讀 |
| `${TRUTH_FUNCTION_PACKAGE}/coverage/*.coverage.yml` | 既有 package example coverage | 有才讀 |

## §Writes

| artifact pattern | 寫入方式 | 備註 |
|------------------|----------|------|
| `${FEATURE_SPECS_DIR}/**/*.feature` | DELEGATE `/aibdd-form-feature-spec` | 為每條 atomic rule 加 Scenario / Scenario Outline + Examples；移除 `@ignore`；不得改 Rule 本文 |
| `${TRUTH_FUNCTION_PACKAGE}/coverage/*.coverage.yml` | Planner 直接寫（example 層） | 寫入或追加 `coverage_type: example` entries；`rule_id` 必須是 atomic Rule anchor |
| `${CURRENT_PLAN_PACKAGE}/promotion-proposal.md` | 條件寫入 | 只有當新版 `dsl.yml` promotion gate 可用且觸發；否則 no-op |

## §Config

| 參數 | 預設 | 說明 |
|------|------|------|
| `${arguments_yml_path}` | `${workspace_root}/.aibdd/arguments.yml` | `/aibdd-plan` resolver 的唯一入口 |
| `${SPECS_ROOT_DIR}` | `specs` | workspace-level specs root，由 arguments.yml 展開 |
| `${FEATURE_SPECS_DIR}` | resolver output | Feature artifacts 目錄 |
| `${TRUTH_FUNCTION_PACKAGE}` | resolver output | package truth root；coverage 預設寫於其下 `coverage/` |
| `${BOUNDARY_PACKAGE_DSL}` | resolver output | package DSL；read-only SSOT |
| `${BOUNDARY_SHARED_DSL}` | resolver output | shared DSL；read-only SSOT |
| `${CONTRACTS_DIR}` | `${TRUTH_BOUNDARY_ROOT}/contracts` | OpenAPI truth root |
| `${DATA_DIR}` | `${TRUTH_BOUNDARY_ROOT}/data` | DBML truth root |
| `${TEST_STRATEGY_FILE}` | resolver output | dependency/test strategy truth |
| `${MAX_QUESTIONS_PER_ROUND}` | `10` | （未使用；plugin 下無互動 clarify） |
