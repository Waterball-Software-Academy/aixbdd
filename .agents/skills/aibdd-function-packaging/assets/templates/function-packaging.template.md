# `function-packaging.md` Template

<!-- 填寫規則：
  1. 檔首固定 `# Function Packaging`；其下每個 function package 一個 `##` 章節。
  2. 每章節 heading 為 `packages/NN-<slug>` 接 ` — <flagged-reason>`；內容只一行 `- rationale: ...`。
  3. flagged-reason 為本批次把該 function package 記進本文件的理由，相對 plan package 建立前 baseline，跨批次不回退：
     - `added`：本 plan 新開此 package，必須建立其目錄。
     - `related`：plan 前既存、本批次受牽動的 package；確切要增修或移除哪些 spec 由下游 owner 決定，本文件只標記其相關。
  4. 只校正本批次受牽動的章節，未受牽動的既有章節原樣保留。
-->

# Function Packaging

## `packages/<NN>-<slug>` — <flagged-reason>

- rationale: <依 flagged-reason 說明：added 為何必須新開、related 為何本批次與此既有 package 相關>
