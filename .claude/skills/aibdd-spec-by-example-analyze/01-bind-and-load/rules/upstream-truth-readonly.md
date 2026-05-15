# 上游真相 READ-ONLY 邊界

- **唯讀範圍**：`${BOUNDARY_PACKAGE_DSL}`、`${BOUNDARY_SHARED_DSL}`、`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${TEST_STRATEGY_FILE}`、`${FEATURE_SPECS_DIR}/**/*.feature` 之 `Rule:` block 本體、`${BOUNDARY_YML}`、constitution。若 `${PLAN_REPORTS_DIR}/aibdd-plan-quality.md` **存在**，同樣唯讀，但 **01-bind-and-load 不將其列為進入本 skill 之必要條件**。
- **本 skill 對上述任一檔不得 WRITE／UPDATE／CREATE-shell**；唯一被允許動到的 `.feature` 範圍是「在 atomic Rule 後新增 Scenario／Scenario Outline + Examples」與「移除 `@ignore` tag」——但**仍**只能透過 DELEGATE `/aibdd-form-feature-spec` 進行，不能本 skill 直接 edit。
- **WHY**：上游檔是 `/aibdd-plan` 與更上游 owner 的 single source of truth；下游 phase 若就地補洞，會讓 plan 與下游脫鉤，未來重跑 plan 就會覆蓋掉下游偷加的內容，造成漂移與審查死角。
- **缺真相之處置**：發現 DSL 缺 binding、contract 缺 operation／欄位、DBML 缺 table、test-strategy 缺 edge → 立即累積 CiC 便條紙到 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，**STOP** 並提示使用者回 `/aibdd-plan` 補完。

# 反例

- ✗ 發現 DSL entry 缺 `assertion_bindings` 之 response 欄位 → 順手在 `${BOUNDARY_PACKAGE_DSL}` 補一筆 `{key: 訂單編號, target: response.body.orderId}`。應改為：累積 CiC(GAP)，STOP。
- ✗ 發現 contract 缺某 operation 之 status code 400 描述 → 順手在 `${CONTRACTS_DIR}/orders.yml` 加 `responses.400`。應改為：CiC(GAP)，STOP。
- ✗ 發現 atomic rule 字詞拗口想潤飾 → 改 `${FEATURE_SPECS_DIR}/orders.feature` 之 `Rule: <title>`。應改為：不動，rule wording 之 ownership 屬 `/aibdd-discovery`。
- ✓ 發現 plan quality 報告 `verdict == VETO` → 直接向使用者列出 vetoes 並 STOP，提示回 `/aibdd-plan` 修。

# 禁止自生

- **不得**新增 DSL entry／OpenAPI operation／DBML table／test-strategy edge 給下游用——所有 plan-owner artifact 之新增僅能在 `/aibdd-plan` 重跑。
- **不得**改 atomic rule 之 title 或 body 字詞——byte-for-byte preserve。
- **不得**改 feature 路徑、檔名、`Background:`、既有 `Scenario:` 之 title／body——`.feature` 之 mutation 只能透過 DELEGATE 加 Examples。
- **不得**改 `${PLAN_REPORTS_DIR}/aibdd-plan-quality.md`——quality 報告之 owner 屬 `/aibdd-plan`；本 skill 自己的 quality 報告寫到 `bdd-analyze-quality.md`。
- 違反處置：偵測到任一上述檔被本 skill 修改 → quality gate VETO（`NO_PLAN_TRUTH_EDIT`），整輪作廢，必須 git revert 後重跑。
