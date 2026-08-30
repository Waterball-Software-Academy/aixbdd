---
name: ui-plan
description: Prototyping skill。承接 plan package 的 `spec.md` 與 acceptance Gherkin，在 `/spec-by-example` 後產出 plan-side `ui/**` 設計與靜態雛形，供後續系統分析與前端實作使用。`ui-plan` 不是 truth owner，不寫入 `specs/truth/**`。
disable-model-invocation: true
---

# UI Plan

`ui-plan` 是 Prototyping skill，只產出本次迭代的 UI plan 與靜態雛形。UI artifact 留在 plan package。

# SOP

## Phase 1 -- 對齊 spec、acceptance 與 UI 範圍

1. READ 讀取使用者需求、plan package 的 `spec.md`、`features/acceptance/**`、既有 `ui/**`，以及與本次使用者流程有關的既有 `specs/truth/features/**`；若 acceptance Gherkin 尚未完成，停止並要求先執行 `/spec-by-example`。
2. READ 讀取 `templates/ui-plan.md`、`templates/ui-plan.example.md`、`templates/prototype-entry.html`、`templates/prototype-entry.example.html`、`templates/prototype-screen.html`、`templates/prototype-screen.example.html`、`rules/高保真靜態頁面切分與Flow覆蓋判準.md` 與 `rules/靜態網站雛形與實作計畫邊界判準.md`，確認 plan-side UI artifact 與靜態雛形的完成樣貌。
3. DELEGATE 若缺口會改變使用者可見流程、畫面責任、互動入口或錯誤狀態，呼叫 `/clarify`；未收斂前停止。

## Phase 2 -- 產出 UI plan 與靜態雛形

1. THINK 依 `spec.md`、acceptance Gherkin 與既有使用者流程收斂畫面範圍、狀態、主要 flow、可見回饋、錯誤處理、accessibility 與 responsive 行為。
2. WRITE 將 UI 規劃寫入 `specs/plans/NNN-<slug>/ui/ui-plan.md`。
3. WRITE 依 UI plan 產出或更新 `specs/plans/NNN-<slug>/ui/*.html` 與必要靜態資源；不得寫入 `specs/truth/**`。
4. READ 回頭檢查 UI plan 與靜態雛形是否完整覆蓋 `spec.md` 與 acceptance Gherkin，且產品畫面沒有混入實作說明；若不符合，立即修正。

## Phase 3 -- 交付後續 handoff

1. WRITE 回報 UI plan、靜態雛形路徑、已覆蓋的 acceptance Journey 與剩餘風險，並要求使用者 review 使用者流程、操作入口、成功／拒絕／錯誤狀態與畫面呈現。
2. WRITE 使用者確認後，明示需求與 Prototyping artifact 已完成；若 `research.md` 尚未完成，下一步進入 `/technical-research`，否則進入 `/system-analysis`。若本次涉及前端，將 UI plan 與靜態雛形列為系統分析與實作前的必要 review artifact。
