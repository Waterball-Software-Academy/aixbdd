# `${PLAN_SPEC}`（plan package 內 `spec.md`）Template

<!-- 填寫規則：
  1. 本檔含「需求描述」與「澄清紀錄」兩段，不新增其他 `##` 章節。
  2. 「需求描述」由 reconcile 維護：以批次（`###`）遞增收錄使用者需求敘事之原文逐字，初次寫入 `### 批次 001`，之後每輪追加 `### 批次 NNN`（NNN = 既有最大批次 + 1，三位數零填充），不改寫既有批次內文。
  3. 批次標題格式固定：`### 批次 NNN（YYYY-MM-DD，初始）` 或 `### 批次 NNN（YYYY-MM-DD，需求變更）`；批次內文僅允許排版換行，禁止改寫、刪減、摘要、重組措辭或拆解成需求點清單。
  4. 「澄清紀錄」由各 planner append /clarify-loop 拍板結論，append-only，既有區塊不改寫，且不得改動「需求描述」段。
  5. 每筆澄清為一個 `### 批次 <NNN> <planner-skill>: <question-summary>` 區塊，掛在觸發它的批次號 `<NNN>` 下；`<planner-skill>` 為提出澄清的 owner，`<question-summary>` 為該澄清的一句話問題摘要。
  6. 區塊內 `location` 指回該澄清所繫的檔；`question` 和 `answer` 各自原文逐字收錄問題與答案。
  7. 建立空骨架時含兩段章節標題即可。
-->

## 需求描述

### 批次 001（<YYYY-MM-DD>，初始）

<使用者本批次需求敘事之原文逐字收錄；僅允許排版換行，禁止改寫、刪減、摘要或重組措辭。>

### 批次 002（<YYYY-MM-DD>，需求變更）

<僅需求變更輪使用：使用者本批次變更敘事之原文逐字收錄；僅允許排版換行，禁止改寫、刪減、摘要或拆解成需求點清單。>

## 澄清紀錄

### 批次 <NNN> <planner-skill>: <question-summary>

- location: <file-path>
- question:
  ```
  <question-verbatim>
  ```
- answer:
  ```
  <answer-verbatim>
  ```
