---
name: implement
description: 根據 plan package 的 `tasks.md`，以 don't stop until deliver / One-Shot 執行已解鎖 task。一輪恰好 1 個 task 或 Parallel Hint 批次；驗證後立刻回寫 `[X]` 再繼續，直到交付。不能跳步驟。
disable-model-invocation: true
---

# Implement

`implement` 將 `tasks.md` 視為唯一執行控制平面，但執行上下文必須包含 plan package 與 `truth-delta.md`。它負責交付 plan，不負責重新定義 truth；若發現 truth 與 tasks 明顯矛盾，應停止受影響 task 並回報需要上游修正。

## Operating Principles

- by default 就是 don't stop until deliver / One-Shot：從第一個已解鎖 task 做到目標 plan 全部 `[X]`。使用者不必再寫這句。
- One-Shot 的一輪任務集恰好是 1 個已解鎖 task；有 `Parallel Hint` 時改為 Hint 列出的 `[P]` 批次。One-Shot 不是把後面的序列 task 一次攤開。
- 做完一個任務集就驗證，立刻回寫 `tasks.md` 的 `[X]`，再重算下一筆。未回寫不得開下一個任務集。
- 嚴格執行不能跳步驟。`don't stop until deliver` 不是跳步驟的許可。
- Feature phase 仍序列。`[BDD-GREEN]`、`[BDD-REFACTOR]` 才委派 `/bdd`，並把該 phase 的 `Test Scope` 當範疇。
- Phase 3 的 `[BDD-ALIGN]`、`[BDD-REMOVE]`、`[BDD-RED]` 不委派 `/bdd`；由 subagent 讀 `dsl.md` 該列的 `StepDef 實作語意` 寫測試層。
- Phase 3 review 通過前，不得進入 Feature Green。
- 全部 tasks `[X]` 後詢問是否 git commit；不得自動 commit。

# SOP

## Phase 1 -- 對齊 plan 並啟動 One-Shot

1. READ 讀取使用者需求、目標 plan package、`tasks.md`、`truth-delta.md` 與目前 task 完成狀態，確認指定範圍（若有）與 One-Shot 起點。
2. READ 讀取 `rules/任務選取與連續續跑判準.md`，確認已解鎖 task 的選取、One-Shot 與停止條件。
3. READ 讀取 `rules/TruthDelta測試對齊與BDD委派判準.md`，確認 ADD / MODIFY / DELETE 的執行策略，以及哪些 marker 才委派 `/bdd`。
4. THINK 依已讀任務與判準收斂 One-Shot 起點、是否命中 `Parallel Hint`、所屬 phase；預設做到交付，不停在第一筆。

## Phase 2 -- 補強 repo hygiene 與執行前置

1. READ 讀取 `rules/repo-hygiene-與-ignore-補強判準.md`，確認本次需要檢查哪些 ignore surfaces、哪些只可增補不可覆寫。
2. THINK 依目前 repo、工具鏈、plan package、truth-delta 與 `specs/truth/techstack.md` 收斂本輪必做的最小 hygiene 補強。
3. WRITE 只在實際相關且確有缺口時建立或增補 ignore 設定，避免擴張到無關工具鏈。

## Phase 3 -- 收斂本輪任務集（不能跳步驟）

1. READ 讀取 `rules/嚴格禁止跳步驟判準.md` 與 `rules/平行執行與檔案衝突判準.md`，確認本輪任務集邊界。
2. READ 若 `tasks.md` 當前 phase 含 `Parallel Hint`，讀取 `rules/ParallelHint平行Subagent與衝突Merge判準.md`。
3. THINK 收斂本輪任務集：有 `Parallel Hint` 則為 Hint 列出的 `[P]` 批次；否則恰好 1 個已解鎖 task。
4. THINK 收斂執行模式：Setup 與 Foundational 直接實作並停在該則「只做／不做」；Phase 3 的 ALIGN / REMOVE / RED 走 subagent 測試層；review 走 review 迴圈；`[BDD-GREEN]` / `[BDD-REFACTOR]` 委派 `/bdd`；`[CODE-REMOVE]`、`[REGRESSION]` 直接實作或直接驗證。

## Phase 4 -- 載入精確參照並執行

1. READ 讀取 `rules/技術參照載入與最小上下文判準.md`，確認 `Read`、phase-level `Shared Must Read`、`Extra Read`、truth-delta rows 與相鄰 task / artifact 的載入邊界。
2. READ 依當前任務集的精確參照載入必要 plan artifacts、truth feature、同模組 DSL、實際列出的介面根共用 DSL rows 與既有自動化測試落點；不得掃描或預讀其他模組 DSL。
3. READ 若本輪修改受憲法治理的 artifact 或與 truth specs 發生衝突，讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md` 與對應憲法檔。
4. READ 讀取 `rules/自主決策與阻塞處理判準.md`，確認規格缺口、局部矛盾或環境阻礙時的決策優先序。
5. DELEGATE 若本輪是 `Parallel Hint` 批次，為每個 `[P]` task 派出獨立 subagent，prompt 指向該 plan `tasks.md` 的對應任務；全部回來後執行 review 迴圈。
6. DELEGATE 若本輪是 `[BDD-GREEN]` 或 `[BDD-REFACTOR]`，呼叫 `/bdd` 的單一 requested step，傳入 `Test Scope`、action、truth rows、模組 DSL 與實際使用的共用 DSL rows。
7. WRITE 若 task 不帶上述 marker，依 task marker 完成本輪所需的程式、設定、文件或測試變更；不得越出本輪任務與 phase boundary。

## Phase 5 -- 驗證、回寫、繼續 One-Shot 直到交付

1. READ 讀取 `rules/完成定義-驗證與回寫判準.md`，確認 task 完成條件與回寫條件。
2. THINK 依 task 類型收斂最直接的驗證方式。
3. WRITE 在本輪任務集的實作與驗證都完成後，立即將對應 task 改寫為 `[X]`，並保留其他 task 狀態不變。
4. THINK 重新計算是否仍存在已解鎖且屬於本次範圍的未完成 task；若有，返回 Phase 3。這是 One-Shot 預設，不是可選。
5. WRITE 若目標 plan package 全部 tasks 已 `[X]` 且驗證通過，向使用者回報本次 plan 已交付，並詢問是否用 git commit deliver；未取得使用者同意前不得 commit。
