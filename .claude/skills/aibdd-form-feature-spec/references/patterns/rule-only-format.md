# Rule-Only Format

Discovery / System Analysis / SA 階段 DELEGATE `form-feature-spec` 時使用。此階段只做 Rule 發散收斂，尚未進入 BDD Analysis。

---

## 結構

```gherkin
@ignore @command
Feature: <功能名>

  <功能描述（一段話，首句必含 trigger keyword）>

  Rule: 前置（狀態） - <主詞> 必須 <單一條件>
    <選填 body：細節 / bullet / 條件分歧>

  Rule: 前置（參數） - <主詞> 必須 <單一條件>

  Rule: 後置（回應） - <主詞> 應 <單一條件>
    <選填 body>

  Rule: 後置（狀態） - <主詞> 應 <單一條件>

  # TODO: Example 區段由後續 BDD Analysis 階段補充。
```

每條 Rule 採**兩段式**：**Rule line**（必填，單行 prefix + 短斷言）+ **Rule body**（選填，縮排 +2 spaces 的多行區塊）。完整規範與正反例見 `format-reference.md §Rule line vs Rule body 的分工`。

### 兩段式範例

```gherkin
Rule: 後置（狀態：行為） - 設定精靈讓工程師輸入測試指令
  工程師在精靈表單內輸入：
  - test command（例 `pnpm test`）
  - test filter pattern（例 `--filter {goalFeature}`）
  並可看到組合後的指令預覽。

Rule: 前置（狀態） - 同一時間只允許一個 active 指揮站臺 tab

Rule: 後置（狀態：行為） - 已有指揮站臺時再點「🚀」直接 focus existing tab
  工程師在已存在 active 指揮站臺時再點擊「🚀」：
  - 把既存的指揮站臺 tab 帶到前景（focus existing），不開新 tab
  - 不重置 session 進度
  - 不重設 chat scope；若右側面板當前不在 Evaluation Agent 模式則同步切回
```

中間那條（單一斷言、已自洽）**不需要 body**。

### 反例：Rule line 臃腫

```gherkin
# ❌ 全部塞在 Rule line（80+ 全形字、bullet 都擠進來）
Rule: 後置（狀態：行為） - 設定精靈 Step 1「測試指令」 — 工程師輸入 test command（例 `pnpm test`）+ test filter pattern（例 `--filter {goalFeature}`）+ 指令預覽。
```

→ 應拆為 Rule line + body 兩段（如上正例）。

---

## 規則

1. **無 Background** — Background 存在的前提是有 Example 需要共用 Given，rule-only 階段沒有 Example，所以不寫 Background
2. **無 Example / Scenario / Scenario Outline** — 具體案例由 BDD Analysis 產出
3. **4-Rules Pattern** — 每條 Rule 使用前綴分類：`前置（狀態）` / `前置（參數）` / `後置（回應）` / `後置（狀態）`（後置（狀態）可選用子類：`後置（狀態：資料）` / `後置（狀態：外發）` / `後置（狀態：資源）` / `後置（狀態：行為）`），命名遵循 `format-reference.md` 的原子化規範與類型前綴決策樹
4. **兩段式 Rule（name + body）** — Rule line 限 prefix + 短斷言；細節與 bullet 縮排 +2 spaces 到 Rule body。完整規範見 `format-reference.md §Rule line vs Rule body 的分工`
5. **Gherkin dialect keyword 撞牆禁忌** — description 段、Rule body、bullet 行的「行首」（縮排後第一字元）**不可**撞到目前 feature 所選 Gherkin dialect 的任一 Given / When / Then / And / But keyword 或 alias；完整規範見 `format-reference.md §Gherkin dialect keyword 撞牆禁忌`；Quality Gate `check_discovery_phase.py` 以 `RULE_BODY_KEYWORD_COLLISION` violation 擋下
6. **前置在上** — 所有前置 Rule 排在後置 Rule 上方
7. **`@ignore` 必備** — 標記為尚未完成 BDD Analysis
8. **TODO 註解** — Feature 末尾帶 `# TODO: Example 區段由後續 BDD Analysis 階段補充。`
9. **Authentication 豁免** — 不寫「使用者必須已登入」「使用者必須持有有效 session」這類認證 Rule。認證屬 actor 身分屬性，由 actor key binding（`@buyer` / `@admin` / `@logged-in-user`）在 feature file 層表達；例外為認證流程本身（登入 / 註冊 / 密碼重設 / MFA）。詳見 `aibdd-core::authentication-binding.md`
