---
name: aibdd-flows-specify
description: >
  當 reconcile 校準矩陣後、本 owner 名下有 pending impact 待落成 spec 時觸發。以本 owner 的 pending impact 為 worklist，在 function-packaging 劃定的 package 內把需求萃取成 api-wise business action、編織可獨立驗收的 UAT flow 並交 /aibdd-form-activity 產出 `.activity`，再把每個 action 落成 rule-less `.feature` 骨架，最後回寫影響矩陣。當 CWD 下找不到 arguments.yml 須先執行 /aibdd-kickoff。當只是要為既有 `.feature` 列舉 atomic rule 則應使用 /aibdd-rules-specify。
metadata:
  user-invocable: true
  source: project-level
---

# AIxBDD - Flows Specify

嚴格遵照底下 PRINCIPLEs 來執行 SOP。 `# SOP` 下每一個編號項目為有序 step。在本 skill 執行完成前，任何需要 conversation compact 的情境必須一字不漏保留所有 PRINCIPLEs。

## PRINCIPLE: CWD 為產出錨點

本 skill 所有經授權產生或修改的 artifact，一律落在本次執行的 `CWD` 所涵蓋之 plan package 樹與 boundary packages 樹內；嚴禁把產物寫到 `CWD` 外的任意絕對路徑，或以方便為由落到未載明於當步 SOP 的其他根目錄。

## PRINCIPLE: Artifact Output Contract

本 SOP 唯一允許調用工具產生、修改或刪除的 artifact，只能來自下述 SOP 中明確標注 CREATE、WRITE、UPDATE、DELETE 或 impact matrix CLI 的步驟；其餘 READ、SEARCH、REASONING 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或刪除。

## PRINCIPLE: slug 命名規則

凡落地 filesystem 的 slug（feature／activity 等規格檔名之 `<NN>-<slug>`）之 `<slug>` 主體，一律以專案規格語系（`arguments.yml` 的 `PROJECT_SPEC_LANGUAGE`）並遵守以下規則書寫。

- 技術名詞（API field、DSL token、operationId、domain acronym 如 CRM／SOP／API／OAuth）可保留英文原文；其餘 slug body 不得整段翻成英文。
- 落地 filesystem 的 slug 與檔名須 Windows-safe，不得含 \ / : * ? " < > | 及結尾空白或點號。
- 嚴禁以 romanization（漢語拼音／注音／粵拼）、kana、romaji 等 transliteration 充當「規避該語系字元」的 fallback；slug 必須讀得懂、可直接還原為該語系文字。
- 語系為 zh-hant／zh-hans：以該字形書寫，例 `01-會員登入`；不得寫成 romanization（`01-hui-yuan-deng-ru`）或無此需求的整段英譯（`01-member-login`）。
- 語系為 en-us：slug 以英文 kebab-case 撰寫，例 `01-member-login`。
- 語系為 ja-jp：以日文書寫，禁止以 romaji 取代漢字／假名；語系為 ko-kr：以韓文（Hangul）書寫，禁止以 romaja 取代。
- 禁止無理由中英混拼的 slug（如 `01-會員-login`，除非含上述技術 token 例外）。
- 若專案規格語系缺失或無法判斷，不得自行 fallback 為英文或 romanization，須向使用者釐清。

## PRINCIPLE: 嚴格依序執行

- 依序執行 `# SOP` 下的編號 step；每做一步，在訊息中明示該步編號。
- 每個 step 或 DELEGATE 的 skill 都不是停點，立即將對應待辦標為完成並續跑下一步，不得停下來等待使用者指示或詢問是否繼續；本 skill 合法的暫停點只有三種：明文 STOP、DELEGATE `/clarify-loop` 等待回覆、以及最後一步的結尾報告。

## PRINCIPLE: 限縮推理

- 僅當 step 明文標示須 THINK、REASONING 時才進行深度推論；其餘 step 依據提示之 READ、SEARCH、CREATE、WRITE、UPDATE、DELETE、EXECUTE、DELEGATE 直接呼叫最合適的工具快速實現，禁止無關或未指示的推論行為。

## PRINCIPLE: 以待辦清單記錄進度

在本 skill 執行完成前，任何需要 conversation compact 的情境必須保留當前待辦與進度：目前正在進行 `# SOP` 的哪一個 step。待辦對應本檔 `# SOP` 每一個編號 step，用執行環境提供的待辦建立與更新能力維護（例：TODOCREATE、TASKCREATE 或等效工具），隨步驟推進更新狀態；嚴禁只在對話列點、不經工具建立的上下文待辦。

