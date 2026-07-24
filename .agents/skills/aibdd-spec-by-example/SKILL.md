---
name: aibdd-spec-by-example
description: >
  當 reconcile 校準 impact matrix 後、本 owner 名下有 pending impact 待補 Example 時觸發。以當前 plan package 內 rules-specify 本批次補了 atomic rule 且仍存在的 `.feature` 為工作集，把每條尚無 Example 的 rule 依其類型前綴套對應 4-pattern 模板，將 Example 全部草擬完、批次釐清收斂後一次寫入，最後回寫 impact matrix。當 CWD 下找不到 arguments.yml 須先執行 /aibdd-kickoff；當尚無含 rule 的 `.feature` 須先執行 /aibdd-rules-specify。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Spec by Example

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生、修改或刪除的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE、DELETE 或 impact matrix CLI 的步驟；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、WRITE、UPDATE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本批次 plan package。
- [ ] (3) 查 worklist。
- [ ] (4) 載入 package 範疇。
- [ ] (5) 載入分析基準。
- [ ] (6) 鎖定待補 Example 的 feature。
- [ ] (7) 分類 rules。
- [ ] (8) 草擬並收斂 Example。
- [ ] (9) 一次寫入 Example。
- [ ] (10) 回寫 impact matrix。
- [ ] (11) 回報結果。
```

# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${FEATURE_SPECS_DIR}` 另含 `<<NN-functional-module>>` 借位由各 `.feature` 所屬 package 的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：rules-specify 剛處理完那個 package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify）要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 查 worklist: EXECUTE command 以 `read --owner aibdd-spec-by-example --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`；`$WORKLIST` 各 impact 的 quotes 為本批次本 owner 要補 Example 的需求句，其中 spec 為空的 impact 為待配對既有 `.feature` 的全新工作、帶 inconsistent `.feature` spec 的 impact 為待重新對齊 Example 的既有 `.feature`。

4. 載入 package 範疇: READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`。

5. 載入分析基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次本 owner 要補 Example 的需求句。

   5.2 READ `${PLAN_SPEC}` 全文作為本批次補 Example 的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

   5.3 載入既有 DSL 語料: SEARCH `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下各 package 的 `dsl.yml` 與 `*.dsl.yml`（含 `features/` 下的 `{feature}.dsl.yml`），READ 各檔 dsl_step 定義，設 `$DSL_CORPUS` 為每條 `{ name, format, params, 來源檔路徑 }`。第二輪以上的 plan 這裡會有前輪 dsl-refine 的產出；找不到任何檔（首輪）則設空集合，後續步驟不受 `dsl-step-reuse.md` 約束。

6. 鎖定待補 Example 的 feature

   6.1 SEARCH `$PLAN_SCOPE` 各 function package 之 `${FEATURE_SPECS_DIR}` 下現存的 `.feature`，依各檔 `Feature:` 業務意圖與 `$WORKLIST_QUOTES` REASONING 配對，設 `$RULE_TARGETS` 為每個被本批次 quotes 命中且仍存在的 `.feature`，每筆為 `{ feature_path, impact_id, quotes }`，其 `quotes` 為命中該檔的需求句子集；對映不到任一現存 `.feature` 的 quotes 蒐集成 `$SOURCE_GAPS`。

   6.2 若 `$SOURCE_GAPS` 非空 則一次性 DELEGATE `/clarify` 批次問清全部、附各項來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-spec-by-example` 的澄清區塊，再依結論重新配對 `$RULE_TARGETS`，重複至 `$SOURCE_GAPS` 清空。

7. 分類 rules

   7.1 對 `$RULE_TARGETS` 每個 `.feature`，解析其既有且 body 尚無 Example 的 atomic rule（已有 Example 者 skip），依各 `Rule:` 類型前綴參考 `aibdd-spec-by-example/rules/rule-pattern-taxonomy.md` REASONING 對應到 4-pattern 之一，設 `$RULES_TO_EXPAND` 為每條待補 rule，每筆為 `{ feature_path, rule_title, pattern_label, impact_id }`；缺合法前綴或對不到 pattern 者蒐集成 `$CLASSIFY_GAPS`。

   7.2 若 `$CLASSIFY_GAPS` 非空 則一次性 DELEGATE `/clarify` 批次問清全部、附各項來源 quote 與對應 `.feature`／rule 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-spec-by-example` 的澄清區塊，再依結論回到 7.1 重新分類，重複至 `$CLASSIFY_GAPS` 清空。

