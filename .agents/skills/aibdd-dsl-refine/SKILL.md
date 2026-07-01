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

2. 限縮延長推理：僅當當步明文標示須 `THINK / REASONING` 時，才拉長內省與推演；否則以最直接可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成該步，省略冗長鋪墊。

## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 conversation compact 之後，執行者仍要靠同一套待辦還原進度。外層只列 phase（本檔 `# SOP` 每一步），進入 LOOP 後每個 example 再把 sub-SOP 步驟拆成子項。必須以執行環境的待辦工具（`TODOCREATE`／`TASKCREATE` 或等效）實體化，禁止只靠聊天口頭列點。

## PRINCIPLE: 提問／澄清只委派 clarify-loop

- 凡須向使用者提問或做結構化澄清，本 SOP 一律以**一個 `DELEGATE /clarify-loop`** 批次提問，由其決定提問工具與白話文轉譯。
- 各提問點用對應模版組裝 payload：選 FP → `assets/fp-question.template.md`；選 features → `assets/features-question.template.md`；example 變更 → `01-refine-example/assets/change-question.template.md`；逐 dsl_step 的 ISA 確認 → `01-refine-example/assets/isa-question.template.md`。
- **rich 內容（完整 Example、ISA 展開、DataTable）先 EMIT 到對話**（markdown 正常渲染表格與 code block），讓使用者在完整脈絡下檢視；clarify-loop 的 `context`/`question` 保持**精簡單句**並引用上方預覽。**切勿把展開／表格塞進 clarify-loop 的 question 欄位**（會被攤平成一坨、無法閱讀）。
- 【嚴禁】在 SOP 內 inline 逐題提問、自行 classify／branch 使用者回覆，或在聊天中自組問句代替 clarify-loop。

## PRINCIPLE: feature 非 SSOT，先驗 step 再推 isa

- `.feature`（SBE 產出）為**待驗證候選、非 SSOT**。每個未定義 step 先驗測試意圖與合理性（見 `01-refine-example/rules/dsl-step-reasoning.md`），確認正確才推 isa_step。
- 【嚴禁】在不正確的 step 上推理 isa_step；合理性未過即先經 `/clarify-loop`（帶完整 Example）確認後變更 `.feature`，再續。

## PRINCIPLE: worklist 只由腳本產出

- 完成度暫存 `DSL_REFINE_PLAN.yml`（專案根）一律由 `scripts/cli/build_worklist.py` 產出／刷新，**AI 不得手動修改**；查看＝READ，刷新＝重跑腳本。
- 持久真相是 dsl.yml 的 `# done` 標記；worklist 為衍生 session 暫存，啟動即刪除重建。詳見 `rules/refine-worklist-query.md`。

# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. SEARCH `**/arguments.yml`（在 `CWD` 下）做 parameters binding；此檔一定存在，如不存在停止並回報：「我在 `${CWD}` 底下找不到 `**/arguments.yml`，你是否已經執行過 /aibdd-kickoff 了？」

1. RESOLVE arguments——將下列 `${VAR}` 透過 sibling resolver 綁定，stdout 原樣 EMIT；非 0 退出則 STOP 並透傳 stderr。

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

