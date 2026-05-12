# Gherkin DSL 最佳實踐

> 純 declarative reference。Phase 3 FORMULATE 時 LOAD 取規則。
>
> 來源：原 SKILL.md `## §4 DSL 最佳實踐`。

## §1 Gherkin 關鍵字

一律使用英文：`Feature` / `Rule` / `Example` / `Scenario Outline` / `Examples` / `Given` / `When` / `Then` / `And` / `But` / `Background`。描述與步驟使用繁體中文。

## §2 Rule 命名

- 前綴分類：`前置（狀態）` / `前置（參數）` / `後置（回應）` / `後置（狀態）`
- 後置（狀態）可選用子類：`後置（狀態：資料）` / `後置（狀態：外發）` / `後置（狀態：資源）` / `後置（狀態：行為）`
- 後置（回應）須通過可測試閘門（能寫成 `Then <主詞> 應為 <具體值>`）；完整決策樹見 `format-reference.md` §類型前綴決策樹
- 主詞 + 動詞 + 單一條件（atomic rule 原則）
- 前置 Rule 排在後置 Rule 上方

## §3 Authentication 豁免

「使用者必須已登入」這類認證 Rule 不列；由 actor key binding 表達。SSOT：`aibdd-core::authentication-binding.md`

## §4 Example 規則

- `Rule:` 區塊內用 `Example`（不用 `Scenario`）
- `Scenario Outline` + `Examples` 用於 data-driven
- 每個 Example 獨立執行（不依賴其他 Example 的狀態或順序）
- 具體值（Spec-by-Example），禁用 `(待澄清)` / `某個` / `XX`

## §5 Background 節制

Background 僅含「所有 Example 都需要」的共用 Given。單一 Example 獨有的 Given 放進該 Example。

## §6 plan DSL L1（句型來源聲明）

Spec-by-Example 具體句型由 caller 推理包約束：BDD Analyze 場景下以 `/aibdd-plan` 產出之 `dsl.yml` **`L1`** 為 SSOT。本 skill 不鏡像句型檔、不自行發明與 plan DSL 不一致的 Given/When/Then。
