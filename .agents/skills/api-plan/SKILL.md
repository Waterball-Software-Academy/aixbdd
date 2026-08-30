---
name: api-plan
description: Truth owner skill。根據 plan package、system-analysis handoff 與現有 API truth，更新 `specs/truth/contracts/**`，支援 ADD / MODIFY / DELETE / NOOP API 語意單元，並委派 `/truth-delta` 記錄本輪 API truth 改動。
disable-model-invocation: true
---

# API Plan

`api-plan` 是 `specs/truth/contracts/**` 的 truth owner。它不再產出 package-local contract，而是直接維護整個系統目前唯一 API truth。

# SOP

## Phase 1 -- 對齊 API truth 與 plan handoff

1. READ 讀取使用者需求、呼叫者 handoff、plan package 的 `spec.md`、`research.md`、`plan.md`、`truth-delta.md`、`specs/truth/techstack.md`、既有 `specs/truth/contracts/**` 與指定後端 / API 介面名稱。
2. READ 讀取 `templates/openapi.yaml` 與 `templates/openapi.example.yaml`，確認 contract artifact 的固定結構與完成樣貌。
3. READ 讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md` 與 `.agents/constitution/skills/api-plan/openapi.md`。

## Phase 2 -- 盤點 API ADD / MODIFY / DELETE

1. THINK 依需求、handoff、現有 OpenAPI 與 truth-delta，整理本輪要新增、修改、刪除或保持不變的 operation、schema、field、response、error code 與狀態轉移語意。
2. DELEGATE 若高影響 MODIFY / DELETE 會改變既有對外契約、請求/回應形狀、錯誤模型或狀態轉移，且尚未有明確使用者決策，呼叫 `/clarify`；未收斂前停止。

## Phase 3 -- 更新 API truth

1. WRITE 直接更新 `specs/truth/contracts/**`，使 API truth 成為目前完整系統契約，不留下「仍以某 plan 契約為準」的分散引用。
2. READ 回頭檢查 contract 是否符合已載入憲法、指定介面需求與既有 truth 的相容性；若不符合，立即修正。
3. THINK 將 API truth 改動整理為語意單元層級的 ADD / MODIFY / DELETE / NOOP 列。

## Phase 4 -- 更新 truth-delta 並交付

1. DELEGATE 呼叫 `/truth-delta`，傳入 plan package、truth root、owner `/api-plan` 與本輪 API truth 改動列。
2. WRITE 向使用者回報更新的 API truth 路徑、主要操作與 schema 變更、是否進入 `/clarify`、truth-delta 更新結果，以及是否可交給後續實作或 `/tasks`。