2. ASSERT arguments 必備鍵齊全——對 `${AIBDD_ARGUMENTS_PATH}` 檢查：`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`BOUNDARY_ISA`、`CONTRACTS_DIR`、`DATA_DIR`。缺鍵 → 列出、提示 `/aibdd-kickoff`、STOP。本步禁止順手補建 arguments.yml。

3. ASSERT 上游真相已就緒（READ-ONLY；任一失敗即列缺項、STOP、提示對應 skill）：
   - `${BOUNDARY_ISA}` 存在（kickoff isa 種子）；缺 → `/aibdd-kickoff`。
   - `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/features/*.feature` 至少一份且已列 atomic rules；缺 → `/aibdd-flows-specify`、`/aibdd-rules-specify`。
   - **api-plan 已完成**：`${CONTRACTS_DIR}` 下有實際 operation contract 檔（排除 `.gitkeep`）；缺 → `/aibdd-api-plan`。
   - **data-plan 已完成**：`${DATA_DIR}` 下有 schema（DDL `.sql`／`.dbml`）與 `entity_to_table_mapping.yml`；缺 → `/aibdd-data-plan`。

4. LOAD 參照真相（一次性，READ-ONLY；供整個 LOOP 共用，不在 loop 內逐 example 重讀）：
   - isa instruction 目錄：READ `${BOUNDARY_ISA}` 與 `${TRUTH_BOUNDARY_PACKAGES_DIR}/*/*.isa.yml`（每條 name／format／instruction_type／data_format／custom 契約）。
   - operation contracts：READ `${CONTRACTS_DIR}/**`（summary／path／query／header／required）。
   - data schema：READ `${DATA_DIR}/**`（DDL／`.dbml` 與 `entity_to_table_mapping.yml`；表／欄位／NOT NULL／PK）。
   - 本步只 READ。

5. BUILD worklist——RUN 下列腳本掃出「含未完成定義 dsl step」的 FP/feature/example，產出 `DSL_REFINE_PLAN.yml`（專案根；先刪舊檔再產，read-only 對 specs）。語意見 `rules/refine-worklist-query.md`。

   ```bash
   python3 .claude/skills/aibdd-dsl-refine/scripts/cli/build_worklist.py --packages-dir ${TRUTH_BOUNDARY_PACKAGES_DIR} --out DSL_REFINE_PLAN.yml
   ```

   產出為空（全部完成）→ STOP 並回報完成；腳本回報找不到 package → STOP 並提示先完成 `/aibdd-flows-specify`。

6. SELECT FP（單選；使用者未指定前不得自選或開始分析）——READ `DSL_REFINE_PLAN.yml` 的 `fps[]`，以 `assets/fp-question.template.md` 組裝、DELEGATE `/clarify-loop` 讓使用者選一個 FP。BIND `$FP_SLUG`、`$FP_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}/$FP_SLUG`、`$FP_FEATURES=$FP_DIR/features`、`$FP_PACKAGE_DSL=$FP_DIR/dsl.yml`。

7. SELECT Features（多選）——READ worklist 選定 FP 的 `features[]`，以 `assets/features-question.template.md` 組裝、DELEGATE `/clarify-loop` 讓使用者複選。BIND `$TARGET_FEATURES[]`；空集合 → STOP。

8. ENSURE `{feature}.dsl.yml` 就緒——對每個 `$TARGET_FEATURES`，`$FP_FEATURES/{feature}.dsl.yml` 不存在 → 以 `assets/dsl.template.yml` 為模版 CREATE 空骨架。（跨 feature 共用的 `$FP_PACKAGE_DSL` 待 sub-SOP 重構步按需才建。）本步只 CREATE 空骨架，不填內容。

9. LOOP examples——對 worklist 中「屬 `$TARGET_FEATURES`、`status: pending`」的每個 example，逐一 EXECUTE the sub-sop：

   `01-refine-example/SOP.md`（輸入：該 example 的 feature 路徑 `${FEATURE}`、example 標題、worklist 列的未完成 step）

   每個 example 的 sub-SOP 返回後，**重跑 step 5 的 `build_worklist.py` 刷新 worklist**（反映剛標的 `# done`），再取下一個 `pending` example；直到 `$TARGET_FEATURES` 內無 `pending`。
   **【強制：逐 example 互動】** 嚴禁一個回合內連做多個 example；sub-SOP 內的逐 dsl_step 確認沒過前，不得跳下一個。

10. FP 級去重 + name 唯一性 gate（收尾，**強制硬閘門**）——**所有選定 feature 的 example 全部 `# done` 後**才執行；這是宣告完成前的決定性 gate，不可略過、不可只憑自我回報「已收斂」（曾發生 agent 謊報無重複、實際 16 條未上移、展開階段被阻斷）。

    a. RUN 偵測器（其 exit code 為 gate）：

    ```bash
    python3 .claude/skills/aibdd-dsl-refine/scripts/cli/detect_shared_dsl.py --packages-dir ${TRUTH_BOUNDARY_PACKAGES_DIR} --fp $FP_SLUG
    ```

    b. **exit 3（有跨 feature 重複）**：對回報的每一條都要處理，依 `01-refine-example/rules/example-refactor.md` §2 hoist 到 `$FP_PACKAGE_DSL`、刪各 `{feature}.dsl.yml` 的重複（**保留 `# done`**）。
       - **name 重複**為阻斷級（dsl.yml 規則：dsl_step name 在其 FP 解析範圍／祖先鏈內必須唯一；重複會在展開時造成名稱衝突 `DSL_DEFINITION_DUPLICATE_NAME`、阻斷整個 FP、連 dry-run 都掃不到）→ **務必全部上移**；標「同名不同 format」者先對齊 format 再上移。
       - format 重複（收斂級）一併上移。
    c. **重跑 a，直到 exit 0**。**唯有 detect exit 0 才得宣告完成**；仍 exit 3 代表還有重複，未清不得結束。
    d. 清乾淨後重跑 step 5 `build_worklist.py` 確認 worklist 仍空。本步只重構結構、不改驗收意圖。
