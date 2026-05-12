# 角色 + 入口契約

> 純 declarative reference。Phase 1-2 LOAD 取角色定位 + 入口 schema。
>
> 來源：原 SKILL.md `## Why this skill exists` + scope 段。

## §1 角色定位

Business-axis analyzer — 把 atomic rule → 最小必要 Example 句型集。

抽象軸：**業務例**（從 rule 推導 Spec-by-Example；機械句型合規以 plan `dsl.yml` **L1** 為準）。

本 skill **不**擁有獨立 step-pattern markdown SSOT；L1/L4 truth 由 `/aibdd-plan` 產出的 `BOUNDARY_PACKAGE_DSL` / `BOUNDARY_SHARED_DSL` 提供；`L4.preset.name` 僅用於追溯 `/aibdd-plan` boundary assets（handler/variant），不是本目錄下額外 preset 檔。

## §2 職責拆分（與物理層 skill 的分工）

- **Example 句型具體化 / Spec-by-Example 填空** — 本 skill 設計與執行（在既有 L1 模板範圍內）
- **L1 模板 + L4（物理綁定）** — 本 skill **只讀** `/aibdd-plan` 產出；**絕不就地新增或改寫 DSL / contract / data / test-strategy truth**

物理層設計住在上游 `/aibdd-plan`，產出 boundary technical truth 與 DSL L4 mapping。

## §3 上游缺 anchor 處理

若發現 physical mapping 缺 binding（例：某 Scenario 想 assert 一個 response/state，但 DSL 無 `assertion_bindings` 或 OpenAPI/DBML 無對應欄位）→ **STOP** 並回 `/aibdd-plan` 補齊，**不得就地補物理元素**。

設計理由與反面/正面案例見 `aibdd-core::physical-first-principle.md`。

## §4 Scope 邊界

- 只到 example 層
- 不改 rule 本體 / DSL / DBML / OpenAPI 合約 / test-strategy / plan package truth
- 提問禁令：本 skill 全程不向使用者提問；疑處累積為 CiC 便條紙，由 SpecKit `/speckit.clarify` 下一輪消化

## §5 Boundary Package Layout

採 `/aibdd-plan` boundary-aware packing model：

- feature truth：`${FEATURE_SPECS_DIR}`
- local DSL：`${BOUNDARY_PACKAGE_DSL}`
- shared DSL：`${BOUNDARY_SHARED_DSL}`
- contracts：`${CONTRACTS_DIR}`
- data/state：`${DATA_DIR}`
- test strategy：`${TEST_STRATEGY_FILE}`
- example coverage：`${TRUTH_FUNCTION_PACKAGE}/coverage/`
