# SOP — refine 一個 example

輸入：**單一個 example**（feature 路徑 `${FEATURE}`、example 標題、worklist 列出的未完成 step）。
前置真相（isa 指令目錄／contracts／data）已由主 SOP step 4 載入，本 sub-SOP 不重讀。
`$FP_FEATURES`／`$FP_PACKAGE_DSL` 等變數沿用主 SOP。一次只處理這一個 example。

a. THINK 合規性檢查——[THINK] 依 `rules/dsl-step-reasoning.md`（A 合理性／B 前置／C VAR鏈／D Rule 一致／E 斷言）對該 example 的未完成 step 驗測試意圖與合理性。只看這一個 example、帶完整 Example 判斷。

b. 合理性未過 → 變更 example——依 `assets/change-question.template.md`：**先 EMIT 變更預覽（完整 Example ＋ 變更前/後）到對話**，再以精簡單句 DELEGATE `/clarify-loop`：
   - 同意 → 依 `rules/feature-restructure.md` 改 `.feature`，回 a 重驗。
   - 不同意 → 依回饋調整建議，回 a。
   - 全部合理（閘門過）→ 進 c+d。【嚴禁】在不正確的 step 上往下推 isa。

c+d. 逐個未完成 dsl_step（**一次一個，N 個 dsl_step → N 題，不批次**）：

   c. DERIVE＋CREATE dsl_step——在該 `{feature}.dsl.yml` 新建／補該 dsl_step（format `{name}` 佔位）：
      - **先找後建**：該 step 若在 worklist 該 example 帶 `reuse` 提示（FP 內已有同 format 定義）→ **不重建**。定義在 `{FP}/dsl.yml` → 直接引用；定義在別的 `{feature}.dsl.yml` → 依 `rules/example-refactor.md` §2 hoist 到 `$FP_PACKAGE_DSL` 兩邊共用（經 `/clarify-loop` 同意）。
      - 依 `rules/builtin-instruction-decision-tree.md` 選內建型別（一句可展開多條有序 isa_step）；
      - 依 `rules/symbol-system-usage.md` 決定 table 符號，NOT NULL 但與情境無關欄位填預設（放 `params`）；
      - 每條 isa_step 的 instruction 必對上主 SOP step 4 已載入的 isa 目錄某條 format；對不上且屬內建範圍外 → 依 `rules/custom-isa-placement.md` 在 FP 層 isa.yml 宣告契約（只寫契約，Step Definition 實作留 RED）。宣告 custom 時 **`intent` 為必填**：一句話描述該 custom 觀察到的行為（含 Given／When／Then 角色），只寫 WHAT、不寫 HOW（供下游 red-execute 推論實作）。
      - **data_table 鏡射**：instruction 對上的指令 `data_format: data_table` 且 isa.yml 有 `datatable_parameters` → 該 dsl_step 必須把欄位鏡射為 `params` ＋ `isa_steps[].table`（見 `rules/custom-isa-placement.md`），勿只寫 instruction。
      WRITE 該 dsl_step 的 `isa_steps`（尚未標 `# done`）。

   d. ISA 確認（**僅此 dsl_step**）——RUN 下列腳本算該 dsl_step 的展開；依 `assets/isa-question.template.md`：**先 EMIT 預覽（完整 Example ＋ 該 dsl_step 展開）到對話**，再以精簡單句 DELEGATE `/clarify-loop`：

      ```bash
      python3 .claude/skills/aibdd-dsl-refine/01-refine-example/scripts/cli/expand_isa.py --feature ${FEATURE} --example "<example 標題>" --dsl $FP_FEATURES/{feature}.dsl.yml --isa ${BOUNDARY_ISA}
      ```

      - 腳本若於 stderr 印出 `⚠ datatable lint`（對上 data_table 指令卻缺 params/table）→ 先回 c 補齊鏡射再重展開，勿帶空 DataTable 提問。
      - 不同意 → 回 c 調整該 dsl_step。
      - 同意 → 在該 dsl_step name 上方標 `# done`；custom 有新增 → 寫 FP 層 isa.yml。取下一個未完成 dsl_step。

e. 重構判斷——該 example 所有 dsl_step 都 `# done` 後，依 `rules/example-refactor.md`：抽變數（format 參數化）／視情況抽 DataTable；跨 feature 共用 → 寫 `$FP_PACKAGE_DSL`（`{FP}/dsl.yml`，不存在則以 `../assets/dsl.template.yml` 建）；**禁過複雜**；改 `.feature` 或搬 dsl_step 經 `/clarify-loop` 同意後才動。

   貫穿本 sub-SOP 的 [DISCUSS]——a 的意圖／合理性、c 的型別歸屬（內建哪型／是否 custom）或欄位角色（斷言重點 vs NOT NULL 陪襯）一旦無法有把握判定（資訊不足、規格含糊、兩解皆通），停止臆測，帶完整 Example DELEGATE `/clarify-loop` 澄清再續，不得帶猜測寫入。

本 sub-SOP 允許寫入：`{feature}.dsl.yml`／`$FP_PACKAGE_DSL` 的 dsl_step 與其 `# done` 註解、FP 層 isa.yml 的 custom 契約、以及經 `/clarify-loop` 同意後重構的 `.feature`（僅步驟結構、不改驗收意圖）。【嚴禁】未經 `/clarify-loop` 同意逕改 `.feature`；【嚴禁】改 spec／contracts／data／既有 isa 內建定義；【嚴禁】在 custom 寫 Step Definition 實作；【嚴禁】手改 `DSL_REFINE_PLAN.yml`（worklist 由主 SOP 重跑腳本刷新）。
