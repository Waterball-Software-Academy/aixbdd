---
name: aibdd-dsl-refine
description: "AIBDD DSL Refine SOP。"
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - DSL Refine

嚴格遵照底下 Principles 來執行 SOP。

## PRINCIPLE: CWD 為產出錨點

- 本 skill 與其 sub-SOP 所有經授權產生或修改的 artifact，一律落在當次執行的工作目錄 `CWD` 所涵蓋之專案／規格樹內（相對路徑自 `CWD` 解析；本檔所列 `${...}` 路徑皆以 `CWD` 為錨）。
- 【嚴禁】把應屬本流程的產物寫到 `CWD` 外的任意絕對路徑，或以「方便」為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact output contract（硬限制）

- 本 SOP 唯一允許產生或修改的 artifact，只能來自於下述 SOP 中透過 CREATE / WRITE / UPDATE 明確標注的產出物。
- 【嚴禁】除上述 target 外，其他任何 READ / SEARCH / THINK / DERIVE 所觀察到的路徑，都只可作為分析依據，不得被順手建立、寫入、更新或補骨架。

## PRINCIPLE: STRICT SOP

1. 依序不漏步：自底下列 SOP 逐一執行；每做一步，在訊息中明示該步編號。

2. 限縮延長推理：僅當 sub-SOP 當步明文標示須 `THINK / REASONING` 時，才拉長內省與推演；否則以最直接可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略與該步授權範圍無關的冗長鋪墊，以降低往返等待時間。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 conversation compact（對話摘要壓縮）之後，執行者仍要靠同一套待辦還原：目前卡在哪個 phase，該 phase 內細項又到哪一格。底下為兩層約定：外層只列 phase，進入該 phase 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- 必須工具化：Tier 0／Tier 1 對應的勾選項，要以執行環境提供的任務／待辦建立與更新能力實體化（例如 `TODOCREATE`、`TASKCREATE` 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP 當下就建好清單並隨步驟推進更新狀態。禁止只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- Tier 0（phase）：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-<slug>/`）。這一層的勾選語意是「該 phase 的細項已全部展開且依 `SOP.md` 跑完」。
- Tier 1（phase 內細項）：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡第一層編號步驟拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；進入該 phase 時以 `TODOCREATE`／`TASKCREATE`（或等效）補齊子項。

## PRINCIPLE: 提問／澄清只委派 clarify-loop

- 凡須向使用者提問或做結構化澄清（選 FP／feature、測試意圖或資料流不明、型別歸屬或欄位角色難判、是否重構 `.feature`、example 展開確認等），本 SOP 一律以**一個 `DELEGATE /clarify-loop`** 批次提問，由其決定提問工具與白話文轉譯。
- 【嚴禁】在 SOP 內 inline 逐題提問、自行 classify／branch 使用者回覆，或在聊天中自組問句代替 clarify-loop。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. SEARCH `**/arguments.yml`（在 `CWD` 下）做 parameters binding，供後續所有 phase 使用；此檔一定存在，如不存在請直接停止執行，向使用者回報：「我在 `${CWD}` 底下找不到 `**/arguments.yml`，你是否已經執行過 /aibdd-kickoff 了？」

1. RESOLVE arguments——將本 SOP 引用的 `${VAR}`（僅本 skill 用到者）透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   BOUNDARY_ISA=${BOUNDARY_ISA}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. ASSERT arguments 必備鍵齊全——對 `${AIBDD_ARGUMENTS_PATH}` 逐項檢查下列鍵存在：`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`BOUNDARY_ISA`、`CONTRACTS_DIR`、`DATA_DIR`。任一缺鍵 → 列出缺鍵，提示使用者回 `/aibdd-kickoff` 補綁後再執行，STOP。本步禁止順手補建 arguments.yml 任何欄位。

3. ASSERT 上游真相已就緒（READ-ONLY，皆為唯讀輸入，本步不得建立或改寫任何檔）——任一條件失敗即列出缺項、STOP，並提示對應上游 skill：
   - `${BOUNDARY_ISA}` 存在（kickoff isa 種子）；缺 → 提示 `/aibdd-kickoff`。
   - `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/features/*.feature` 至少一份且已列 atomic rules；缺 → 提示 `/aibdd-flows-specify`、`/aibdd-rules-specify`。
   - **api-plan 已完成**：`${CONTRACTS_DIR}` 下有實際 operation contract 檔（排除 `.gitkeep`）；缺 → 提示先執行 `/aibdd-api-plan`。
   - **data-plan 已完成**：`${DATA_DIR}` 下有 schema（DDL `.sql` 或 `.dbml`）與 `entity_to_table_mapping.yml`；缺 → 提示先執行 `/aibdd-data-plan`。

4. SELECT FP ＋ feature files（互動；使用者未指定前不得自選或開始分析）
   4.1 SEARCH `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/` 列出 function package（FP）候選（`NN-slug`），DELEGATE `/clarify-loop` 讓使用者選一個 FP（候選僅一個或為空也要問，不得自選）。BIND `$FP_SLUG`，DERIVE FP-scoped 路徑：`$FP_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}/$FP_SLUG`、`$FP_FEATURES=$FP_DIR/features`。
   4.2 SEARCH `$FP_FEATURES/*.feature` 列出 feature 候選，DELEGATE `/clarify-loop` 讓使用者選本輪要處理的 feature（可全選）。BIND `$TARGET_FEATURES[]`；空集合 → STOP。

