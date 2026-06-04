# 參數設定

- **需求故事錨點** → `${PLAN_SPEC}`（`${CURRENT_PLAN_PACKAGE}/spec.md`）
- **Discovery 報告（function package charters 來源）** → `${PLAN_REPORTS_DIR}/discovery-sourcing.md`
- **Feature 規格根目錄（Action↔feature 綁定路徑；本 phase 只「綁定」不落檔）** → `${FEATURE_SPECS_DIR}`（= `${TRUTH_FUNCTION_PACKAGE}/features`，per function package 借位解析）
- **活動規格／`.activity` 根目錄** → `${ACTIVITIES_DIR}`（= `${TRUTH_FUNCTION_PACKAGE}/activities`，per function package 借位解析）
- **Activity 落地** → DELEGATE `/aibdd-form-activity`（formulation skill）；本 phase **只做建模**，`.activity` 的語法翻譯、寫檔與語法驗證一律交該 skill，**不**自行手寫 `.activity`。

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

   0.1 READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Function package charters` 與 `## Packaging decision`，DERIVE `$function_packages[]`（本輪涉及的 `packages/NN-<slug>` 與各自職責／納入／排除；各 package 的 `${FEATURE_SPECS_DIR}` = `packages/NN-<slug>/features/`、`${ACTIVITIES_DIR}` = `packages/NN-<slug>/activities/`）。同時鎖定各 package 的 `$package_naming_language`（feature／activity 檔名之業務意圖用語；缺則沿用 `${PROJECT_SPEC_LANGUAGE}`）。

1. THINK: 拆解 `${PLAN_SPEC}` 中需求敘述的每一段話，進行段落流程建模分析。標註每一段話為 $P，所有話的集合為 all $P。

2. **FAITHFUL REASONING: 萃取 api-wise 業務 Action（本輪 Action 之 SSOT）**——FOR EACH $P，萃取此段落句子中的 RESTful-API-like 業務動作，請勿捕捉句子中不存在的元素，每個捕捉物都要明確指回 `${PLAN_SPEC}` 原文段落。
    - `$Actions` = 嚴格遵照 [`rules/apiwise-granularity.md`](rules/apiwise-granularity.md) 的顆粒度定義來萃取：一個 Action ＝一次由 Actor（系統用戶）主動觸發、可獨立驗收業務結果的完整業務行動；流程編排／系統自動推進／內建處理**不**獨立成 Action。
    - **綁定與檔名（本 phase 不落檔，僅決定契約路徑）**：每個**證據充足**的 Action 綁定到**一個** `$function_package`，並 DERIVE 其 `binds_feature` = `${FEATURE_SPECS_DIR}/<NN>-<action-slug>.feature`（該 package 的 `features/` 下；`<NN>` 為 package 內兩位數序號；`<action-slug>` 以 `$package_naming_language` 表業務意圖；**檔名須 Windows-safe**：不得含 `\ / : * ? " < > |` 及結尾空白／點號）。此 `binds_feature` 即 **Phase 03 落檔 `.feature` 的契約路徑**，本 phase **只記錄、不建立**。
    - `$GAPS` = 記錄下列現象，留待步驟 7 澄清（落入者**不**在本 phase 綁節點、亦不予 `binds_feature`）：
        - 針對某 Action 不確定其顆粒度是否正確（例：疑似把系統自動推進誤收成 Action，或同一使用者意圖被拆成多個技術步驟）。
        - 某段需求暗示了業務動作，但證據不足以判定 Actor、觸發點或可驗收結果。
        - 某 Action 無法明確歸屬到任一既有 `$function_package`。

3. **FAITHFUL REASONING: 萃取 Actors**——FOR EACH `$Actions` 之 Action，自 all $P 找出其觸發者；`$Actors` 嚴格遵照 [`rules/activity-actor-granularity.md`](rules/activity-actor-granularity.md)（以 UI-facing 人類／組織角色為主軸；產品內建系統／排程／worker／DB／非入口下游第三方**不得**為 Actor）。某 Action 無法判定觸發 Actor 者記入 `$GAPS`。