範例（語意範本；實務請用 TODOCREATE／TASKCREATE 或等效工具建立）：

```markdown
- [ ] (1) 解析 arguments。
- [ ] (2) 解析本批次 plan package。
- [ ] (3) 查 worklist。
- [ ] (4) 載入 package 範疇。
- [ ] (5) 載入建模基準。
- [ ] (6) 萃取 api-wise 業務 action。
- [ ] (7) 萃取 Actors。
- [ ] (8) 編織 UAT flow 清單。
- [ ] (9) 控制流建模。
- [ ] (10) 產出 .activity。
- [ ] (11) 盤點並刪除孤兒 .activity。
- [ ] (12) 回寫 .activity impact。
- [ ] (13) 確認待落檔 feature。
- [ ] (14) WRITE feature-file 骨架。
- [ ] (15) 盤點並刪除孤兒 .feature。
- [ ] (16) 回寫 .feature impact。
- [ ] (17) 結案完成的 impact。
- [ ] (18) 回報結果。
```

# SOP

沒有明文 THINK、REASONING 就不啟用 extended thinking。

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出含 `<<NNN-plan-slug>>` 借位者由 `$PLAN_PACKAGE_SLUG` 解析，`${ACTIVITIES_DIR}`、`${FEATURE_SPECS_DIR}`、`${TRUTH_FUNCTION_PACKAGE}` 另含 `<<NN-functional-module>>` 借位由各 spec 所屬 function package 的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：reconcile 或 function-packaging 剛處理完那個 package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續做 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問要做哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 查 worklist: EXECUTE command 以 `read --owner aibdd-flows-specify --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 屬本 owner 的 pending impact 作為 `$WORKLIST` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`。

4. 載入 package 範疇: READ `${PLAN_REPORTS_DIR}/function-packaging.md` 取各 function package 的 flagged-reason（`added`／`related`）與 rationale 作為 `$PLAN_SCOPE`。

5. 載入建模基準

   5.1 設 `$WORKLIST_QUOTES` 為 `$WORKLIST` 各 impact 的 quotes 聯集，每句標註其來源 impact id，為本批次要 formulate 成 spec 的需求句。

   5.2 設 `$STALE_ACTIVITIES` 為 `$WORKLIST` 中 spec status 為 inconsistent 且以 `.activity` 結尾的 spec，為既有待重新建模的 UAT flow。

   5.3 READ `${PLAN_SPEC}` 全文作為本批次建模的主要真相來源；依據 `$WORKLIST_QUOTES` 在 `${PLAN_SPEC}` 全文 REASONING 每個 quote 跨段落相關的完整需求上下文作為 `$QUOTE_SEGMENTS`。並設 `$BATCH_NO` 為其需求描述段最新批次號。

6. 萃取 api-wise 業務 action

   6.1 針對 `$QUOTE_SEGMENTS` 每段嚴格遵照 `aibdd-flows-specify/rules/apiwise-granularity.md` 的顆粒度定義 REASONING 萃取 RESTful-API-like 業務 action；請勿捕捉 segment 中不存在的元素，每個捕捉物都要明確指回其來源 spec 原文與來源 impact id。

   6.2 將每個證據充足的 action 綁定至 `$PLAN_SCOPE` 中某個 `added` 或 `related` 的 package：既有待更新者沿用其來源 impact 既有 spec path 所屬 package，全新者依該 action 與各 package rationale REASONING 配對；derive 其 binds_feature path 為 `${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`（`<NN>` 為 package 內兩位數序號，`<action-slug>` 依 slug 命名規則 PRINCIPLE 命名），本步只命名不建檔。

   6.3 紀錄所有證據充足的 action 作為 `$ACTIONS`，每個含 `{ action, package, binds_feature, impact_id }`，其 `{ binds_feature, impact_id }` 成對聯集為 `$ACTION_FEATURES`；下列疑點蒐集成 `$ACTION_GAPS`（落入者不作節點、不予 binds_feature、不納入 `$ACTION_FEATURES`）：
     - 針對某 action 不確定其顆粒度是否正確。
     - 某句需求暗示了業務動作，但證據不足以判定 actor、觸發點或可驗收結果。
     - 某 action 無法明確歸屬到任一 `$PLAN_SCOPE` 的 package。

   6.4 若 `$ACTION_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其來源 quote 與候選 package 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-flows-specify` 的澄清區塊，再依結論回到步驟 6.2 重新 REASONING，重複至 `$ACTION_GAPS` 清空。