5. ENSURE 每個 `$TARGET_FEATURES` 的 `{feature}.dsl.yml` 就緒
   - 對每個 feature，ASSERT `$FP_FEATURES/{feature}.dsl.yml` 是否存在；不存在 → 以本 skill asset `assets/dsl.template.yml` 為模版 CREATE 一份（保留 schema 註解；`dsl_steps` 下的示例佔位待 step 7 填入實際 dsl_step 時取代）。
   - dsl_step 一律 per-feature（不跨 FP／feature 共用），故本 skill 不建立 package 層共用 dsl.yml。
   - 本步只允許以模版 CREATE 上述 `{feature}.dsl.yml`，不得填任何實際 dsl_step 內容。

6. LOAD 參照真相（一次性，READ-ONLY；供 step 7 整個 loop 共用，不在 loop 內逐 example 重讀）
   - isa instruction 目錄：READ `${BOUNDARY_ISA}` 與 `$FP_DIR/*.isa.yml`，彙整可用 instruction（name／format／instruction_type／data_format／custom 契約）。這是 step 7 每條 isa_step 的 instruction 唯一可對上的真相。
   - operation contracts：READ `${CONTRACTS_DIR}/**`（operation summary／path／query／header／required 欄位），供判斷 api_call 的 operation 對應與必填欄位。
   - data schema：READ `${DATA_DIR}/**`（DDL `.sql`／`.dbml` 與 `entity_to_table_mapping.yml`），供判斷 entity 三型的表／欄位、NOT NULL 與 PK。
   - 本步只 READ，不寫任何檔。

7. LOOP 逐個分析 Example——**每次只處理一個 example，快速產出它的 dsl_step 定義後即停下與使用者互動，經回應才取下一個。**

   **【強制：小步快出＋逐例互動】** 一輪只取「單一個」example：聚焦快速跑 7.1→7.4 產出它的 dsl_step，接著 7.5 必停下互動。【嚴禁】一個回合內連做多個 example、預讀或推理後續 example、或一次把多個 example／整份 isa.yml／dsl.yml 大量寫滿。產出要快、呈現要精簡，[THINK] 與上下文牢牢限縮在當前這一個 example。

   7.1 ASSERT 跳過——該 example 的每個業務 Step 若在對應 dsl.yml 都已有 dsl_step 且狀態註解為 `[done]` → 跳過，不重做。
   7.2 THINK 測試意圖——[THINK] 對照 step 6 已載入的真相，**聚焦且快速**地讀該 example 的 GWT 全文 ＋ 所屬 `Rule:`，推出本例在驗什麼、資料怎麼流（誰建立識別碼、誰引用）、預期與 negative；只看這一個 example，不預讀後續、不做與本例無關的鋪陳。
   7.3 DERIVE＋CREATE dsl_step——對該 example 每個尚未 `[done]` 的業務 Step，快速定義：
       - 尚無對應 dsl_step → 在該 `{feature}.dsl.yml` 新建一條（format 對得上該句，`{name}` 佔位）；dsl_step 一律 per-feature，不跨 FP／feature 共用；
       - 依 `rules/builtin-instruction-decision-tree.md` 選內建型別（一句可展開多條有序 isa_step）；
       - 依 `rules/symbol-system-usage.md` 決定每個 table 欄位的符號，NOT NULL 但與情境無關的欄位填預設值（集中放 `params`）；
       - 每條 isa_step 的 instruction 必須對上 step 6 已載入的 instruction 目錄某條 format；對不上且屬內建範圍外 → 依 `rules/custom-isa-placement.md` 在 FP 層 isa.yml 宣告契約（只寫契約，Step Definition 實作留 RED）；
       - 步驟結構不利對應 isa（如一個 api_call 被拆成兩句）→ 依 `rules/feature-restructure.md` 經 `/clarify-loop` 同意後重構 `.feature`，再依新句建立 dsl_step。
       WRITE 進該 dsl_step 的 `isa_steps`（狀態註解先維持 `# [kw]`、尚未標 done）。
   7.4 DERIVE 抽變數（format 參數化）——判斷本輪 dsl_step 業務句中、會在「同 feature 其他 example」變動的字面值（人名、數字、日期等），抽成 format 變數 `{Name}`（搭配 isa_steps 的 `{{Name}}` 內插或 `params` 預設），使同 feature 後續 example 能重用同一條 dsl_step；列舉型固定描述維持字面、不抽。**抽變數與重用僅限該 feature 內，不跨 FP 及 feature**。
   7.5 STOP ＋ 互動——把本 example 剛寫入的 dsl_step **精簡呈現該 dsl.yml 片段即可（不渲染整段 .isa.feature、不貼大量內容）**，DELEGATE `/clarify-loop` 收「確認／要調整／繼續下一個」。**STOP：未得到使用者回應前，絕不進入下一個 example。** 使用者確認 → 把該 dsl_step 狀態註解改標 `# [kw] [done]`，再取下一個 example；要調整 → 回 7.3 修訂後重 7.5。

   貫穿 step 7 的規則 [DISCUSS]——卡住即委派澄清：7.2 的意圖／資料流、7.3 的型別歸屬（內建哪型／是否 custom）或欄位角色（斷言重點 vs NOT NULL 陪襯）、或步驟結構是否該重構，一旦無法有把握判定（資訊不足、規格含糊、兩解皆通），停止臆測，把卡住的點批次成疑問 DELEGATE `/clarify-loop` 澄清，取得答覆再續，不得帶猜測就寫入 dsl_step。

   本 step 允許寫入：`{feature}.dsl.yml` 的 dsl_step 與狀態註解、FP 層 isa.yml 的 custom 契約、以及經 `/clarify-loop` 同意後重構的 `.feature`（僅步驟結構、不改驗收意圖）。【嚴禁】未經 `/clarify-loop` 同意逕改 `.feature`；【嚴禁】改 spec／contracts／data／既有 isa 內建定義；【嚴禁】在 custom 寫 Step Definition 實作。 
    
