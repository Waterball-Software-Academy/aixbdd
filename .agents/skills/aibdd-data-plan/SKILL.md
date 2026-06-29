---
name: aibdd-data-plan
description: >
  當 reconcile 校準 impact matrix 後、本 owner 名下有 pending impact 待落成 persistent data schema 時觸發。以 `read --owner aibdd-data-plan --impact-status pending` 為 worklist，依 Discovery 真相（spec.md／feature truth）把須穩定保存的系統狀態推論成 state schema、在草稿上收斂後委派 boundary profile 宣告之 state_specifier 落地至 `${DATA_DIR}`，最後回寫 impact matrix。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Data Plan

把本輪 Discovery 真相中須穩定保存、驗證、追蹤的部分，從資料流動拆成 Domain Aggregate／Entity／Value-Object，並委派 boundary profile 宣告之 `state_specifier` 落地。嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許產生或修改的 artifact，只能來自下述 SOP 中明確標注的步驟：DELEGATE specifier 寫入 `${DATA_DIR}`、DELEGATE `/aibdd-table-to-entity` 寫入 `${DATA_DIR}/entity_to_table_mapping.yml`、impact matrix CLI 維護 `${IMPACT_MATRIX_YML}`、以及把澄清結論 WRITE 進 `${PLAN_SPEC}` 的澄清區；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: 不重畫 Discovery 真相

Discovery 已 accepted 的 `${FEATURE_SPECS_DIR}/**`、`${ACTIVITIES_DIR}/**`、`${PLAN_REPORTS_DIR}/function-packaging.md`、`${PLAN_SPEC}` 需求描述全文為唯讀輸入；本 skill 不得改寫任何 feature／activity 內容、不得改 atomic rule 文字、不得新增 Scenario／Background／Examples，只能 append `${PLAN_SPEC}` 的澄清區。`${IMPACT_MATRIX_YML}` 僅能經 impact matrix CLI 維護本 skill 推論出的 data impact，不得手改 YAML 本體。若發現上游真相不足以推導 data schema，必須當步 DELEGATE `/clarify-loop` 釐清，禁止補洞。

## PRINCIPLE: 委派 specifier 落地 schema

Boundary profile 宣告之 `state_specifier.skill` 是寫入 `${DATA_DIR}/**` 的唯一合法管道；本 skill 不得手寫任何 DBML 或其他 state 格式，只負責 DERIVE caller payload 並以 DELEGATE 交給 specifier skill，一個 entity／schema 一次 DELEGATE。違者視為 ownership 違規，立即 STOP。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify-loop` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、WRITE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本批次 plan package。
- [ ] (3) 查 worklist。
- [ ] (4) 載入 boundary profile 與 package 範疇。
- [ ] (5) 載入分析基準。
- [ ] (6) 推論並收斂 state schema。
- [ ] (7) 委派 specifier 落地 schema。
- [ ] (8) 回寫 impact matrix。
- [ ] (9) 委派建立 entity 對映。
- [ ] (10) 回報結果。
```

# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${FEATURE_SPECS_DIR}` 另含 `<<NN-functional-module>>` 借位由各 function package 的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   BOUNDARY_YML=${BOUNDARY_YML}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：稍早解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify-loop）要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清；若使用者指名新建或不存在的 plan package，則 STOP 並提示本 skill 必須基於既有 plan package 執行。

3. 查 worklist: EXECUTE command 以 `read --owner aibdd-data-plan --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`；`$WORKLIST` 各 impact 的 quotes 為本批次本 owner 要落成 state schema 的需求句，其中 spec 為空的 impact 為待推論並 add-spec 全新 schema 的工作、帶 inconsistent state spec 的 impact 為待重新對齊既有 schema 檔。

4. 載入 boundary profile 與 package 範疇

   4.1 參考 `aibdd-core::references/ssot/boundary-profile-resolution.md` 解析 `$BOUNDARY_PROFILE`，自其取出 `state_specifier.{skill,format}` 作為 `$SPECIFIER`，其產出目錄對齊 `${DATA_DIR}`。

   4.2 READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`，作為待讀 feature truth 的範疇。

5. 載入分析基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次本 owner 要落成 state schema 的需求句。

   5.2 READ `${PLAN_SPEC}` 全文作為本批次推論 state schema 的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

   5.3 READ `$PLAN_SCOPE` 各 function package 之 `${FEATURE_SPECS_DIR}` feature truth 與 `${ACTIVITIES_DIR}` activity truth 作為 `$DISCOVERY_TRUTH`，為本批次推論 state schema 的真相基準。

6. 推論並收斂 state schema

   6.1 參考 `$DISCOVERY_TRUTH` 依 `$QUOTE_SEGMENTS` 從資料流動 REASONING 建立資料狀態聚合分析、把資料客觀拆分成 Domain Aggregate／Entity／Value-Object，不得腦補，若 segment 內有須穩定保存的欄位／狀態／紀錄列舉須逐項納入 schema、不得概括，作為 `$STATE_TARGETS`，每筆為 `{ target_path, scope, impact_id }`；`target_path` 為相對 `${DATA_DIR}` 的 flat 檔案路徑（不得含 `<<NN-functional-module>>` 借位子層，見 `aibdd-core::references/ssot/spec-package-paths.md`），`impact_id` 為驅動該 schema 的 `$WORKLIST` impact；本步只推理不落地。

   6.2 對 `$STATE_TARGETS` 參考 `aibdd-data-plan/reasoning/derive-findings.md` 的分析切角 REASONING 出 `$NEED_TO_FIX` 與 `$NEED_TO_CLARIFY`。

   6.3 若 `$NEED_TO_FIX` 非空，則重推對應 `$STATE_TARGETS`，重複至 `$NEED_TO_FIX` 清空。

   6.4 若 `$NEED_TO_CLARIFY` 非空 則對其每個項目 DELEGATE `/clarify-loop` 釐清、附其來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-data-plan` 的澄清區塊，再依結論回到 6.1 重新推論對應 `$STATE_TARGETS`，重複至 `$NEED_TO_CLARIFY` 清空。

7. 委派 specifier 落地 schema: 對 `$STATE_TARGETS` 每個 target DELEGATE `/${SPECIFIER.skill}`，帶入該 target 作為 caller payload，遵循該 skill 自身的輸入／輸出形狀與禁令；specifier 依其認定之 `format` 寫入 `${DATA_DIR}` 下的 `target.target_path`，一個 entity／schema 一次 DELEGATE。

8. 回寫 impact matrix

   8.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

   8.2 對 `$STATE_TARGETS` 每個 target，設其 `target_path` 對映之 schema 檔相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其 `impact_id` 為 impact_id；若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

   8.3 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-data-plan --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

9. 委派建立 entity 對映: DELEGATE `/aibdd-table-to-entity` 產出 `${DATA_DIR}/entity_to_table_mapping.yml`，遵循該 skill 的輸入、輸出介面與規則。

10. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-data-plan 已以 Discovery 真相把本 owner 的 pending impact 推導成 state schema、委派 specifier 落到 `${DATA_DIR}`，impact matrix 已同步。下面逐一列出本批次產出的 schema 與 resolve 的 impact：<逐一列出>。請檢視資料規格設計是否正確。」本步不建議下一步，不得引導任何後續 skill 或 slash command，後續由使用者自行決定。
