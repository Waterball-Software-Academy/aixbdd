# SOP

0. 解析 arguments

  0.0 將本 SOP 引用的變數透過 resolver 綁定，並把 resolver stdout（每行一筆 KEY=value）原樣顯示給用戶。Resolver 非 0 退出時，STOP 並把 stderr 透傳給用戶。

    ```bash
    python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
    ACTIVITIES_DIR=${ACTIVITIES_DIR}
    CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
    FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
    IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
    PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
    PLAN_SPEC=${PLAN_SPEC}
    PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
    TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
    TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
    TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
    EOF
    ```

  0.1 READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 function package charters 與 packaging decision，derive `$function_packages`（包含本輪 plan 涉及的 `packages/NN-<slug>` 與各自職責／納入／排除；各 package 的 `${FEATURE_SPECS_DIR}` = `packages/NN-<slug>/features/`、`${ACTIVITIES_DIR}` = `packages/NN-<slug>/activities/`）。
  
  0.2 feature／activity 檔名之業務意圖用語以 `${PROJECT_SPEC_LANGUAGE}` 書寫。

1. 拆解 `${PLAN_SPEC}` 需求敘述的每一段話，標註每一段話為 `$P`，所有話的集合為 all `$P`。

  1.1 若 `$MODE` 為 RECONCILE：THINK all `$P` 限縮為 `${PLAN_SPEC}` 本批次變更章節之段落，加上 `$ENTRIES_BEFORE` 與 `$ENTRIES_AFTER` 有新增、改判、移除差異之 entries 所牽動的既有段落；兩快照一致之 entry 對應的既有段落不重新建模。

  1.2 本輪需求已不再涵蓋（不再對應任何 UAT flow／action、或需求明文淘汰）且 activity artifact 已落地之既存 spec，記入 `$OBSOLETE_ACTIVITIES` 待 DELETE。無法確證者記入 `$GAPS` 待澄清。

2. Faithful REASONING 萃取 api-wise 業務 action：

  2.1 針對每個 `$P` 萃取此段落句子嚴格遵照 `aibdd-flows-specify/02-activity-analyze/rules/apiwise-granularity.md` 的顆粒度定義萃取 RESTful-API-like 業務 action；請勿捕捉句子中不存在的元素，每個捕捉物都要明確指回 `${PLAN_SPEC}` 原文段落。

  2.2 依據 `$function_packages` 各元素職責將每個證據充足的 action 綁定至對應 function package，並 derive 其 binds_feature path 為 `${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`（<NN> 為 package 內兩位數序號，<action-slug> 依 slug 命名規則 PRINCIPLE 命名）；本步只命名不建檔。

  2.3 紀錄所有證據充足的 Action 作為 `$ACTIONS`，其中所有 binds_feature path 為 `$ACTION_FEATURES`；並將下列待澄清 action 記錄於 `$GAPS`（落入者不作節點、不予 binds_feature、不納入 `$ACTION_FEATURES`）：
    - 針對某 action 不確定其顆粒度是否正確。
    - 某段需求暗示了業務動作，但證據不足以判定 actor、觸發點或可驗收結果。
    - 某 action 無法明確歸屬到任一既有 function package。

3. Faithful REASONING 萃取 Actors

  3.1 針對 `$ACTIONS` 之每個 action 自 all `$P` 找出其觸發者作為 `$ACTORS`；`$ACTORS` 嚴格遵照 `aibdd-flows-specify/02-activity-analyze/rules/activity-actor-granularity.md`。

  3.2 若某 Action 無法判定觸發 Actor 者記入 `$GAPS`。

4. Faithful REASONING `$UAT_FLOWS` 清單（一條 flow = 一張 activity，從 actor 可理解的進場到可驗收完整旅程）：

  4.1 READ `aibdd-flows-specify/02-activity-analyze/rules/activity-diagram-granularity.md`。

  4.2 從 all `$P` 與 `$ACTIONS` 提煉獨立的 flows 作為 `$UAT_FLOWS`。`$UAT_FLOWS` 中每筆必備：
    - uat_flow_id：本輪唯一
    - summary_one_line：一句話 journey
    - activity_relpath：相對 `${ACTIVITIES_DIR}` 之唯一相對路徑，須以 `.activity` 結尾、不得以 / 開頭，檔名依 slug 命名規則 PRINCIPLE 命名
    - member_actions：本 flow 涵蓋之 actions ⊆ `$ACTIONS`，每個帶其 binds_feature。
    - variation_role：寬鬆度（happy_path／extreme_min／extreme_max／additional）選填，未知則 additional。
  
  4.3 覆蓋約束確認：每個證據充足的 Action 至少歸屬一條 flow（純查詢／唯讀且無業務狀態遷移者得依 `activity-diagram-granularity.md` 併入主流程之讀取段、不另立圖，但仍保留其 `$ACTIONS` 身分與 `$ACTION_FEATURES` 成員資格）。