7. 萃取 Actors

   7.1 針對 `$ACTIONS` 之每個 action 自 `$QUOTE_SEGMENTS` REASONING 其觸發者作為 `$ACTORS`，嚴格遵照 `aibdd-flows-specify/rules/activity-actor-granularity.md`；某 action 無法判定觸發 Actor 者蒐集成 `$ACTOR_GAPS`。

   7.2 若 `$ACTOR_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其 action 與來源 quote 作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-flows-specify` 的澄清區塊，再依結論回到步驟 7.1 重新 REASONING，重複至 `$ACTOR_GAPS` 清空。

8. 建構 `$UAT_FLOWS` 清單（一條 flow = 一張 activity，從 actor 可理解的進場到可驗收完整旅程）

   8.1 READ `aibdd-flows-specify/rules/activity-diagram-granularity.md`。

   8.2 從 `$QUOTE_SEGMENTS` 與 `$ACTIONS` REASONING 提煉獨立的 flows 作為 `$UAT_FLOWS`，每筆必備：
     - uat_flow_id：本批次唯一
     - summary_one_line：一句話 journey
     - activity_relpath：相對其 package `${ACTIVITIES_DIR}` 之唯一相對路徑，須以 `.activity` 結尾、不得以 / 開頭，檔名依 slug 命名規則 PRINCIPLE 命名
     - member_actions：本 flow 涵蓋之 actions ⊆ `$ACTIONS`，每個帶其 binds_feature
     - variation_role：寬鬆度（happy_path／extreme_min／extreme_max／additional）選填，未知則 additional

   8.3 覆蓋約束確認：每個證據充足的 action 至少歸屬一條 flow（純查詢或唯讀且無業務狀態遷移者得依 `activity-diagram-granularity.md` 併入主流程之讀取段、不另立圖，但仍保留其 `$ACTIONS` 身分與 `$ACTION_FEATURES` 成員資格）。

9. 控制流建模

   9.1 READ `aibdd-flows-specify/reasoning/activity-control-flow.md`。

   9.2 針對 `$UAT_FLOWS` 每一條 flow，依 `activity-control-flow.md` REASONING 建模成完整有向圖，含 name／id／initial／finals[]／actors[]／nodes[]（Action｜Decision｜Fork｜Merge｜Join，Action 節點帶 display_id、@actor、description、binds_feature）；建模未盡之處蒐集成 `$GRAPH_GAPS`。

   9.3 若 `$GRAPH_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其所屬 flow 與節點作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-flows-specify` 的澄清區塊，再依結論回到步驟 9.2 重新 REASONING，重複至 `$GRAPH_GAPS` 清空。

   9.4 將每條 flow 之 name／id／initial／finals／actors／nodes 整體設為該 flow 之 `$ACTIVITY_ANALYSIS`。

10. 產出 .activity: 針對 `$UAT_FLOWS` 每條 flow DELEGATE `/aibdd-form-activity`，交付該 flow 之 `$ACTIVITY_ANALYSIS` 並落檔 target_path 定為其 package 的 `${ACTIVITIES_DIR}/<activity_relpath>`，既有檔需更新且建模有實質變更時帶 overwrite；所須輸入與 `.activity` 格式參照 `aibdd-form-activity/references/role-and-contract.md`；form activity 落檔不是停點，ok 為 false 則修正後重新建模。

11. 盤點並刪除孤兒 .activity: DELETE 本批次無任何 `$ACTIONS` 指向且需求明文淘汰的既有 `.activity` 檔案；實際刪除者記為 `$DELETED_ACTIVITIES`。

