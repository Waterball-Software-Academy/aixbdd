# <Rule 名稱>（<boundary-id>）

1. dsl-arrangement-rules/ 是選用目錄：只有當此 boundary 需要為某類 Gherkin block（Given / Then ...）提供「該怎麼編排」的推理規章時才建。純後端的 web-service 有；不需要的 boundary 可整個 dsl-arrangement-rules/ 不建。
2. 這些檔不是被任何 script 讀取的；它們以路徑形式被 /aibdd-spec-by-example-analyze 寫進產出的 feature 檔，成為 `# rule: <path>` breadcrumb，引導後續 Worker 來讀。所以檔案路徑本身是 load-bearing 的 citation target。
3. 分工慣例：把所有 rule type 共用的 block construction law 放在一份 shared law（例：`shared-given-law.md`）；rule-type-specific 的 delta 各自拆到 `given-delta-<type>.md`、`shared-then-*-law.md` 等 sibling，不要混回 shared 檔。

## <Block 名稱，例：Given Block>

1. 用 Decision Tree + Forces + Legality Gate 的結構，逐步引導推理者選出合法的 DSL 編排方式。
2. Decision Tree：以 numbered list 表達「先問什麼、是/否各往哪走、選哪個 plan」。
   1. <判準一>？是 → <結果>；否 → 進下一步。
3. Forces：列出推理時必須同時權衡的約束（例：只能用現有 candidate、必須維持 aggregate invariant、最小合法背景即可）。
4. Legality Gate：列出最終產出必須通過的硬性合法條件（例：不得偷跑受測主操作、不得依賴隱含 lookup）。
5. Output Expectation：說明最終要產出什麼形狀（例：一個 selected_plan，把 `<dsl>` 替換成對應 step 序列）。
