---
name: tasks
description: 根據 plan package 的 `spec.md`、`plan.md`、`research.md`、`ui/**`，以及 `truth-delta.md` 與 `specs/truth/**` 產出可直接執行的 `tasks.md`。先寫 Setup 與 Foundational，測試層集中在 Phase 3 `Test Alignment & Implementation`；Feature phase 只留 Green / Refactor 或 CODE-REMOVE / REGRESSION。
disable-model-invocation: true
---

# Tasks Skill

`tasks` 是 plan-side execution planner。它不修改 truth，只把本次 plan、truth-delta 與目前 truth 轉成 `/implement` 可逐步執行的 `tasks.md`。本輪新增技術先寫 Setup；再寫 Foundational；測試層在寫產品碼之前一次對齊最新版 truth。盤點既有自動化測試只發生在寫 Phase 3 時，不得輸出成 implement task。

# SOP

## Phase 1 -- 收斂 plan package、truth-delta 與本輪 DSL 清單

1. READ 讀取使用者需求、目標 plan package 的 `spec.md`、`plan.md`、`research.md`、`ui/**`、`truth-delta.md`，以及受影響模組的 truth feature、模組 DSL、truth-delta 實際引用的介面根共用 DSL rows、相關 contracts/data 與 `specs/truth/techstack.md`。
2. READ 讀取 `.agents/constitution/CONSTITUTION.md` 與 `.agents/constitution/shared.md`，並將其中規則視為高於本地 artifact 規範的約束。
3. READ 讀取 `rules/TruthDelta影響盤點與任務型態判準.md`，確認 ADD / MODIFY / DELETE / NOOP 如何拆到 Phase 3 測試層與 Feature 產品層，以及 Setup、Foundational 與 Test Alignment 的邊界。
4. THINK 盤點本輪 Feature 用到的全部 DSL 句：含 truth-delta 有改的句，以及本輪 Feature 用到、尚無 stepdef 的句。若有 `MODIFY` 或 `DELETE`，同時盤點既有 stepdef、helper、fixture 與產品分支，只用來寫後續 task，不輸出獨立 phase。若任一句沒有唯一 DSL 定義，停止受影響範圍並回交 `/dsl-refine`。

## Phase 2 -- 產生 Setup 與 Foundational

1. THINK 若本輪有新增技術，建立 Phase 1 `Setup`：寫清套件名、配置、技術環境與最後的 smoke-test；不寫 DSL 語意、不寫產品行為。
2. THINK 若本輪沒有新增技術，省略 Setup；不得把 helper、fixture 或落點骨架塞進 Setup。
3. THINK 建立 Phase 2 `Foundational`：只建立後續實作程式、測試共用元件、入口、fixture、helper 與落點骨架；每則寫「只做／不做」。
4. THINK Setup 與 Foundational 不得偷做 Phase 3 測試層或 Feature Green。

## Phase 3 -- 建立 Test Alignment & Implementation

1. READ 讀取 `templates/tasks.md` 與 `templates/tasks.example.md`，確認 Phase 3 固定章節：`DSL 參照`、`Markers`、`Shared Must Read`、`Boundary`、`Parallel Hint`。
2. THINK 為盤點出的每一句標 `[BDD-ALIGN]`、`[BDD-REMOVE]` 或 `[BDD-RED]`；一條 DSL 一個 `[P]` task；最後一個 task 是 subagent review。
3. THINK 寫入 `DSL 參照`（每句的權威 `dsl.md` 與讀 `StepDef 實作語意` 的方法）、`Markers`、本輪要讀的句、`Boundary` 與 `Parallel Hint`。
4. THINK 本 phase 不得安排產品碼任務。

## Phase 4 -- 建立 Feature phases

1. THINK 對 `ADD` 的 truth interface feature file，建立 `[BDD-GREEN] -> [BDD-REFACTOR]`，並宣告 `Test Scope`。
2. THINK 對 `MODIFY` 的 truth interface feature file，建立 `[BDD-GREEN] -> [BDD-REFACTOR]`，並宣告 `Test Scope`。
3. THINK 對 `DELETE` 的 truth interface feature file、Rule、Example 或 DSL 句型，建立 `[CODE-REMOVE] -> [REGRESSION]`，並宣告 `Test Scope`。
4. THINK 為每個 Feature phase 填入 `Shared Must Read`、`Boundary` 與 `Test Scope`；未使用介面根共用 DSL row 時省略根 DSL 參照。truth 參照必須使用 `specs/truth/**` 路徑。
5. THINK 若驗收情境無法被現有 truth feature、同模組 DSL 與相關共用 DSL rows 唯一承接，停止受影響範圍並回交 `/dsl-refine`。

## Phase 5 -- 輸出並驗證 tasks.md

1. WRITE 依 template 骨架輸出 `specs/plans/NNN-<slug>/tasks.md`。
2. READ 回頭檢查：任務皆為 `- [ ] T###`、truth-delta 已納入 Core Inputs、沒有 Impact Audit phase、有新增技術時 Setup 寫清套件名與 smoke-test、Foundational 每則有「只做／不做」、Phase 3 已集中 ALIGN / REMOVE / RED、Feature phase 不含 `[BDD-RED]` / `[BDD-ALIGN]` / `[BDD-REMOVE]`、每個 Feature phase 有 `Test Scope`、truth 路徑都指向 `specs/truth/**`；若不符合，立即修正。
