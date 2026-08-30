---
name: system-analysis
description: 在 plan package 的 `spec.md`、acceptance Gherkin、UI Prototyping artifact、`research.md`、`truth-delta.md` 與 `specs/truth/**` 基礎上，盤點本次需求涉及的系統介面與分析 wave，產出 plan-side `plan.md`，並把 API 與 data 介面交給 `/api-plan`、`/data-plan`。涉及前端時，review 已存在的 UI plan 與靜態雛形，不重新執行 `/ui-plan`。
disable-model-invocation: true
---

# System Analysis

`system-analysis` 是 planner orchestration skill。它本身不修改 truth，但必須把已確認的需求、acceptance、Prototyping artifact，以及本輪 plan 與既有 truth 的差異帶給後續 owner。UI plan 應已在 `/spec-by-example` 後完成；本 skill 只在涉及前端時 review 其可落地性與一致性。

# SOP

## Phase 1 -- 對齊 plan、acceptance、UI、truth 與控制平面

1. READ 讀取使用者需求、呼叫者要求、目標 plan package 的 `spec.md`、`features/acceptance/**`、`ui/**`、`research.md`、`truth-delta.md`、既有 `plan.md`、`specs/truth/techstack.md` 與相關 `specs/truth/**`。
2. READ 讀取 `templates/plan.md` 與 `templates/plan.example.md`，確認 `plan.md` 的固定結構與完成樣貌。
3. READ 讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md` 與 `.agents/constitution/skills/system-analysis/plan.md`。
4. WRITE 若 plan package 尚未有 `plan.md` 父層，建立必要目錄；本 skill 不建立或修改 `specs/truth/**`。

## Phase 2 -- 收斂系統介面盤點與 clarify 策略

1. THINK 從需求原文、`spec.md`、acceptance Gherkin、UI artifact、`research.md`、`truth-delta.md` 與現有 truth 整理本次需求部位、外部依賴、資料責任、前端責任與技術端點。
2. READ 需要判斷介面邊界時，讀取 `rules/系統介面盤點與端點歸類判準.md`。
3. DELEGATE 若缺口會改變系統介面數量、端點類型、介面邊界、truth owner 責任或 Wave 切分，呼叫 `/clarify`；未收斂前停止。

## Phase 3 -- 規劃分析 Wave 並產出 plan

1. READ 需要判斷先後與平行分組時，讀取 `rules/Wave依賴排序與平行分組判準.md`。
2. THINK 依介面依賴、truth 變更風險與可平行程度安排 Wave，確認每個 API 與 data 介面至少被一個後續 planner 承接；前端介面則必須綁定既有 UI plan 與靜態雛形作為實作參照。
3. WRITE 將系統介面盤點、Wave、分析重點與委派理由寫入 `specs/plans/NNN-<slug>/plan.md`。

## Phase 4 -- Review 前端 artifact、委派 planner 並交付

1. READ 需要判斷 planner 對應時，讀取 `rules/分析介面委派與planner對應判準.md`。
2. READ 若本次包含前端介面，review `ui/ui-plan.md` 與靜態雛形是否完整覆蓋 acceptance Journey、是否可由目前技術邊界實作，以及是否缺少成功、拒絕或錯誤狀態；若問題會改變使用者流程或畫面需求，停止受影響範圍並回交 `/ui-plan`，不得在本 skill 直接重做 Prototyping。
3. DELEGATE 依 Wave 順序將 API 介面交給 `/api-plan`、資料介面交給 `/data-plan`；每次 handoff 都必須包含 plan package path、truth root、truth-delta path、介面名稱與分析重點。
4. WRITE 向使用者回報 `plan.md`、系統介面數量、Wave 數量、前端 UI artifact review 結果、委派到哪些 planner，以及是否可進入 `/dsl-refine` 或 `/tasks`。
