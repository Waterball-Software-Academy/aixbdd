# `${PLAN_SPEC}`（plan package 內 `spec.md`）Template

<!-- 填寫規則：
  1. 本檔僅含兩段：「需求描述」與置於檔案最後的「Discovery Sourcing Summary」；不要新增其他 `##` 標題或章節。
  2. 「需求描述」之下以批次（`###`）遞增紀錄需求：初始 sourcing 寫入 `### 批次 001`；之後每輪需求變更（amend）追加 `### 批次 NNN`（NNN = 既有最大批次 + 1，三位數零填充），不改寫既有批次內文。
  3. 批次標題格式固定：`### 批次 NNN（YYYY-MM-DD，初始）` 或 `### 批次 NNN（YYYY-MM-DD，需求變更）`。
  4. 批次內文為使用者該批次需求敘事之原文逐字收錄；僅允許排版換行，禁止改寫、刪減、摘要、重組措辭或拆解成需求點清單。
  5. 「Discovery Sourcing Summary」固定置於檔案最後，含指向 `discovery-sourcing.md` 報告的 pointer 與可選的執行摘要；由 sourcing／amend 步驟維護，每輪覆寫為當前真相。
-->

## 需求描述

### 批次 001（<YYYY-MM-DD>，初始）

<使用者本批次需求敘事之**原文逐字收錄**；僅允許排版換行，禁止改寫、刪減、摘要或重組措辭。>

### 批次 002（<YYYY-MM-DD>，需求變更）

<僅需求變更輪使用：使用者本批次變更敘事之**原文逐字收錄**；僅允許排版換行，禁止改寫、刪減、摘要或拆解成需求點清單。>

## Discovery Sourcing Summary

- 報告 Pointer：<相對路徑指向本 plan package 的 `discovery-sourcing.md`>
- 摘要：<可選執行摘要>
