# SOP — refine 一個 example

輸入：**單一個 example**（feature 路徑 `${FEATURE}`、example 標題、worklist 列出的未完成 step；`$FP_FEATURES/{feature}.dsl-intent.md` 存在時一併輸入）。
前置真相（isa 指令目錄／contracts／data）已由主 SOP step 4 載入，本 sub-SOP 不重讀。
`$FP_FEATURES`／`$FP_PACKAGE_DSL` 等變數沿用主 SOP。一次只處理這一個 example。

a. THINK 合規性檢查——先 READ `{feature}.dsl-intent.md` 中該 example 的區塊（檔或區塊不存在則略過，自行從 Example 文本推讀），以其測試意圖、關鍵參數選值理由與逐句觀察意圖為第一手來源；再 [THINK] 依 `rules/dsl-step-reasoning.md`（A 合理性／B 前置／C VAR鏈／D Rule 一致／E 斷言）對該 example 的未完成 step 驗測試意圖與合理性。只看這一個 example、帶完整 Example 判斷。意圖檔記載與 Example 文本矛盾時不逕行擇一，帶完整 Example 與意圖記載 DELEGATE `/clarify-loop`。

b. 合理性未過 → 變更 example——依 `assets/change-question.template.md`：**先 EMIT 變更預覽（完整 Example ＋ 變更前/後）到對話**，再以精簡單句 DELEGATE `/clarify-loop`：
   - 同意 → 依 `rules/feature-restructure.md` 改 `.feature`，回 a 重驗。
   - 不同意 → 依回饋調整建議，回 a。
   - 全部合理（閘門過）→ 進 c+d。【嚴禁】在不正確的 step 上往下推 isa。

c+d. 逐個未完成 dsl_step（**一次一個推導；ISA 確認不在本 sub-SOP 內，集中於主 SOP step 10 batch review**）：

   c. DERIVE＋CREATE dsl_step——在該 `{feature}.dsl.yml` 新建／補該 dsl_step（format `{name}` 佔位）：
      - **先找後建**：該 step 若在 worklist 該 example 帶 `reuse` 提示（FP 內已有同 format 定義）→ **不重建**。定義在 `{FP}/dsl.yml` → 直接引用；定義在別的 `{feature}.dsl.yml` → 依 `rules/example-refactor.md` §2 hoist 到 `$FP_PACKAGE_DSL` 兩邊共用（經 `/clarify-loop` 同意）。
      - 依 `rules/builtin-instruction-decision-tree.md` 選內建型別（一句可展開多條有序 isa_step）；拆解組合依 `rules/builtin-composition-patterns.md`（先套模式、後判 custom），各型指令用法界限對照 `rules/builtin-instruction-usage.md`；
      - 依 `rules/symbol-system-usage.md` 決定 table 符號，NOT NULL 但與情境無關欄位填預設（放 `params`）；
      - 每條 isa_step 的 instruction 必對上主 SOP step 4 已載入的 isa 目錄某條 format；對不上且屬內建範圍外 → 依 `rules/custom-isa-placement.md` **草擬** FP 層 isa.yml 的 custom 契約並附進待 review 清單（只寫契約，Step Definition 實作留 RED；**落檔在主 SOP step 10 batch review 同意後**）。宣告 custom 時 **`intent` 為必填**：一句話描述該 custom 觀察到的行為（含 Given／When／Then 角色），只寫 WHAT、不寫 HOW（供下游 red-execute 推論實作）；`{feature}.dsl-intent.md` 對該句已有逐句意圖記載時，據以撰寫、不重新腦補。
      - **DataTable 欄位必進 params**（builtin／custom 皆適用）：該 dsl_step 若 (i) feature 句掛了 DataTable、或 (ii) 對上的指令在 isa.yml 有 `datatable_parameters` → 必須把那些欄位**全部宣告進 `params`**、並在 `isa_steps[].table` 以 `{{欄位}}` 內插（見 `rules/symbol-system-usage.md`「params 必涵蓋 DataTable 欄位」＋ `rules/custom-isa-placement.md`）。漏宣告即展開報 `DSL_EXPAND_PARAM_UNKNOWN`。
      WRITE 該 dsl_step 的 `isa_steps`（尚未標 `# done`）。

   d. 展開驗證＋累積待 review（**僅此 dsl_step，不確認、不定案**）——RUN 下列腳本算該 dsl_step 的展開：

      ```bash
      python3 .claude/skills/aibdd-dsl-refine/01-refine-example/scripts/cli/expand_isa.py --feature ${FEATURE} --example "<example 標題>" --dsl $FP_FEATURES/{feature}.dsl.yml --isa ${BOUNDARY_ISA}
      ```

      - 腳本若於 stderr 印出 `⚠ datatable lint`（對上 data_table 指令卻缺 params/table）→ 先回 c 補齊鏡射再重展開。
      - 展開成功 → 將該 dsl_step 的展開加入本 example 的待 review 清單，取下一個未完成 dsl_step。
      - 【嚴禁】在此逐 dsl_step DELEGATE `/clarify-loop` 確認、標 `# done`、或寫 FP 層 isa.yml——ISA 確認、`# done` 標記與 custom 契約落檔一律由主 SOP step 10 batch review 取得使用者同意後才執行。

e. 重構判斷——該 example 所有 dsl_step 推導完成（待 review 清單就緒）後，依 `rules/example-refactor.md`：抽變數（format 參數化）／視情況抽 DataTable；跨 feature 共用 → 寫 `$FP_PACKAGE_DSL`（`{FP}/dsl.yml`，不存在則以 `../assets/dsl.template.yml` 建）；**禁過複雜**；改 `.feature` 或搬 dsl_step 經 `/clarify-loop` 同意後才動。

   貫穿本 sub-SOP 的 [DISCUSS]——a 的意圖／合理性、c 的型別歸屬（內建哪型／是否 custom）或欄位角色（斷言重點 vs NOT NULL 陪襯）一旦無法有把握判定（資訊不足、規格含糊、兩解皆通），停止臆測，帶完整 Example DELEGATE `/clarify-loop` 澄清再續，不得帶猜測寫入。

本 sub-SOP 允許寫入：`{feature}.dsl.yml`／`$FP_PACKAGE_DSL` 的 dsl_step 定義、以及經 `/clarify-loop` 同意後重構的 `.feature`（僅步驟結構、不改驗收意圖）。`# done` 註解與 FP 層 isa.yml 的 custom 契約**不在本 sub-SOP 寫入**——由主 SOP step 10 batch review 同意後落檔。【嚴禁】未經 `/clarify-loop` 同意逕改 `.feature`；【嚴禁】改 spec／contracts／data／既有 isa 內建定義；【嚴禁】在 custom 寫 Step Definition 實作；【嚴禁】手改 `DSL_REFINE_PLAN.yml`（worklist 由主 SOP 重跑腳本刷新）。