5. Faithful REASONING 控制流建模：

  5.1 READ `aibdd-flows-specify/02-activity-analyze/reasoning/activity-control-flow.md`。
  
  5.2 針對 `$UAT_FLOWS` 每一條 flow，依 `activity-control-flow.md` 建模成完整有向圖，包含 name／id／initial／finals[]／actors[]／nodes[]（Action｜Decision｜Fork｜Merge｜Join，Action 節點帶 display_id、@actor、description、binds_feature）。建模未盡之處記入該 flow 的 graph gaps；將該 flow 之 name／id／initial／finals／actors／nodes 與 graph gaps 整體綁為該 flow 之 `$ACTIVITY_ANALYSIS`。

6. 針對 `$UAT_FLOWS` 每條 flow DELEGATE /aibdd-form-activity，交付該 flow 之 `$ACTIVITY_ANALYSIS` 並落檔 target_path 定為 `${ACTIVITIES_DIR}/<activity_relpath>`，既有檔需更新且建模有實質變更時帶 overwrite；所須輸入與 `.activity` 格式參照 `aibdd-form-activity/references/role-and-contract.md`。form activity 建模落檔不是停點，每次返回後依語法驗證報告處理，ok 為 false 則修正後重新建模，不停下等待使用者指示。

7. DELETE `$OBSOLETE_ACTIVITIES`：若 `$OBSOLETE_ACTIVITIES` 非空，DELETE `${ACTIVITIES_DIR}` 下該些 `.activity`，實際刪除者記為 `$DELETED_ACTIVITIES`；刪除清單於結尾報告列出。

8. WRITE `${IMPACT_MATRIX_YML}`，回寫本輪產出之 `.activity`。為每個本輪建立／改寫的 `.activity` spec，以 `(owner, spec)` 為鍵冪等 write 一個 impact，owner 一律 `aibdd-flows-specify`，`quotes` 指回 `${PLAN_SPEC}` 原文、`rationale` 寫該 `.activity` 的規格增量。只經本步 CLI command 更新 `${IMPACT_MATRIX_YML}`：

   8.0 READ `aibdd-core::impact-matrix/cli-usage.md`，取得 CLI 通用規則、資料模型、status 語意與冪等 write 各情境應用 command；詳細 flag 用法以該 reference 為準。

   8.1 針對新建或以 mode="overwrite" 改寫之每個 `.activity`，取其相對 `${TRUTH_BOUNDARY_ROOT}` 路徑（即 `packages/<NN-slug>/activities/<activity_relpath>`）為 spec，owner=`aibdd-flows-specify`、`--quote` 帶其所本之 `${PLAN_SPEC}` 原文句（≥1）、`--rationale` 寫規格增量、spec status 以 `inconsistent` 落地；以 `read` 依 owner+spec-path 定位後 found 則 `write --id` 取代、否則 `write` 新建（CLI 用法見已載入的 manual）。

   8.2 對 `$DELETED_ACTIVITIES` 之每個 `.activity`，以 `read` 取回其 impact id 後 `remove --id`（matrix `remove` 對應實際刪檔）。


9. 釐清 `$GAPS`：若 `$GAPS` 非空，逐項 DELEGATE /clarify-loop 釐清，每項附其對應 `${PLAN_SPEC}` 段落、候選 function package 或 activiy dir 作 anchor；澄清結論若改變 action 顆粒度／歸屬、flow 切分或 actor，回對應步驟重新依序執行。

10. 向使用者說道（語意不變、詞彙可改）：「OK，本輪需求的業務流程已建模完成，api-wise 業務 Action 已萃取並編織成下列可獨立驗收的 UAT flow，各對應一張 `.activity`（已通過語法驗證）：<逐一列出 activity 路徑與其一行 summary>。各 Action 與其對應 feature 的綁定路徑如下：<列出 `$ACTION_FEATURES`>。接著我會把每個 Action 落成對應的 rule-less `.feature` 骨架。」
