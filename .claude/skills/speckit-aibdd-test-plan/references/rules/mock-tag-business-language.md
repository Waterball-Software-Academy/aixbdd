# R14 — Mock Step [MOCK] Tag + 業務語言（Phase 5 invariant）

> 純 declarative reference。Phase 5 Subagent semantic validation 用此規則檢驗。
>
> 來源：原 SKILL.md `## Step 4 — R14`。NEW per `aibdd-core::physical-first-principle.md` MR-1 / MR-2。

## §1 規則本體

flow scenario 內所有引用 mock-setup 類 DSL entry 的 Given step（含 datatable 形式），句首 keyword 後必加 `[MOCK]` 視覺 tag。

## §2 範例

- ✓ `Given [MOCK] AI 評審員預設判定為 "pass"`
- ✗ `Given Goal evaluator mock 將下列 TestReport 推入回傳佇列`

## §3 業務語言守則

Tag 後句子必須為業務語言，禁出現：

- mock 機制術語：mock / stub / queue / 推入 / 佇列 / fixture / spy 等
- schema 名：TestReport / verdict / phaseAdvancedTo 等
- op id：verify_goal / get_next_goal / bindTestplan 等

datatable header 也適用同規則（用業務翻譯如「評審 / 原因 / 通過數」取代「verdict / reason / scenarios.passed」）。

## §4 違反處理

違反 → `R14_MOCK_TAG_OR_BUSINESS_LANGUAGE`（hard-fail）；指示回 Phase 4 重寫；若 boundary `dsl.md` 對應 entry 本身就違規 → 回 `/speckit.aibdd.bdd-analyze` Phase 5 補 `MOCK_DSL_HAS_MOCK_TAG` / `MOCK_DSL_L1_BUSINESS_LANGUAGE_GUARD`。
