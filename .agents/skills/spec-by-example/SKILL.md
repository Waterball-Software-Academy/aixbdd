---
name: spec-by-example
description: 承接新的 plan package 中的 `spec.md`，把需求收斂成 plan-side `features/acceptance/*.feature`。此 skill 只寫入 `specs/plans/NNN-*/features/acceptance/**`，不修改 `specs/truth/**`，也不更新 `truth-delta.md`。
disable-model-invocation: true
---

# Spec By Example

`spec-by-example` 產出 PM 可 review 的總驗收 Gherkin。這一層仍屬於 plan：它描述本次迭代希望達成的業務旅程，不是目前系統的 interface truth。

# SOP

## Phase 1 -- 對齊 plan spec 與輸出位置

1. READ 讀取使用者需求、呼叫者要求、目標 plan package 的 `spec.md`、既有 `features/acceptance/` 內容，以及必要的 `specs/truth/**` 高層現況。
2. READ 讀取 `rules/輸出位置與acceptance切檔判準.md`，確認 acceptance feature files 必須輸出到當前 plan package。
3. WRITE 若 `specs/plans/NNN-<slug>/features/acceptance/` 尚不存在，建立該目錄。

## Phase 2 -- 收斂驗收旅程與需求缺口

1. READ 讀取 `rules/gherkin-驗收句型與結構判準.md`、`templates/acceptance.feature`、`templates/acceptance.example.feature`、`templates/電商範例/features/acceptance/訂單成立與付款超時.feature`、`templates/電商範例/features/acceptance/庫存預留與超賣防護.feature`、`templates/電商範例/features/acceptance/折扣疊加與互斥.feature`、`templates/電商範例/features/acceptance/滿額贈品與條件取消.feature` 與 `templates/電商範例/features/acceptance/運費分區與免運判定.feature`，確認 acceptance Gherkin 的顆粒度、句型、Rule / Example 邊界與完成樣貌。
2. THINK 依 `spec.md` 的 User Stories、Acceptance Criteria、邊界情況與全域需求，收斂少量但關鍵的 Journey 型驗收流程。
3. READ 若需求存在會改變 Journey、規則歸屬、驗收結果或切檔的高影響缺口，讀取 `rules/缺口標記與Clarify升級判準.md`。
4. DELEGATE 若仍有高影響缺口，呼叫 `/clarify`；未收斂前停止，不自行假設答案。

## Phase 3 -- 產出 acceptance Gherkin

1. WRITE 在目標 plan package 的 `features/acceptance/` 下建立或更新 feature files；Gherkin 維持業務語言，不拆前端 / 後端，也不產出 `dsl.md`。
2. WRITE 將高影響未定事項直接標在對應 feature 的規則或步驟旁，格式固定為 `# [need clarification] ...`。
3. READ 回頭檢查每份 feature 是否與 `spec.md` 一致、可被 PM 直接閱讀，且不與已知 truth 明顯衝突；若不符合，立即修正或升級 clarify。

## Phase 4 -- 交付後續 handoff

1. WRITE 向使用者回報寫入的 acceptance feature files、已澄清決策、剩餘 `# [need clarification]`，以及是否可進入 `/system-analysis` 或 `/dsl-refine`。
