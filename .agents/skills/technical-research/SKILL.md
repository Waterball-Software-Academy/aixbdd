---
name: technical-research
description: 承接 plan package 的 `spec.md`，產出 plan-side `research.md`，並作為 truth owner 更新 `specs/truth/techstack.md`。每次執行都必須盤點 techstack truth 的 ADD / MODIFY / DELETE / NOOP，完成後委派 `/truth-delta` 更新本 plan 的 `truth-delta.md`。
disable-model-invocation: true
---

# Technical Research

`technical-research` 同時產出研究過程與技術堆疊真相：`research.md` 留在 plan package，`specs/truth/techstack.md` 是整個系統目前唯一 techstack truth。

# SOP

## Phase 1 -- 對齊 plan 與 techstack truth

1. READ 讀取使用者需求、呼叫者要求、目標 plan package 的 `spec.md`、既有 `research.md`、`truth-delta.md`、`specs/truth/techstack.md` 與必要 codebase 邊界。
2. READ 讀取 `templates/research.md`、`templates/research.example.md`、`templates/techstack.md` 與 `templates/techstack.example.md`，確認 research 與 techstack 的責任邊界。
3. READ 讀取 `rules/Research輸出定位與spec後接續判準.md`，確認 `research.md` 寫入 plan package、`techstack.md` 寫入 `specs/truth/techstack.md`。
4. READ 讀取 `.agents/constitution/CONSTITUTION.md`、`.agents/constitution/shared.md`、`.agents/constitution/skills/technical-research/research.md` 與 `.agents/constitution/skills/technical-research/techstack.md`。

## Phase 2 -- 收斂研究缺口與 truth 變更風險

1. READ 讀取 `rules/AIxBDD必問問題與起始專案介面澄清判準.md`，對過 `spec.md`、既有 `techstack.md` 與使用者這輪原話，標出尚未拍板的必問題。
2. DELEGATE 若 BDD techstack、測試策略、或起始專案下系統有哪些端尚未拍板，呼叫 `/clarify`；未問完前停止，不進入 Phase 3。
3. THINK 必問題已拍板後，再從 `spec.md` 與現有 techstack truth 整理其餘要拍板的核心決策、候選方案、已知限制、比較面向與成功條件。
4. READ 若需要判斷其餘缺口是否升級 clarify，讀取 `rules/Clarify升級門檻與研究提問預算判準.md`。
5. DELEGATE 若其餘缺口會改變決策集合、候選方案、技術邊界，或高影響修改/刪除既有 techstack truth，呼叫 `/clarify`；未收斂前停止。

## Phase 3 -- 產出 research 與更新 techstack truth

1. READ 需要確認 research 與 techstack 最小必要資訊時，讀取 `rules/研究artifact最小必要資訊判準.md` 與 `rules/techstack-artifact最小必要資訊判準.md`。
2. WRITE 將 decision-driven 研究內容寫入 `specs/plans/NNN-<slug>/research.md`。
3. WRITE 依現有 truth 與本輪決策更新 `specs/truth/techstack.md`，使其代表目前系統完整技術堆疊，不保留「以某 plan 為準」的分散說法。
4. THINK 將 techstack truth 改動整理為語意單元層級的 ADD / MODIFY / DELETE / NOOP 列。

## Phase 4 -- 更新 truth-delta 並交付

1. DELEGATE 呼叫 `/truth-delta`，傳入 plan package、truth root、owner `/technical-research` 與本輪 techstack truth 改動列。
2. WRITE 向使用者回報 `research.md`、`specs/truth/techstack.md`、`truth-delta.md`、主要技術決策與殘餘風險。
