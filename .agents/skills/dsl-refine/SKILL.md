---
name: dsl-refine
description: Truth owner skill。承接 plan package 的 acceptance Gherkin 與 system-analysis 產物，將業務 Journey 拆成 interface-level executable feature files 與 DSL，並更新 `specs/truth/features/backend/**`、`specs/truth/features/frontend/**`。完成後委派 `/truth-delta` 記錄 feature/dsl truth 改動。
disable-model-invocation: true
---

# DSL Refine

`dsl-refine` 是 interface feature 與 DSL 的 truth owner。Acceptance Gherkin 留在 plan package；拆解後可執行的前後端介面 feature/dsl 則寫入 `specs/truth/features/**`，代表目前系統測試規格真相。

# SOP

## Phase 1 -- 對齊 acceptance、系統介面與 feature truth

1. READ 讀取使用者要求、目標 plan package 的 `features/acceptance/**`、`plan.md`、`truth-delta.md`、`specs/truth/techstack.md`、相關 UI plan，以及受影響介面的既有功能模組、feature、模組 DSL 與介面根共用 DSL。
2. THINK 從 `plan.md`、truth-delta 與現有 feature truth 辨識本次涉及的前端、後端或其他系統介面，以及各介面既有 feature/dsl 是否需要 ADD / MODIFY / DELETE。
3. WRITE 向使用者回報本輪辨識出的介面、預計新增/修改/刪除的 truth feature files 與 DSL 範圍。

## Phase 2 -- 分派 acceptance 規則並處理高影響變更

1. READ 讀取 `rules/介面Gherkin原子化與單一Act判準.md`，確認介面 Gherkin 原子化與單一 Act 邊界。
2. THINK 逐一盤點 acceptance 的 Rule、Example、關鍵 Given / When / Then 與 `# [need clarification]`，分派到相關介面，確認每條 acceptance 規則至少由一個 interface truth 承接。
3. DELEGATE 若高影響 MODIFY / DELETE 會改寫既有 interface 行為、移除既有驗收或削弱 DSL 驗證契約，且尚未有明確使用者決策，呼叫 `/clarify`；未收斂前停止。

## Phase 3 -- 更新 interface feature truth

1. READ 讀取 `../gherkin-and-dsl/SKILL.md` 與 `../gherkin-and-dsl/STANDARDS.md`，承接其已掛載的 Gherkin、DSL 與唯一歸屬判準。
2. WRITE 依已載入規則在唯一權威位置建立、修改、移動或刪除受影響的 interface feature 與 DSL rows。
3. DELEGATE 呼叫 `/gherkin-and-dsl` 檢查受影響介面，取得拓樸機械稽核、DSL 唯一歸屬、acceptance 覆蓋與 Gherkin 結構結果；若不符合，立即修正。
4. THINK 將 feature/dsl truth 改動整理為語意單元層級的 ADD / MODIFY / DELETE / NOOP 列。

## Phase 4 -- 更新 truth-delta 並交付

1. DELEGATE 呼叫 `/truth-delta`，傳入 plan package、truth root、owner `/dsl-refine`、受影響模組、feature、模組 DSL、相關共用 DSL rows 與本輪 truth 改動列；DSL row 僅搬移權威位置而未改語意時，明示舊位置、新位置與「語意不變」。
2. WRITE 向使用者回報更新的 interface feature/dsl truth、truth-delta 更新結果、已澄清決策、剩餘阻塞缺口，以及是否可交給 `/tasks` 或 `/bdd`。
