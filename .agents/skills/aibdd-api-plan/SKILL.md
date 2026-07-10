---
name: aibdd-api-plan
description: >
  當 reconcile 校準 impact matrix 後、本 owner 名下有 pending impact 待落成 operation contract 時觸發。以 `read --owner aibdd-api-plan --impact-status pending` 為 worklist，依 Discovery 真相（spec.md／feature truth）推論 operation contract、在草稿上收斂後委派 boundary profile 宣告之 operation_contract_specifier 落地至 `${CONTRACTS_DIR}`，最後回寫 impact matrix。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - API Plan

把本輪 Discovery 真相中對外互動承諾的部分推導成 operation contract，並委派 boundary profile 宣告之 `operation_contract_specifier` 落地。嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許產生或修改的 artifact，只能來自下述 SOP 中明確標注的步驟：DELEGATE specifier 寫入 `${CONTRACTS_DIR}`、impact matrix CLI 維護 `${IMPACT_MATRIX_YML}`、以及把澄清結論 WRITE 進 `${PLAN_SPEC}` 的澄清區；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: 不重畫 Discovery 真相

Discovery 已 accepted 的 `${FEATURE_SPECS_DIR}/**`、`${ACTIVITIES_DIR}/**`、`${PLAN_REPORTS_DIR}/function-packaging.md`、`${PLAN_SPEC}` 需求描述全文為唯讀輸入；本 skill 不得改寫任何 feature／activity 內容、不得改 atomic rule 文字、不得新增 Scenario／Background／Examples，只能 append `${PLAN_SPEC}` 的澄清區。`${IMPACT_MATRIX_YML}` 僅能經 impact matrix CLI 維護本 skill 推論出的 contracts impact，不得手改 YAML 本體。若發現上游真相不足以推導 operation contract，必須當步 DELEGATE `/clarify` 釐清，禁止補洞。

## PRINCIPLE: 委派 specifier 落地 contract

Boundary profile 宣告之 `operation_contract_specifier.skill` 是寫入 `${CONTRACTS_DIR}/**` 的唯一合法管道；本 skill 不得手寫任何 OpenAPI 或其他 contract 格式，只負責 DERIVE caller payload 並以 DELEGATE 交給 specifier skill，一個 target 一次 DELEGATE。違者視為 ownership 違規，立即 STOP。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify` 等待回覆、以及最後一步的結尾報告。

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
- [ ] (6) 推論並收斂 operation contract。
- [ ] (7) 委派 specifier 落地 contracts。
- [ ] (8) 回寫 impact matrix。
- [ ] (9) 回報結果。
```

# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${FEATURE_SPECS_DIR}` 另含 `<<NN-functional-module>>` 借位由各 function package 的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   BOUNDARY_YML=${BOUNDARY_YML}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：稍早解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify）要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清；若使用者指名新建或不存在的 plan package，則 STOP 並提示本 skill 必須基於既有 plan package 執行。

3. 查 worklist: EXECUTE command 以 `read --owner aibdd-api-plan --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`；`$WORKLIST` 各 impact 的 quotes 為本批次本 owner 要落成 operation contract 的需求句，其中 spec 為空的 impact 為待推論並 add-spec 全新 contract 的工作、帶 inconsistent contract spec 的 impact 為待重新對齊既有 contract 檔。