8. 草擬並收斂 Example

   8.1 對 `$RULES_TO_EXPAND` 每條取對應 pattern 之 `aibdd-spec-by-example/assets/templates/` 模板，依 `aibdd-spec-by-example/rules/five-elements-mapping.md`、`aibdd-spec-by-example/rules/business-language-judgments.md`、`aibdd-spec-by-example/rules/skeleton-vs-semantics-tradeoff.md` 與 `aibdd-spec-by-example/rules/example-value-rule.md` REASONING 出該 rule 的 5 個關鍵組成，再依據該 rule 對應 impact 的 `$QUOTE_SEGMENTS` REASONING 出 Example 的具體輸入與預期結果，套模板草擬其 Example block 作為 `$DRAFTS`。草擬每個 Given／When／Then 句時，先對照 `$DSL_CORPUS` 並嚴格遵守 `aibdd-spec-by-example/rules/dsl-step-reuse.md`：同語意者必沿用既有 dsl_step 的 `format` 句式填本 Example 具體值，不得另創同義異形句；語意不同才草擬新句式。推論中一旦缺少定案所需的重要資訊（模板必填元素從標題與 `$QUOTE_SEGMENTS` 推不出而須標 null 者、`example-value-rule.md` 之型別一致性約束無法從真相滿足者、以及 `dsl-step-reuse.md` 之語意對映拿不準者）蒐集成 `$ASK_BATCH`；本步不寫檔。

   8.2 若 `$ASK_BATCH` 非空 則一次性 DELEGATE `/clarify` 批次問清，附各項來源 quote 與對應 `.feature`／rule 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-spec-by-example` 的澄清區塊，再依結論回 8.1 重新草擬對應 `$DRAFTS`，重複至 `$ASK_BATCH` 清空。

   8.3 對收斂後的 `$DRAFTS` DELEGATE `/analyze-and-clarify` 稽核，交辦上下文說清楚：稽核對象為 plan package `$PLAN_PACKAGE_SLUG` 需求批次 `$BATCH_NO` 的推論結果；推論目的為依各 rule 標題與其 `$QUOTE_SEGMENTS` 套 4-pattern 模板產出 Example，且每條本批次 in-scope rule 都要有對應 Example；稽核基準為 `aibdd-spec-by-example/rules/` 下的 `rule-pattern-taxonomy.md`、`five-elements-mapping.md`、`business-language-judgments.md`、`formatter-rules.md`、`cucumber-literal-format.md`、`example-value-rule.md`、`dsl-step-reuse.md`（`$DSL_CORPUS` 非空時須逐句檢查同語意句是否沿用既有 format）；待稽核結果為 `$DRAFTS` 完整內容（附內容本身，非路徑），並附 `$DSL_CORPUS` 的 `{ name, format }` 清單供重用檢查；example 為 `aibdd-spec-by-example/assets/templates/` 的 pattern 模板。

   8.4 依 `/analyze-and-clarify` 回報的 violations 處置：`fixable` 就地重擬對應 `$DRAFTS`；`to-clarify` 併入 `$ASK_BATCH` 回 8.2 批次問清、記澄清區後重擬；本輪 violations 尚有 `to-clarify` 未獲使用者回答前不得重新 DELEGATE `/analyze-and-clarify`，待全數處置完畢才回 8.3 重新稽核，重複至 violations 回空。

9. 一次寫入 Example: 對 `$DRAFTS` 每筆 UPDATE 進其 `feature_path`，在對應 `Rule:` body 下方插入收斂後的 Example block；保留既有檔頭（`#` 註解列、`@ignore`、`Feature:` 標題）與既有 Rule，Example 不帶類型前綴（前綴僅屬 `Rule:` 標題層），不得新增 `Background` 或建立新檔。

10. 回寫 impact matrix

    10.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

    10.2 對 `$RULE_TARGETS` 每個 target，設其 `feature_path` 相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其 `impact_id` 為 impact_id；待該 `.feature` 內本批次所有 in-scope rule 都已補上 Example，若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

    10.3 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-spec-by-example --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

11. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-spec-by-example 已為 rules-specify 觸動的每個 `.feature` 把每條尚無 Example 的 atomic rule 套對應 4-pattern 模板補完 Example，疑慮已就地修正或交澄清，impact matrix 已同步。下面逐一列出本批次補上 Example 的 `.feature` 與 resolve 的 impact：<逐一列出>。接著請執行 /aibdd-plan 來產出實作規劃。」
