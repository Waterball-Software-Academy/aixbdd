---
name: aibdd-rules-specify
description: >
  當 reconcile 校準 impact matrix 後、本 owner 名下有 pending impact 待落成 atomic rule 時觸發。以當前 plan package 內 flows-specify 本批次觸動且仍存在的 `.feature` 為工作集，依本 owner pending impact 的 quotes 為每個 `.feature` 列舉 atomic rules（4 種類型前綴、單一主詞／單一條件、可指回需求原文），逐檔當下收斂疑慮，最後回寫 impact matrix。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Rules Specify

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生、修改或刪除的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE、DELETE 或 impact matrix CLI 的步驟；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify-loop` 等待回覆、以及最後一步的結尾報告。

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
- [ ] (6) 鎖定待補 rule 的 feature。
- [ ] (7) 列舉 atomic rules。
- [ ] (8) WRITE rules。
- [ ] (9) 回寫 rule impact。
- [ ] (10) 回報結果。
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
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：flows-specify 剛處理完那個 package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify-loop）要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 查 worklist: EXECUTE command 以 `read --owner aibdd-rules-specify --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`；`$WORKLIST` 各 impact 的 quotes 為本批次本 owner 要落成 atomic rule 的需求句，其中 spec 為空的 impact 為待配對既有 `.feature` 的全新 rule 工作、帶 inconsistent `.feature` spec 的 impact 為待重新對齊 rule 的既有 `.feature`。

4. 載入 package 範疇: READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`。

5. 載入分析基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次本 owner 要落成 atomic rule 的需求句。

   5.2 READ `${PLAN_SPEC}` 全文作為本批次列舉 atomic rule 的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

6. 鎖定待補 rule 的 feature

   6.1 SEARCH `$PLAN_SCOPE` 各 function package 之 `${FEATURE_SPECS_DIR}` 下現存的 `.feature`，依各檔 `Feature:` 業務意圖與 `$WORKLIST_QUOTES` REASONING 配對，設 `$RULE_TARGETS` 為每個被本批次 quotes 命中且仍存在的 `.feature`，每筆為 `{ feature_path, impact_id, quotes }`，其 `quotes` 為命中該檔的需求句子集；對映不到任一現存 `.feature` 的 quotes 蒐集成 `$SOURCE_GAPS`。

   6.2 若 `$SOURCE_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-rules-specify` 的澄清區塊，再依結論重新配對 `$RULE_TARGETS`，重複至 `$SOURCE_GAPS` 清空。

7. 列舉 atomic rules

   7.1 對 `$RULE_TARGETS` 每個 target 參考 `aibdd-rules-specify/rules/atomic-rule-granularity.md`，依該 target 的 `quotes` 對應的 `$QUOTE_SEGMENTS` REASONING 該 `.feature` 的 atomic rules 作為該 target 的 `$RULES`；上下文內若有表格／分級／允許值／回應欄位清單，須逐列展開成獨立 rule 或掛在 rule 下的補充行，不得概括成單條高階 rule；列舉完後須確認該 target 每個 segment 都已被 `$RULES` 完整涵蓋，未涵蓋者補列；每條須遵守該檔的顆粒度、4 種類型前綴、原子化與禁止自生規則，且可指回其來源 spec 原文；本步只推理不寫檔。

   7.2 對各 target 的 `$RULES` 參考 `aibdd-rules-specify/reasoning/derive-findings.md` REASONING 出 `$NEED_TO_FIX` 與 `$NEED_TO_CLARIFY`。

   7.3 若 `$NEED_TO_FIX` 非空，則參考 `aibdd-rules-specify/rules/atomic-rule-granularity.md` 重新推論對應 target 的 `$RULES`，重複至 `$NEED_TO_FIX` 清空。

   7.4 若 `$NEED_TO_CLARIFY` 非空 則對其每個項目 DELEGATE `/clarify-loop` 釐清、附其來源 quote 與對應 `.feature` 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-rules-specify` 的澄清區塊，再依結論回到 7.1 重新推論對應 `$RULES`，重複至 `$NEED_TO_CLARIFY` 清空。

8. WRITE rules: 對 `$RULE_TARGETS` 每個 target 參考 `aibdd-rules-specify/assets/templates/atomic-rule-format.template.feature` 把收斂後的 `$RULES` 依模板縮排與區塊結構 UPDATE 進其 `feature_path`；保留既有檔頭（`#` 註解列、`@ignore`、`Feature:` 標題），不得新增 `Background`／`Scenario`／`Examples`／表格或 Step，同一檔內既存的同一 `Rule:` 主句不重複寫入。

9. 回寫 rule impact

   9.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

   9.2 對 `$RULE_TARGETS` 每個 target，設其 `feature_path` 相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其 `impact_id` 為 impact_id；若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

   9.3 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-rules-specify --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

10. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-rules-specify 已為 flows-specify 觸動的每個 `.feature` 依本 owner 的需求 quotes 列舉並收斂 atomic rules，疑慮已就地修正或交澄清，impact matrix 已同步。下面逐一列出本批次補上 rule 的 `.feature` 與 resolve 的 impact：<逐一列出>。接著請執行 /aibdd-spec-by-example，為每條 atomic rule 補上可跑的 Example。」