4. 載入 boundary profile 與 package 範疇

   4.1 參考 `aibdd-core::references/ssot/boundary-profile-resolution.md` 解析 `$BOUNDARY_PROFILE`，自其取出 `operation_contract_specifier.{skill,format}` 作為 `$SPECIFIER`，其產出目錄對齊 `${CONTRACTS_DIR}`。

   4.2 READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`，作為待讀 feature truth 的範疇。

5. 載入分析基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次本 owner 要落成 operation contract 的需求句。

   5.2 READ `${PLAN_SPEC}` 全文作為本批次推論 operation contract 的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

   5.3 READ `$PLAN_SCOPE` 各 function package 之 `${FEATURE_SPECS_DIR}` feature truth 與 `${ACTIVITIES_DIR}` activity truth 作為 `$DISCOVERY_TRUTH`，為本批次推論 operation contract 的真相基準。

6. 推論並收斂 operation contract

   6.1 參考 `$DISCOVERY_TRUTH` 依 `$QUOTE_SEGMENTS` 並嚴格遵照 `aibdd-api-plan/rules/operation-contract-rule.md` 全部約束 REASONING operation contract，切出精準切分的 target 作為 `$CONTRACT_TARGETS`，每筆為 `{ target_path, scope, impact_id }`，`impact_id` 為驅動該 target 的 `$WORKLIST` impact；推論中一旦某項該規則的約束無法從真相滿足（切檔視角、設計取捨、operation／state 歸屬、本輪範疇等取決於使用者意圖者）蒐集成 `$ASK_BATCH`；本步只推理不落地。

   6.2 若 `$ASK_BATCH` 非空 則一次性 DELEGATE `/clarify` 批次問清，附各項來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-api-plan` 的澄清區塊，並依結論處置：判定屬 persistent state 者本 skill 不建 target，EXECUTE command `read --id <impact_id>` 取回該 impact 後 `write --id <impact_id> --owner aibdd-data-plan` 重新提供其原 quotes 與 rationale 把 owner 改派給 data plan；判定本輪不納入者更新該 impact 的 quote／rationale 標記本輪緩做並保留其 pending；再依結論回 6.1 重推，重複至 `$ASK_BATCH` 清空。

   6.3 對收斂後的 `$CONTRACT_TARGETS` DELEGATE `/analyze-and-clarify` 稽核，交辦上下文說清楚：稽核對象為 plan package `$PLAN_PACKAGE_SLUG` 需求批次 `$BATCH_NO` 的推論結果；推論目的為依 `$QUOTE_SEGMENTS` 推論產出 operation contract，且每個本 owner pending impact 的對外承諾都要有 target 承接；稽核基準為 `aibdd-api-plan/rules/operation-contract-rule.md` 與 `aibdd-core::references/ssot/spec-package-paths.md`；待稽核結果為 `$CONTRACT_TARGETS` 完整內容（附內容本身，非路徑）。

   6.4 依 `/analyze-and-clarify` 回報的 violations 處置：`fixable` 就地重推對應 `$CONTRACT_TARGETS`；`to-clarify` 併入 `$ASK_BATCH` 回 6.2 批次問清、記澄清區後重推；本輪 violations 尚有 `to-clarify` 未獲使用者回答前不得重新 DELEGATE `/analyze-and-clarify`，待全數處置完畢才回 6.3 重新稽核，重複至 violations 回空。

7. 委派 specifier 落地 contracts: 對 `$CONTRACT_TARGETS` 每個 target DELEGATE `/${SPECIFIER.skill}`，帶入該 target 作為 caller payload，遵循該 skill 自身的輸入／輸出形狀與禁令；specifier 依其認定之 `format` 寫入 `${CONTRACTS_DIR}` 下的 `target.target_path`，一個 target 一次 DELEGATE。

8. 回寫 impact matrix

   8.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

   8.2 對 `$CONTRACT_TARGETS` 每個 target，設其 `target_path` 對映之 contract 檔相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其 `impact_id` 為 impact_id；若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

   8.3 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-api-plan --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

9. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-api-plan 已以 Discovery 真相把本 owner 的 pending impact 推導成 operation contract、委派 specifier 落到 `${CONTRACTS_DIR}`，impact matrix 已同步。下面逐一列出本批次產出的 contract 與 resolve 的 impact：<逐一列出>。請檢視 API 規格設計是否正確。」本步不建議下一步，不得引導任何後續 skill 或 slash command，後續由使用者自行決定。
