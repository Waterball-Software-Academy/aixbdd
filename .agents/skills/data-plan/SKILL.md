---
name: data-plan
description: Truth owner skill。根據 plan package、system-analysis handoff 與現有 data truth，更新 `specs/truth/data/**`，支援 ADD / MODIFY / DELETE / NOOP 資料語意單元，並委派 `/truth-delta` 記錄本輪 data truth 改動。
disable-model-invocation: true
---

# Data Plan

`data-plan` 是 `specs/truth/data/**` 的 truth owner。它維護目前系統唯一資料模型 truth，無論底層是持久化資料庫或記憶體狀態模型。

# SOP

## Phase 1 -- 對齊 data truth 與 plan handoff

1. READ 讀取使用者需求、呼叫者 handoff、plan package 的 `spec.md`、`research.md`、`plan.md`、`truth-delta.md`、`specs/truth/techstack.md`、既有 `specs/truth/data/**` 與指定資料介面名稱。
2. READ 讀取 `templates/data-model.dbml`、`templates/data-model.example.dbml` 與 `templates/data-model.example.dbdiagram`，確認資料模型 artifact 的固定結構、註記密度與完成樣貌。
3. READ 讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md` 與 `.agents/constitution/skills/data-plan/data-model.md`。

## Phase 2 -- 盤點 data ADD / MODIFY / DELETE

1. THINK 依需求、handoff、現有 DBML 與 truth-delta，整理本輪要新增、修改、刪除或保持不變的 table、enum、ref、field、index、生命週期與儲存責任。
2. DELEGATE 若高影響 MODIFY / DELETE 會改變既有資料生命週期、唯一鍵、關聯方向、公開投影或儲存模型，且尚未有明確使用者決策，呼叫 `/clarify`；未收斂前停止。

## Phase 3 -- 更新 data truth

1. WRITE 直接更新 `specs/truth/data/**`，使 data truth 成為目前完整系統資料模型，不留下「沿用某 plan 模型」的分散引用。
2. READ 回頭檢查 data truth 是否符合已載入憲法、指定資料需求、生命週期與現有 API/feature truth；若不符合，立即修正。
3. THINK 將 data truth 改動整理為語意單元層級的 ADD / MODIFY / DELETE / NOOP 列。

## Phase 4 -- 更新 truth-delta 並交付

1. DELEGATE 呼叫 `/truth-delta`，傳入 plan package、truth root、owner `/data-plan` 與本輪 data truth 改動列。
2. WRITE 向使用者回報更新的 data truth 路徑、主要實體與生命週期變更、是否進入 `/clarify`、truth-delta 更新結果，以及是否可交給後續實作或 `/tasks`。
