# Subsection Schema 規則

- 每個 subsection 之 H2 heading 文字**必為**下表「Heading」欄字面（含大小寫與空白），不得自造別名（譬如以 `## Problems` 代替 `## Problem Space`）。
- 每個 subsection 之 body 結構**必須**遵守下表「Body 結構」欄；違反 → phase 3 step 5 ASSERT 失敗，回退。

| enum 名 | Heading | Body 結構 |
|---|---|---|
| `definition` | `## Definition` | 編號列表（`1.` / `2.` / ...），每條為一條 atomic fact，描述本 issue 想達成的事。 |
| `problem-space` | `## Problem Space` | 一或多個 `**Pn:** <短句>` 區塊，每塊含 fact 描述與 bullet list；末尾選填單一 `**Desired property**` block 列舉目標屬性。 |
| `brainstorming` | `## Brainstorming` | 一或多個 `**Sn:** <方案名>` 區塊，每塊含描述 + `pros` bullet list + `cons` bullet list；末尾選填單一比較表（columns = 評估維度，rows = Sn）。**Sn 之 n 從 1 起連續編號**，S1 為 AI 推薦首選。 |
| `solution` | `## Solution` | 一或多個 `**Policy n:** <政策名>` 或 `**Rule n:** <規則名>` 區塊，每塊以肯定式描述被採納方案的構成。**禁止**提及未被採納方案、**禁止**保留 pros / cons 對照、**禁止**回顧排序。 |
| `examples` | `## Examples` | 一或多個 fenced code / 配對情境，每例對應 `## Solution` 之某條 Policy / Rule。範例旁可帶單段描述但**不得**含 pros / cons 或方案比較。 |
| `implementation` | `## Implementation` | 編號步驟列表（`1.` / `2.` / ...），每步為一句以動詞起首之 high-level 動作。可帶 sub-bullet 補細節，但**禁止**含 hedging 或「待定」字樣。 |
| `implementation-package-structure` | `## Implementation Package Structure` | 單一 fenced block（語言標 `text` 或 `bash`），內含相對於專案根之 file tree 結構，含目錄與檔名註解。 |

## §1 識別子格式

- Pn / Sn / Policy n / Rule n **必為** ASCII 半形數字 + 連續編號從 1 起，**不得**用中文數字（「P一」「S貳」）、**不得**跳號（P1 之後直接 P3）。
- Heading 區塊以 markdown bold 標示：`**P1: <名>**`、`**S1: <名>**`、`**Policy 1: <名>**`、`**Rule 1: <名>**`。

## §2 跨 subsection 引用

- 同 issue 內可以 inline 引用其他 subsection 之識別子（譬如 `## Solution` 提及「解 P1 與 P2」）；**禁止**跨 issue 引用，跨 issue 必須 spell-out。
- `## Examples` 必須在每例旁顯式標出對應 `## Solution` 之 Policy / Rule 名稱。

## Good

- `definition` body：
  ```
  1. 把 dsl.yml schema 從 4 層巢狀壓成單層平面結構。
  2. 移除冗餘欄位（assertion_bindings、preset.variant）。
  3. 把路徑語義收斂為單一 target_part_path 概念。
  ```
- `problem-space` body：
  ```
  **P1: SSOT 錯位**
  template_generator.py 目前放在 aibdd-core ...

  - 條目 1
  - 條目 2

  **Desired property**

  - 條目 a
  - 條目 b
  ```
- `brainstorming` body 含 S1 / S2 / S3 三方案 + 比較表：
  ```
  **S1: 檔案級 plugin — ...**

  - pros: ...
  - cons: ...

  **S2: 套件級 plugin — ...**

  ...

  | 維度 | S1 | S2 | S3 |
  |---|---|---|---|
  ```
- `solution` body 僅含 Policy 1..N，無 S1 / S2 對比、無「為什麼選 S2」narrative。

## Bad

- `## Problems` 取代 `## Problem Space`（heading 字面不對）。
- `definition` body 用 bullet 而非編號（`-` 開頭），讀者無法回引「第 2 條 fact」。
- `problem-space` 用「**問題 1**」「**問題 2**」中文 + 全形，違反 Pn ASCII 編號規則。
- `brainstorming` 跳號（出現 S1 與 S3、缺 S2），讀者無法對齊比較表。
- `solution` 保留 `**Policy 1**...選此而非 S3 是因為 S3 cons 太多` narrative — 違反「不得回顧排序」，pros/cons 與 ranking 已歸屬 archived brainstorming。
- `examples` 出現但未標對應 Policy / Rule，讀者無法追溯每例落實了哪條解法。
- `implementation` 步驟寫「先 try 看看 X，如果不行再 Y」— 含 hedging，違反 as-is。
- `implementation-package-structure` 拆成多個 fenced block 並夾敘述 — 違反「單一 fenced block」，應整併為一塊。
