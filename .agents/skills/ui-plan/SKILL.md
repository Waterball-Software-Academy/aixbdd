---
name: ui-plan
description: 根據 plan package、system-analysis handoff、truth-delta 與現有 truth，產出 plan-side `ui/**` 設計與靜態雛形。`ui-plan` 不是 truth owner，不寫入 `specs/truth/**`，但必須讀 truth-delta 以對齊本輪 API/data/feature truth 變更。
disable-model-invocation: true
---

# UI Plan

`ui-plan` 只產出本次迭代的 UI plan 與靜態雛形。UI artifact 留在 plan package，作為實作參考與評審材料，不是系統 truth。

# SOP

## Phase 1 -- 對齊 plan、truth-delta 與 UI 範圍

1. READ 讀取使用者需求、呼叫者 handoff、plan package 的 `spec.md`、`research.md`、`plan.md`、`truth-delta.md`、既有 `ui/**`，以及與 UI 有關的 `specs/truth/contracts/**`、`specs/truth/features/**`。
2. READ 讀取 `templates/ui-plan.md`、`templates/ui-plan.example.md`、`templates/prototype-entry.html`、`templates/prototype-entry.example.html`、`templates/prototype-screen.html`、`templates/prototype-screen.example.html`、`rules/高保真靜態頁面切分與Flow覆蓋判準.md` 與 `rules/靜態網站雛形與實作計畫邊界判準.md`，確認 plan-side UI artifact 與靜態雛形的完成樣貌。
3. DELEGATE 若缺口會改變使用者可見流程、畫面責任、互動入口、錯誤狀態或與 truth 的對齊方式，呼叫 `/clarify`；未收斂前停止。

## Phase 2 -- 產出 UI plan 與靜態雛形

1. THINK 依需求、truth-delta 與現有 truth 收斂畫面範圍、狀態、主要 flow、可見回饋、錯誤處理、accessibility 與 responsive 行為。
2. WRITE 將 UI 規劃寫入 `specs/plans/NNN-<slug>/ui/ui-plan.md`。
3. WRITE 依 UI plan 產出或更新 `specs/plans/NNN-<slug>/ui/*.html` 與必要靜態資源；不得寫入 `specs/truth/**`。
4. READ 回頭檢查 UI plan 與靜態雛形是否對齊 spec、truth-delta 與相關 truth；若不符合，立即修正。

## Phase 3 -- 交付後續 handoff

1. WRITE 向使用者回報 UI plan、靜態雛形路徑、引用的 truth 變更、剩餘風險，以及是否可進入 `/dsl-refine`、`/tasks` 或實作。
