---
name: implement
description: 根據 plan package 的 `tasks.md` 自主執行下一個已解鎖 task，精準載入 `Shared Must Read` / `Boundary` / `Read` / `Extra Read`。嚴格一步一 task，禁止跳步；對 truth-delta 的 ADD / MODIFY / DELETE 採 action-aware 執行與驗證，完成整個 plan 後詢問是否用 git commit deliver。
license: Complete terms in LICENSE
disable-model-invocation: true
---

# Implement

`implement` 將 `tasks.md` 視為唯一執行控制平面，但執行上下文必須包含 plan package 與 `truth-delta.md`。它負責交付 plan，不負責重新定義 truth；若發現 truth 與 tasks 明顯矛盾，應停止受影響 task 並回報需要上游修正。

## Operating Principles

- 嚴格一步一 task：每一輪預設只推進恰好 1 個已解鎖 task；禁止跳步、跨 `BDD-*`、預做後續 task，或未驗證／未回寫就開做下一個。
- `[P]` 是唯一可同輪例外，且不代表必須平行；凡未標 `[P]`、共享檔案、共享驗證面或存在前後依賴者，一律序列。
- 執行前必須依 `truth-delta.md` 判斷當前 task 是 ADD / MODIFY / DELETE / NOOP 哪一類；MODIFY / DELETE 必須先確認受影響既有自動化測試面。
- 若 task 帶 `[BDD-RED]`、`[BDD-ALIGN]`、`[BDD-GREEN]`、`[BDD-REFACTOR]`、`[BDD-REMOVE]`，必須呼叫 `/bdd` 的單一步驟，並明確帶上 truth delta action、truth feature file、同模組 `dsl.md`、實際使用的介面根共用 DSL rows 與既有測試對齊要求。
- 每完成一個 task 都要先驗證，再立即回寫 `[X]`，接著才能重新計算下一個已解鎖 task。
- 當目標 plan package 所有 tasks 都已 `[X]` 且驗證通過，停止續跑並詢問使用者是否建立 git commit；不得自動 commit。

# SOP

## Phase 1 -- 對齊 plan、truth-delta 與 task 邊界

1. READ 讀取使用者需求、目標 plan package、`tasks.md`、`truth-delta.md` 與目前 task 完成狀態，確認本次是執行指定範圍，還是自動接手下一個已解鎖 task。
2. READ 讀取 `rules/任務選取與連續續跑判準.md`，確認已解鎖 task 的選取方式、續跑規則與停止條件。
3. READ 讀取 `rules/TruthDelta測試對齊與BDD委派判準.md`，確認 ADD / MODIFY / DELETE / NOOP 的執行策略、既有測試盤點與 `/bdd` 委派要求。
4. THINK 依已讀任務與判準收斂本輪執行範圍、起始 task、task marker、truth delta action、所屬 phase、受影響測試面與預期續跑邊界。

## Phase 2 -- 補強 repo hygiene 與執行前置

1. READ 讀取 `rules/repo-hygiene-與-ignore-補強判準.md`，確認本次需要檢查哪些 ignore surfaces、哪些只可增補不可覆寫。
2. THINK 依目前 repo、工具鏈、plan package、truth-delta 與 `specs/truth/techstack.md` 收斂本輪必做的最小 hygiene 補強。
3. WRITE 只在實際相關且確有缺口時建立或增補 ignore 設定，避免擴張到無關工具鏈。

## Phase 3 -- 收斂本輪可執行任務集與執行模式

1. READ 讀取 `rules/嚴格禁止跳步驟判準.md` 與 `rules/平行執行與檔案衝突判準.md`，確認本輪不得跳步、跨 BDD step、預做後續或併批衝突任務。
2. THINK 依 `tasks.md` 的 phase 順序、Dependencies、勾選狀態、本輪指定範圍、truth-delta action 與受影響測試面，收斂本輪任務集；預設恰好 1 個已解鎖 task。
3. THINK 若 task 帶 `[BDD-*]` 或 `[BDD-ALIGN]` / `[BDD-REMOVE]`，本輪模式為委派 `/bdd` 的單一 requested step；`[CODE-REMOVE]`、`[REGRESSION]`、Setup / Foundational / NFR / 一般任務則直接實作或直接驗證。

## Phase 4 -- 載入精確參照並執行

1. READ 讀取 `rules/技術參照載入與最小上下文判準.md`，確認 `Read`、phase-level `Shared Must Read`、`Extra Read`、truth-delta rows 與相鄰 task / artifact 的載入邊界。
2. READ 依當前 task 的精確參照載入必要 plan artifacts、truth feature、同模組 DSL、實際列出的介面根共用 DSL rows 與既有自動化測試落點；不得掃描或預讀其他模組 DSL。MODIFY / DELETE 類 task 必須載入或定位受影響 step definitions、fixtures、helpers、focused tests 與產品分支。
3. READ 若本輪修改受憲法治理的 artifact 或與 truth specs 發生衝突，讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md` 與對應憲法檔。
4. READ 讀取 `rules/自主決策與阻塞處理判準.md`，確認規格缺口、局部矛盾或環境阻礙時的決策優先序。
5. DELEGATE 若 task 帶 BDD marker，呼叫 `/bdd` 的單一 requested step，原樣傳入 action、truth rows、feature、模組 DSL、實際使用的共用 DSL rows 與既有自動化測試面；不得在此重新判斷 DSL 歸屬。
6. WRITE 若 task 不帶 BDD marker，依 task marker 完成本輪所需的程式、設定、文件或測試變更；不得越出本輪任務與 phase boundary，也不得讓過期測試繼續保護舊 truth。

## Phase 5 -- 驗證、回寫與交付判斷

1. READ 讀取 `rules/完成定義-驗證與回寫判準.md`，確認 task 完成條件、action-aware 驗證方式與回寫條件。
2. THINK 依 task 類型、truth-delta action 與變更內容收斂最直接的驗證方式；ADD 檢查新增測試紅綠路徑，MODIFY 檢查既有測試已改成新版 truth，DELETE 檢查過期測試與過期行為已移除且回歸通過。
3. WRITE 在本輪 task 實作與驗證都完成後，立即將對應 task 改寫為 `[X]`，並保留其他 task 狀態不變。
4. THINK 重新計算是否仍存在已解鎖且屬於本次範圍的未完成 task；若有，返回 Phase 3，仍套用單 task 閘門。
5. WRITE 若目標 plan package 全部 tasks 已 `[X]` 且驗證通過，向使用者回報本次 plan 已交付，並詢問是否用 git commit deliver；未取得使用者同意前不得 commit。

# License & Attribution

本 skill 參考並改寫自 [GitHub Spec Kit](https://github.com/github/spec-kit)（含 `speckit-implement` 等相關流程與原始碼概念）。

Spec Kit is licensed under the MIT License. Copyright GitHub, Inc.  
完整授權條款見本目錄 [`LICENSE`](./LICENSE)。