4. **FAITHFUL REASONING: `$UAT_FLOWS` 清單**（一條 flow = **一張** Activity；從 actor 可理解的「進場→可驗收」完整旅程）
   - **READ** [`rules/activity-diagram-granularity.md`](rules/activity-diagram-granularity.md)
   - 從 all `$P` 與 `$Actions` 提煉**幾條**獨立 flow、因而**幾張**活動圖 → `$UAT_FLOWS`（每條 flow **一筆**）。每筆必備鍵：`uat_flow_id`（本輪唯一）、`summary_one_line`（一句話 journey：進場→可驗收）、`activity_relpath`（相對 `${ACTIVITIES_DIR}` 之唯一相對路徑；**須**以 `.activity` 結尾、**不得**以 `/` 開頭；檔名以 `$package_naming_language` 表業務意圖且 **Windows-safe**）、`member_actions`（本 flow 涵蓋之 Action 子集 ⊆ `$Actions`，每個帶其 `binds_feature`）。**寬鬆度** `variation_role`（`happy_path`／`extreme_min`／`extreme_max`／`additional`）選填，未知則 `additional`。
   - **覆蓋約束**：每個**證據充足**的 Action **至少**歸屬一條 flow（純查詢／唯讀且無業務狀態遷移者，依 `activity-diagram-granularity.md` 得併入主流程之讀取段、不另立圖，但**仍保留其 `$Actions` 身分**供 Phase 03 落檔）。

5. **FAITHFUL REASONING: 控制流建模** — **FOR EACH** `$UAT_FLOWS` 之一條 flow：**READ** [`reasoning/activity-control-flow.md`](reasoning/activity-control-flow.md)，依該檔**編號**逐項建模成完整有向圖。素材來自 **all `$P`、該筆 `summary_one_line`、以及其 `member_actions`**。產出該 flow 的 `activity_analysis.activity` 推理包：`name`／`id`／`initial`／`finals[]`／`actors[]`（`$Actors` 子集）／`nodes[]`（`Action｜Decision｜Fork｜Merge｜Join`；Action 節點帶 `display_id`、`@actor`、`description`、`binds_feature`＝步驟 2 決定之契約路徑）。建模未竟之處記入該 flow 的 `graph_gaps`。

6. **DELEGATE 落地：`/aibdd-form-activity`** — **FOR EACH** `$UAT_FLOWS`：DELEGATE `/aibdd-form-activity`，payload 依其 [`references/role-and-contract.md`](../../aibdd-form-activity/references/role-and-contract.md) 之 schema 組裝：
    - `target_path` = `${ACTIVITIES_DIR}/<activity_relpath>`（專案相對；位於該 flow 主要 function package 的 `activities/` 下）。
    - `format` = `".activity"`。
    - `reasoning.activity_analysis.activity` = 步驟 5 推理包；`reasoning.activity_analysis.graph_gaps` = 該 flow `graph_gaps`；`reasoning.activity_analysis.exit_status` = `"complete"`（若 `graph_gaps` 非空則 `"blocked"`——此時 form-activity 會拒絕落檔，該 flow 改走步驟 7 澄清後重送）。
    - **冪等**：同一 flow 對應之 `.activity` 已存在且建模無實質變更時**不重寫**；需更新既有檔才帶 `mode="overwrite"`。
    - 依 form-activity 回傳的語法驗證報告處理：`ok=false` → 修正步驟 5 建模後重送。
    - 本步**唯一允許**的 WRITE 是由 `/aibdd-form-activity` 代理落於 `${ACTIVITIES_DIR}` 下之 `.activity`；**禁止**本 phase 寫 `.feature`（那是 Phase 03，且此刻檔尚未建立——`binds_feature` 為前向契約路徑）、`dsl.yml`、contracts／data 或 activities 以外的任何檔。

7. 若 `$GAPS` 非空（**至少要逐項處理**）：DELEGATE `/clarify-loop`，帶 `delegated_intake`（`phase`=`aibdd-flows-specify/02-activity-analyze`、`raw_items`=各 GAP 一句話描述、`anchors`=對應 `${PLAN_SPEC}` 段落、候選 function package、`activities_dir`）。澄清結論若改變 Action 顆粒度／歸屬、flow 切分或 Actor，回步驟 2／3／4／5 修正後重送步驟 6。

8. 向使用者說道（語意不變、詞彙可改）：「OK，本輪需求的業務流程已建模完成——api-wise 業務 Action 已萃取，並編織成下列可獨立驗收的 UAT flow，各對應一張 `.activity`（已通過語法驗證）：<逐一列出 activity 路徑與其 `summary_one_line`>。各 Action 與其對應 feature 的綁定路徑如下：<列出 `$Actions` 與 `binds_feature`>。接著我會把每個 Action 落成對應的 rule-less `.feature` 骨架。」