12. 回寫 .activity impact

    12.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

    12.2 對本批次新建或以 overwrite 改寫的每個 `.activity`，設其相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其所 formulate 的來源 impact 為 impact_id；若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

    12.3 對 `$DELETED_ACTIVITIES` 每個 `.activity`，以 `read` 取回其所屬 impact id 與 spec_path 後 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent` 保留該 spec 並轉為 consistent；若 command 失敗則依其 violations 修正後重試直到成功。

13. 確認待落檔 feature: ASSERT `$ACTION_FEATURES` 非空，為空則 STOP 並對使用者輸出尚未偵測到任何 action 與其 binds_feature，請先完成 activity 建模再建構 feature 骨架。

14. WRITE feature-file 骨架（rule-less）

    14.1 對 `$ACTION_FEATURES` 每個 `{ binds_feature, impact_id }` 的 binds_feature path，在該 path CREATE `.feature`，維持 `.activity` action 節點與 `.feature` 一一對應；該 `.feature` 已存在時不覆寫、不重建，僅在缺檔時新建。

    14.2 `.feature` 內容只寫檔頭骨架，逐行如下，不得寫入任何 Rule:、Background、Scenario、Examples、Step：

      ```gherkin
      # @ignore - 等執行 /aibdd-red-execute 時，會只將 target Feature file 標注的 @ignore 拿掉，透過此手段來控制範疇。
      @ignore
      Feature: <表該 action 業務意圖的標題>
      ```

    14.3 Feature: 標題填該 binds_feature 對應 action 之業務意圖，不得等同實作細節或內部技術步驟名稱。

    14.4 一致性確認：每個 `.activity` action 節點之 binds_feature 都須對應到本步建立或既存之 `.feature`；某 binds_feature path 非法或無法建立者蒐集成 `$FEATURE_GAPS`。

    14.5 若 `$FEATURE_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其對應 action 與預期 feature 路徑作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-flows-specify` 的澄清區塊，再依結論修正 binds_feature 並重寫對應 `.feature`，若結論改動了某既有 `.activity` action 節點之 binds_feature 則連動更新該 `.activity`，重複至 `$FEATURE_GAPS` 清空。

15. 盤點並刪除孤兒 .feature

    15.1 設 `$OBSOLETE_FEATURES` 為本批次已無任何 `.activity` action 節點 binds_feature 指向且需求明文淘汰的既有 `.feature`。

    15.2 對 `$OBSOLETE_FEATURES` 每個先 ASSERT 已無任何 `.activity` action 節點 binds_feature 指向，仍被綁定者不刪、蒐集成 `$ORPHAN_GAPS`，確認無指向後 DELETE，實際刪除者記為 `$DELETED_FEATURES`。

    15.3 若 `$ORPHAN_GAPS` 非空 則對其每個 gap DELEGATE `/clarify-loop` 釐清、附其 `.feature` 與既有綁定作 anchor，參考 `aibdd-core::references/ssot/spec.template.md` 的澄清紀錄填寫規則把拍板結論 WRITE 進 `${PLAN_SPEC}` 批次 `$BATCH_NO`、owner `aibdd-flows-specify` 的澄清區塊，再依結論重新判定各目標刪除與否、補刪確認淘汰者，重複至 `$ORPHAN_GAPS` 清空。

16. 回寫 .feature impact

    16.1 READ `aibdd-core::references/impact-matrix/cli-usage.md`，取得通用規則、資料模型、status 語意與各 verb 應用 command。

    16.2 對本批次新建的每個 `.feature`，設其相對 `${TRUTH_BOUNDARY_ROOT}` 路徑為 spec_path、其 binds_feature 在 `$ACTION_FEATURES` 對應的來源 impact 為 impact_id；若該 impact 尚無此 spec 則 EXECUTE command `add-spec --id <impact_id> --spec <spec_path> --status consistent`，否則 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent`；若 command 失敗則依其 violations 修正後重試直到成功。

    16.3 對 `$DELETED_FEATURES` 每個 `.feature`，以 `read` 取回其所屬 impact id 與 spec_path 後 EXECUTE command `transit-status --id <impact_id> --spec <spec_path> --status consistent` 保留該 spec 並轉為 consistent；若 command 失敗則依其 violations 修正後重試直到成功。

17. 結案完成的 impact: EXECUTE command 以 `read --owner aibdd-flows-specify --impact-status pending` 取回本 owner 仍 pending 的 impact，對其中 specs 非空且全部 spec 皆為 consistent 的每個 impact EXECUTE command `transit-status --id <impact_id> --status resolved`；若 command 失敗則依其 violations 修正後重試直到成功。

18. 回報結果: 對使用者輸出（可使用不同詞彙但維持語意）「OK，/aibdd-flows-specify 已把本 owner 的 pending 需求落成 spec：受牽動的 UAT flow 已建模成 `.activity`、每個 action 已落成 rule-less `.feature` 骨架，impact matrix 已同步，孤兒 spec 已刪除。下面逐一列出本批次產出的 `.activity`、`.feature` 與 resolve 的 impact：<逐一列出>。接著請執行 /aibdd-rules-specify，為受影響的 `.feature` 補列 atomic rules。」
