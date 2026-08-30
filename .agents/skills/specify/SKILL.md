---
name: specify
description: 將自然語言功能需求轉成新的 plan package。每次執行都建立下一個 `specs/plans/NNN-<slug>/`，產出 `spec.md`、`checklists/requirements.md` 與初始化 `truth-delta.md`；不得改寫舊 plan package，也不得寫入 `specs/truth/**`。
disable-model-invocation: true
---

# Specify

`specify` 是每次迭代的 plan 起點。它只描述「這次要改什麼」，不直接修改系統 truth。即使本次需求是修改或刪除既有行為，也建立新的 plan package，讓舊 plan 保持歷史，讓 `specs/truth/**` 代表目前系統真相。

# SOP

## Phase 1 -- 建立新的 plan package

1. READ 讀取使用者需求、呼叫者要求、目前 `specs/plans/` 下既有編號與 `specs/truth/**` 的高層現況，確認本次功能主題、範圍、語言要求與明示限制。
2. READ 讀取 `templates/spec.template.md`、`templates/spec.example.md`、`templates/requirements-checklist.md` 與 `templates/requirements-checklist.example.md`，確認 spec 與 checklist 的固定結構。
3. READ 讀取 `rules/Feature目錄命名與輸出定位判準.md`，確認下一個 `NNN-<slug>` plan package 命名方式與輸出定位。
4. READ 讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md`、`.agents/constitution/skills/specify/spec.md` 與 `.agents/constitution/skills/specify/requirements-checklist.md`，並將其中規則視為高於本地 artifact 規範的約束。
5. WRITE 建立 `specs/plans/NNN-<slug>/` 與 `checklists/`，並初始化 `truth-delta.md` 骨架；本 phase 不建立或修改 `specs/truth/**`。

## Phase 2 -- 收斂需求缺口與 clarify 策略

1. THINK 從需求與現有 truth 整理主要使用者目標、核心流程、顯性限制、品質期望、可能的 ADD / MODIFY / DELETE 意圖與可辨識範圍邊界。
2. READ 若需要判斷哪些缺口必須升級為 clarify，讀取 `rules/Clarify升級門檻與提問預算判準.md`。
3. DELEGATE 若缺口會改變使用者故事切分、需求歸戶、主要流程、正式驗收標準，或會高影響修改/刪除既有 truth 行為，呼叫 `/clarify` 先訪談使用者；未收斂前停止，不自行假設答案。

## Phase 3 -- 重建 spec 語意骨架

1. READ 需要切分故事或需求歸戶時，讀取 `rules/使用者故事切分與優先級判準.md` 與 `rules/FR與NFR歸戶到UserStory與全域需求判準.md`。
2. THINK 依已載入規則收斂可獨立驗證的 User Stories、Priority、驗收情境、故事專屬 FR / NFR、全域需求、邊界情況、關鍵實體、成功標準與假設。
3. THINK 對涉及既有 truth 的需求，明確標示它預期是新增、修改或刪除現有系統行為，但不在本 skill 寫入 truth。

## Phase 4 -- 產出 plan artifacts 並自檢

1. WRITE 將 spec 寫入 `specs/plans/NNN-<slug>/spec.md`，將 checklist 寫入 `specs/plans/NNN-<slug>/checklists/requirements.md`。
2. READ 讀取 `rules/spec完整性與一致性自檢判準.md`，檢查使用者故事、FR / NFR、驗收情境、邊界情況、成功標準、假設與剩餘 clarify 缺口是否一致；若不符合，立即修正。

## Phase 5 -- 交付後續 handoff

1. WRITE 向使用者回報 plan package、spec、checklist、truth-delta 路徑、本次是否進入 `/clarify`、仍保留的 `NEEDS CLARIFICATION` 或假設，以及此 plan 是否可進入 `/spec-by-example` 或 `/technical-research`。
