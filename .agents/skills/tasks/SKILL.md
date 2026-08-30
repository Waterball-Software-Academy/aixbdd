---
name: tasks
description: 根據 plan package 的 `spec.md`、`plan.md`、`research.md`、`ui/**`，以及 `truth-delta.md` 與 `specs/truth/**` 產出可直接執行的 `tasks.md`。任務切分必須依 truth-delta 的 ADD / MODIFY / DELETE / NOOP 採用不同任務模型，並在 MODIFY / DELETE 時先安排既有自動化測試影響盤點。
license: Complete terms in LICENSE
disable-model-invocation: true
---

# Tasks Skill

`tasks` 是 plan-side execution planner。它不修改 truth，只把本次 plan、truth-delta 與目前 truth 轉成 `/implement` 可逐步執行的 `tasks.md`。當 truth-delta 出現 `MODIFY` 或 `DELETE`，任務清單必須先保證既有自動化測試、step definitions、fixtures、helpers 與產品行為會被對齊最新版 truth，而不是只新增新的 BDD feature work。

# SOP

## Phase 1 -- 收斂 plan package、truth-delta 與輸出骨架

1. READ 讀取使用者需求、目標 plan package 的 `spec.md`、`plan.md`、`research.md`、`ui/**`、`truth-delta.md`，以及受影響模組的 truth feature、模組 DSL、truth-delta 實際引用的介面根共用 DSL rows、相關 contracts/data 與 `specs/truth/techstack.md`。
2. READ 讀取 `.agents/constitution/CONSTITUTION.md` 與 `.agents/constitution/shared.md`，並將其中規則視為高於本地 artifact 規範的約束。
3. READ 讀取 `rules/TruthDelta影響盤點與任務型態判準.md`，確認 ADD / MODIFY / DELETE / NOOP 的任務模型、impact audit 觸發條件與既有測試對齊要求。
4. THINK 依故事優先序、truth-delta rows、實際存在的 interface feature、同模組 DSL、實際相關的介面根共用 DSL rows 與 shared dependency，收斂任務 phase 骨架；若任一步驟沒有唯一 DSL 定義，停止受影響範圍並回交 `/dsl-refine`。

## Phase 2 -- 產生 truth-delta impact audit phase

1. THINK 若 `truth-delta.md` 含有 `MODIFY` 或 `DELETE` rows，先建立 `Truth Delta Impact Audit` phase，盤點受影響的 truth feature/dsl、既有 step definitions、fixtures、helpers、focused tests、產品分支與回歸測試面。
2. THINK 若 truth-delta 只有 `ADD` 或 `NOOP`，可省略 impact audit phase；但若 ADD 會碰到既有 shared helper 或 fixture，仍應在 Setup / Foundational task 中明列相關讀取與驗證。
3. THINK Impact Audit task 只能盤點與建立對齊工作入口，不得偷做 feature 的完整 RED / GREEN / REFACTOR。

## Phase 3 -- 依 action 建立 feature file phases

1. READ 讀取 `templates/tasks.md` 與 `templates/tasks.example.md`，確認固定章節、phase 排序、task checklist 格式，以及 action-specific task pattern 的呈現方式。
2. THINK 對 `ADD` 的 truth interface feature file，建立 `[BDD-RED] -> [BDD-GREEN] -> [BDD-REFACTOR]` 任務。
3. THINK 對 `MODIFY` 的 truth interface feature file 或 DSL 句型，建立 `[BDD-ALIGN] -> [BDD-GREEN] -> [BDD-REFACTOR]` 任務；`BDD-ALIGN` 必須先修正既有自動化測試語意，使測試表達最新版 truth。
4. THINK 對 `DELETE` 的 truth interface feature file、Rule、Example 或 DSL 句型，建立 `[BDD-REMOVE] -> [CODE-REMOVE] -> [REGRESSION]` 任務；不得讓過期測試或產品行為繼續存在。
5. THINK 對 `NOOP` rows 不建立 feature phase，但可作為 Shared Must Read 的確認依據。

## Phase 4 -- 綁定精確技術參照與依賴順序

1. THINK 為每個 Feature File phase 填入 `Shared Must Read` 與 `Boundary`；精確列出 feature、模組 DSL 與實際使用的介面根共用 DSL rows，未使用共用 row 時省略根 DSL 參照。truth 參照必須使用 `specs/truth/**` 路徑，plan 參照才使用當前 plan package 內相對路徑；不得在本 skill 重新判斷 DSL 歸屬。
2. THINK 每個 `MODIFY` / `DELETE` phase 必須在 `Shared Must Read` 或 task-level `Read` 中明列既有測試程式碼、step definitions、fixtures 或 helpers 的盤點入口；若現有落點未知，先在 Impact Audit phase 建立查找任務。
3. THINK 若驗收情境無法被現有 truth feature、同模組 DSL 與相關共用 DSL rows 唯一承接，停止受影響範圍並回交 `/dsl-refine`，不要自行搬移或補寫 DSL。

## Phase 5 -- 輸出並驗證 tasks.md

1. WRITE 依 template 骨架輸出 `specs/plans/NNN-<slug>/tasks.md`。
2. READ 回頭檢查所有任務皆為 `- [ ] T###` 格式、truth-delta 已納入 Core Inputs、ADD/MODIFY/DELETE 使用正確任務型態、MODIFY/DELETE 已安排既有測試對齊工作、truth 路徑都指向 `specs/truth/**`、plan 路徑都指向當前 plan package；若不符合，立即修正。

# License & Attribution

本 skill 參考並改寫自 [GitHub Spec Kit](https://github.com/github/spec-kit)（含 `speckit-tasks` 等相關流程與原始碼概念）。

Spec Kit is licensed under the MIT License. Copyright GitHub, Inc.  
完整授權條款見本目錄 [`LICENSE`](./LICENSE)。
