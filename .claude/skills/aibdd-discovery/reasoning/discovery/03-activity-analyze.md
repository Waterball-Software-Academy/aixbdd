---
rp_type: reasoning_phase
id: discovery.03-activity-analyze
context: discovery
slot: "03"
name: Activity Analyze
variant: none
consumes:
  - name: source_material_bundle
    kind: required_axis
    source: upstream_rp
    required: true
  - name: impact_scope
    kind: required_axis
    source: upstream_rp
    required: true
  - name: filename_axes
    kind: required_axis
    source: caller
    required: true
  - name: hallucination_detection_checklist
    kind: reference
    source: reference
    required: true
produces:
  - name: activity_analyses
    kind: material_bundle
    terminal: false
    cardinality: list
    item: activity_analysis
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: 偵測到流程結構歧義（Class 2）時輸出題目；無歧義則 questions 為空
downstream:
  - discovery.04-activity-clarify
  - discovery.05-atomic-rules
---

# Activity 前置分析

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + target boundary / function package context（原始想法、目標 boundary、目標功能模組）
    required_fields:
      - raw_idea
      - relevance
      - target_boundary
      - target_function_package
    optional_fields:
      - filename_axes
    completeness_check:
      rule: source material 足以定位本次 Activity 的 target boundary / function package
      on_missing: ASK
    examples:
      positive:
        - raw idea 具可觀察 actor action，且已綁定 target boundary truth
      negative:
        - raw idea 只有資料欄位或內部實作要求
  - name: impact_scope
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: existing flow / atomic rule / actor / state / operation trigger impact objects
    required_fields:
      - impacts
    optional_fields:
      - blocking_gaps
    completeness_check:
      rule: Activity Analyze 只消費 impact scope，不重新掃 truth 或重建 sourcing
      on_missing: STOP
    examples:
      positive:
        - impact object 指向既有 Activity action id 或 new_behavior gap
      negative:
        - Activity Analyze 自行重新搜尋 `${SPECS_ROOT_DIR}` 產生第二份 relevance matrix
  - name: filename_axes
    source:
      kind: caller
      path: BDD_CONSTITUTION_PATH §5.1
    granularity: Activity / feature target path 命名軸
    required_fields:
      - filename.convention
      - filename.title_language
    optional_fields: []
    completeness_check:
      rule: filename axes 已由 bdd-constitution 宣告
      on_missing: STOP
    examples:
      positive:
        - convention=kebab-all-lower, title_language=en
      negative:
        - plugin 自行猜測檔名規則
```

### 1.2 Search SOP

1. 先把這一輪要用來建 Activity 的三條主軸讀進來：raw/source material、impact scope、檔名軸。
   `$bundle` = READ source_material_bundle
   `$impact_scope` = READ impact_scope
   `$axes` = READ filename_axes

2. 再把 raw idea 與 impact objects 拆成後面真的會用到的來源單位，至少要能辨識 actor、action、condition、branch、parallel、loop、binding、sequence、operation trigger。
   `$raw_units` = PARSE `$bundle.raw_idea` and `$impact_scope.impacts` into raw actor / action / decision / branch / parallel / loop / binding / sequence cues

3. 這一步只准消費 `source_material_bundle`、`impact_scope`、`filename_axes`；不得自行重掃 truth 或再建第二份 sourcing。
   ASSERT `$bundle.raw_idea` non-empty
   ASSERT `$impact_scope.impacts` exists
   ASSERT `$axes.filename.convention` non-empty
   ASSERT this RP does not read truth artifacts outside `source_material_bundle` / `impact_scope`

## 2. Modeling Element Definition

本 RP 的 reasoning 目的，是把 raw idea 分類成 graph driver Activity model 支援的元素。graph driver 的 Activity 資料結構是本模型的 SSOT；Reasoning SOP 中可以有任意多中間變數、判斷、草稿、檢查，但最後必須透過 `CLASSIFY` verb 把已分類元素加入本節定義的 model elements。Reducer 只把這些 elements 收斂成 `activity_analysis`，不新增 Activity model 語意。

```yaml
modeling_element_definition:
  output_model: activity_analysis
  element_rules:
    element_vs_field:
      element: "Activity、Actor、Initial、Final、或 flow node 中可被獨立承載的 entity"
      field: "只能隸屬於某個 element 的屬性或 nested object；不得提升為獨立 element"

  elements:
    Activity:
      role: "單一 .activity 檔的流程模型；對應一個 UAT flow"
      fields:
        file_path: string
        version: number
        name: string
        id: stable_id
        initial: Initial
        finals: Final[]
        actors: Actor[]
        nodes: [Action, Decision, Fork, Merge, Join]
      invariants:
        - "name / id / initial / finals / actors / nodes 對齊 graph driver Activity state"
        - "initial exactly one"
        - "finals one or more"
        - "nodes 只包含 Action | Decision | Fork | Merge | Join"
        - "一個 Activity 對應一個 UAT flow（= 從 actor 入口到 actor 驗收的完整 end-to-end 旅程）；一個 functional package 可以產生多個 Activity 檔"
        - "UAT flow 邊界偵測：(a) actor-entry → actor-verification arc；(b) 可獨立 demo 的 swimlane diagram；(c) 不與 sibling flow 共享內部狀態"
        - "**Self-contained invariant**：同一個 lifecycle 中，若 phase A 的 postcondition 是 phase B 的必要 precondition，且使用者驗收的是整段 journey，則 A/B 不得拆成 sibling Activity；必須合併成單一 actor-entry → verification / terminal arc"
        - "**Rejection-rework loop 屬同一 UAT flow**：被某 actor 拒絕 → 買家修正 / 補資料 → 重新送出 → 再次評估 → 最終通過或最終拒絕，整段屬於同一個 UAT flow，不拆分為兩個 Activity（業務領域無關 — 大額訂單審退-補資料-重審、訂單退回-修正-重送、優惠碼核銷失敗-修正-重試 等模式皆屬此 invariant）"
        - "**多 actor 端到端 UAT flow**：當同一 functional package 內，actor A 的 setup-time command（如建立 journey、指派學員）產生的狀態，是 actor B 後續 execution（如執行 SOP、記錄回應）的前置條件時，A 與 B 屬於**同一 UAT flow**，整段以單張 Activity 表達（多 STEP、多 Actor）；不得因 actor 不同而拆成多張 Activity"
        - "跨 **functional package** 的前置動作（如登入屬 identity-management package、建立客戶主檔屬 customer-master package）只放在 [INITIAL] narrative，不建立 Action 節點；**注意**：跨 package ≠ 跨 actor — 同一 package 內不同 actor 的動作仍須建立 Action 節點"
        - "**Query-only flow 不獨立成 Activity**：純 query / read 操作（無業務狀態變遷、無多 actor handoff、無業務驗收 milestone）不建立獨立 Activity；以 feature file 內部 Rules 表達即可。Query 只在伴隨明確 actor-entry → verification arc 與業務 milestone（例如「查詢結果觸發後續決策」）時才升格為 Activity"
        - "**Feature-index anti-pattern**：若候選 Activity 只是把多個 feature bindings 依時間順序排成 checklist，而沒有顯式 state transition、decision、loop、terminal verification，則不得產出 Activity，必須列為 graph_gap / 歧義"

    Actor:
      role: "Activity.actors[] 中的參與者"
      fields:
        id: stable_id
        name: string
        actor_type: external_user
        binding: string | null
      invariants:
        - "name 在同一 Activity 內唯一"
        - "Activity action 一律由 UI-facing actor 觸發；product system / third-party system 不升格為 Actor，詳見 `../../references/rules/activity-action-granularity.md`"
        - "binding 是 Actor 的 field，不是獨立 model element"

    Initial:
      role: "流程入口"
      fields:
        id: stable_id
        next: node_ref | null
      invariants:
        - "next 指向第一個 flow node；null 表示缺 first action"
        - "不承載 actor / action / binding / CiC"

    Final:
      role: "流程終點"
      fields:
        id: stable_id
        next: null
      invariants:
        - "next 必須恆為 null"
        - "不承載 actor / action / binding / CiC"
        - "流程只能經由 explicit Action 或 terminal compact branch 抵達 Final；不得靠 comment-only 終止"

    Action:
      role: "Activity.nodes[] 中的可執行節點；對應 ui_step / command / query"
      fields:
        id: stable_id
        display_id: string
        action_type: ui_step | command | query
        name: string
        actor: actor_ref
        binds_feature: string
        next: node_ref | null
      invariants:
        - "ui_step / command / query 是 action_type 變體，不另造 BackendOverlay element"
        - "actor 必須指向 actors[] 中的 Actor.id"
        - "binds_feature 是 Action 的 field，不另造 Binding element"
        - "binds_feature 必須為非 null（矩形 = feature file）；每個 Action 節點都必須對應恰好一個 feature file；無法對應 feature file 的 actor 動作不得建立 Action 節點"
        - "**Distinct operation invariant**：若 raw idea / impact scope 已明示多個可被獨立驗收、獨立命名、或獨立觸發的 operation trigger（例如不同指令、不同 API、不同招式 / 行動類型），則它們不得共用同一 `binds_feature`；必須拆成多個 Action，各自綁定不同 feature"
        - "@command 與 @query feature 必須分開；action_type=command 的 Action 不可 binds_feature 指向 @query feature，反之亦然"
        - "display_id 是 DSL positional id，不是 stable id"
        - "每個 Action 代表從 UI 開始的一個完整業務行動，並包含跨多個 system boundary 後已處理好的 postcondition；不得拆成循序圖顆粒度，詳見 `../../references/rules/activity-action-granularity.md`"

    Decision:
      role: "Activity.nodes[] 中的條件分支節點"
      fields:
        id: stable_id
        display_id: string
        type: decision
        condition: string
        paths: decision_path[]
        next: null
      invariants:
        - "Decision outgoing edges 由 paths 管理，next 固定 null"
        - "condition 是 Decision 的 field，不是獨立 model element"
        - "decision_path 是 nested object，不是獨立 model element"
        - "Decision 只在其 paths 各自導向不同的下一個 feature（不同 first_node）時才存在；所有 paths 指向同一目的地（包含 reroute self-loop）的 Decision 是 feature 內部邏輯，不建立為 Activity Decision 節點"
        - "**Decision vs operation split**：只有『同一 operation 的內部分支』才可視為 feature 內部邏輯；若不同 paths 本身已對應可獨立命名 / 驗收 / 觸發的 operation（例如分支選出不同招式、不同回合行動、不同外顯命令），則不得共用同一 feature，必須拆成不同 `first_node` / `binds_feature`"
        - "condition 欄位 = 描述「被判斷的業務條件域」（例如：會員資格 + 風評分數 + 訂單金額區間、店長簽核決定）；不得包含 CiC error codes（EC-N）、系統行為描述、或實作 if/else wording"
      nested_fields:
        decision_path:
          guard: string
          first_node: node_ref
          actor: actor_ref | null
          binding: string | null
          loop_back_target: node_ref | null
          stable_id: stable_id | null
        guard_constraints:
          - "guard = 簡潔的路由條件標籤（例如：條件不符、合法、駁回、核准）"
          - "guard 不得包含 CiC error codes（EC-N）、系統行為描述（cap、ignore）、或實作細節"
          - "所有失敗路徑指向同一個 terminal 時，合併為一條 guard（例如：條件不符）；失敗細節屬於 feature Rules"
          - "non-terminal guard 必須有對應 first_node 指向下一個 feature Action"
          - "**BRANCH compact pattern**：當 `decision_path` 對應**單一 terminal feature**（即該 path 走完後直達 MERGE / FINAL，且只有 1 個 feature binding、無後續 STEP sequence）時，採 `[BRANCH:id:guard] @actor {feature}` compact 樣式（path 直接綁 feature，**不另開 STEP**）；只有當 branch 後仍有多 STEP sequence 或 nested decision 時，才允許在 BRANCH 後展開 STEP-then-feature 樣式"
          - "不得產生 comment-only terminal branch；若 guard 對應終止，必須有 terminal feature binding 或明確 terminal first_node"

    Fork:
      role: "Activity.nodes[] 中的並行分流節點"
      fields:
        id: stable_id
        display_id: string
        type: fork
        paths: fork_path[]
        next: null
      invariants:
        - "Fork outgoing edges 由 paths 管理，next 固定 null"
        - "fork_path 是 nested object，不是獨立 model element"
      nested_fields:
        fork_path:
          first_node: node_ref
          actor: actor_ref | null
          binding: string | null
          stable_id: stable_id | null

    Merge:
      role: "Activity.nodes[] 中的 Decision 合流節點"
      fields:
        id: stable_id
        display_id: string
        type: merge
        next: node_ref | null
      invariants:
        - "display_id 等於對應 Decision 的 display_id"
        - "不承載業務 action"

    Join:
      role: "Activity.nodes[] 中的 Fork 合流節點"
      fields:
        id: stable_id
        display_id: string
        type: join
        next: node_ref | null
      invariants:
        - "display_id 等於對應 Fork 的 display_id"
        - "不承載業務 action"

```

## 3. Reasoning SOP

1. 先把三條輸入主軸讀成同一份推理上下文：source material、impact scope、檔名軸。
   `$source_axes` = READ `source_material_bundle`
   `$filename_axes` = READ `filename_axes`
   `$impact_scope` = READ `impact_scope`

2. 把 raw idea 與 impact objects 拆成後面建 Activity 真的會用到的來源單位。
   `$source_units` = PARSE `$source_axes.raw_idea` and `$impact_scope.impacts` into 有序來源單位：
   - `actor_mentions`：明確 UI-facing 使用者、角色、部門
   - `action_mentions`：從 UI 觸發、且使用者可感知結果的完整業務行動
   - `condition_mentions`：條件、判斷、成功／失敗／回退語句
   - `parallel_mentions`：並行責任或同步進行線索
   - `loop_mentions`：retry / repeat / re-submit / until 等迴圈語句
   - `binding_mentions`：feature path、actor persona path、rule-bearing target、UI note、引用 artifact
   - `sequence_mentions`：before / after / then / finally / return-to / continue-with
   - `impact_mentions`：`impact_scope` 已指出的 flow / actor / state / operation / new behavior
   - `operation_trigger_mentions`：可獨立命名、獨立驗收的操作 surface

3. 從這些來源單位收斂 UAT flows，先把「一張 Activity 到底代表哪段旅程」定義清楚。
   `$uat_flows` = DERIVE 根據 `$source_units` 收斂出的 UAT flow 清單
   - UAT flow 必須是 actor-entry → actor-verification 的完整可 demo 路徑
   - 多 actor 但同一 package、且後段依賴前段狀態時，仍屬同一 UAT flow
   - rejection → rework → re-submit → re-evaluate 視為同一個 flow，不拆分
   - 只停在 handoff / prepare / enter-phase 的半段流程，不算完整 flow
   - 只是把多個 feature 名稱排成清單、卻沒有狀態轉移 / decision / terminal verification 的，不得產生 Activity
   - routing depth / approval layer / tier table 等**結構性差異**要拆成 sibling Activity，不得在同一張 Activity 裡把多個 variation 畫成平行選單

4. 為每個 UAT flow 建立 Activity identity，並依 variation decomposition 規則補上 `variation_role`。
   `$activity_identities` = DERIVE 每個 `$uat_flow` 的 `name`、`file_path`、`version`、`id`
   ASSERT 每個 `$uat_flow.variation_role ∈ {happy_path, extreme_min, extreme_max, additional}`

5. 逐個 UAT flow 建立 Activity skeleton。
   LOOP per `$uat_flow` in `$uat_flows`
   5.1 `$actor_candidates` = DERIVE 根據 actor mentions、action subject、path subject、binding owner、actor impact objects 整理出的 Actor 候選紀錄
   5.2 `$actors` = CLASSIFY `$actor_candidates` into `Actor` elements
      - human role / organization role 才能升格為 Actor
      - product system / third-party system 只能吸收進 Action 的 postcondition / boundary note，不可成為 Actor
      - duplicate actor names 要依 domain identity 合併，不可只看拼字
   5.3 `$activity` = DERIVE Activity skeleton，至少含 `initial`、一個以上 `final`、`$actors`、空的 `nodes`
   5.4 `$frontier` = DERIVE 根據 action / condition / parallel / loop / sequence / impact mentions 排出的遞迴建模佇列
   5.5 `$context_stack` = DERIVE 根節點 flow context，含 `previous_node = initial`、`open_decision = null`、`open_fork = null`、`exit_target = final`

6. 用 frontier 遞迴展開節點，把來源單位逐步分類成 Action / Decision / Fork / Merge / Join / loop_back / field_only / graph_gap。
   LOOP while `$frontier` 非空
   6.1 `$unit` = DERIVE 從 `$frontier` 取出的下一個 source unit
   6.2 `$unit_kind` = CLASSIFY `$unit` into action | decision | branch_path | fork | parallel_path | merge | join | loop_back | field_only | graph_gap
   6.3 IF `$unit_kind` == action:
      - 補出 actor ref、action_type、action_name、binds_feature
      - graph link 接到目前 `previous_node`
      - 更新 `previous_node`
   6.4 IF `$unit_kind` == decision:
      - 補出業務條件，不接受純 implementation if/else wording
      - 建立 `Decision`
      - 派生 child branch units，並 push decision context
   6.5 IF `$unit_kind` == branch_path:
      - 補出 guard、path actor、path binding、first child unit
      - 寫回 `decision.paths[]`
      - 缺 child 與 binding 時，列為 terminal / comment-only gap
   6.6 IF `$unit_kind` == merge:
      - 建立 `Merge`
      - 把目前 decision paths 的終點收回 merge
   6.7 IF `$unit_kind` == fork` or `parallel_path` or `join`:
      - 依並行線索建立 `Fork` / `fork_path` / `Join`
   6.8 IF `$unit_kind` == loop_back:
      - 補 loop target；若放置位置不合法，列為 gap
   6.9 IF `$unit_kind` == field_only:
      - 只更新既有 element field，不得升格成獨立 element
   6.10 IF `$unit_kind` == graph_gap:
      - 明確記錄缺來源、邊界模糊、結構不支援、順序矛盾等 gap
   END LOOP

7. 把所有 terminal 收斂乾淨，完成 Activity 的 graph 形狀。
   `$activity_with_edges` = DERIVE 根據 `$activity` 補齊 `Initial.next`、node `next`、`decision_path.first_node`、`fork_path.first_node`、final reachability
   `$terminal_nodes` = DERIVE 遞迴展開後沒有後繼節點的 nodes
   LOOP per `$terminal` in `$terminal_nodes`
   7.1 IF `$terminal` is not `Decision` or `Fork`: DERIVE `$terminal.next = first Final.id`
   7.2 IF `$terminal` is `Decision` or `Fork`: ASSERT outgoing paths 最終抵達 Merge / Join，否則記錄 `$graph_gaps`
   END LOOP
   `$activity_resolved` = DERIVE 根據 `$activity_with_edges` 正規化後的 Activity

8. 做收尾驗證，確認這張 Activity 至少在 graph driver 的基本結構上是合法的。
   ASSERT Activity exactly one `Initial`
   ASSERT Activity one or more `Final`
   ASSERT every `Action.actor` resolves to `Actor.id`
   ASSERT 每個 node id 穩定且唯一
   ASSERT every `display_id` 在其 element family 內唯一
   ASSERT every `Decision.paths[]` has `guard` and `first_node`
   ASSERT every `Fork.paths[]` has `first_node`
   ASSERT `Decision.paths[]` and `Fork.paths[]` 維持 nested fields，不得成為獨立 elements
   END LOOP

9. 對整批 Activity 做 ambiguity detection，取代舊的 batch confirm。
   `$ambiguity_findings` = DERIVE 根據 `$activities` 整理出的 ambiguity findings
   - actor 沒有 raw traceback
   - branch label 沒有 raw 對應
   - loop_back 沒有明確迴圈線索
   - step 動作或 postcondition 沒有 raw / impact traceback
   - granularity 過粗，應拆 sibling step
   - Decision selector attribute 沒有上游記錄動作支撐
   - 出現 phase-slice smell、feature-list smell、或 terminal 不可達
   - variation trigger 被偵測到，但缺 `extreme_min` / `extreme_max`
   - 某 flow scope 看起來仍屬 speculative scope

10. 把 ambiguity findings 組成 `clarify_payload`；沒有 finding 就保持空陣列。
    > **Phase 2/3 約束**：本步驟只生成原始 findings 清單（不轉換成用戶面向的 cic 題目）；「如何把發現轉成提問、選項如何設定、預設值選哪個」**完全交由 Phase 5 `/clarify-loop` 負責**。此約束保證 Phase 2/3 遵循「自動化檢驗，決策交還用戶」原則。
   
   `$clarify_payload` = DERIVE 根據 `$ambiguity_findings` 整理出的 clarify-loop 題組（原始 findings 清單）
   LOOP per `$finding` in `$ambiguity_findings`
   10.1 `$question` = COLLECT `$finding` as-is（不篩選、不轉換），並組成 question 結構用於 `/clarify-loop` 消費
   10.2 APPEND `$question` to `$clarify_payload.questions`
   END LOOP
   IF `$ambiguity_findings` empty: SET `$clarify_payload.questions = []`（無歧義 — 主流程繼續）

11. 整理最終輸出；caller 若收到非空 `clarify_payload`，就交給 SKILL.md Phase 2 Seam A 觸發 `/clarify-loop`。
    > `/clarify-loop` 負責：(a) 將 findings 轉成用戶可理解的問題、(b) 設定選項和預設值、(c) 管理重試預算。User 回答後 caller 以 `GOTO #2.17` 重跑本 RP；本 RP 不做 inline 確認或自動決策。
   
   `$activities_final` = DERIVE 由 `$activities` 組成的 Activity models（保留 `modeled` flag）
   ASSERT 每個 `$activities_final[*].activity` 只包含 Modeling Element Definition 列出的 elements

## 4. Material Reducer SOP

1. 把每個 UAT flow 的 Activity 與 graph gaps 收成 `activity_analysis` items，保留 `variation_role` 與 `modeled` 狀態。
   `$activity_analyses` = DERIVE 由 `$activities_final` 與 `$graph_gaps` 組成的 `activity_analysis` items 清單

2. 最後確認 reducer 沒有漏掉必要結構，也沒有把 unresolved graph gap 偷偷放行。
   ASSERT 每個 `$activity_analyses.items[*].activity` 只包含 Modeling Element Definition 列出的 elements
   ASSERT 每個 `$activity_analyses.items[*].activity.actors[]` and `.nodes[]` complete（除非 `modeled=false`）
   ASSERT 每個 `$activity_analyses.items[*].variation_role ∈ {happy_path, extreme_min, extreme_max, additional}`
   ASSERT modeled=true 的 item 不得含 unresolved self-contained / terminal graph_gaps；若命中則 `exit_status = blocked`

3. 把最終輸出包成 terminal `activity_analyses`，並把 `clarify_payload` 一起並列輸出，讓 caller 能一致判斷要不要進 Seam A。
   `$reducer_output` = DERIVE 最終 `activity_analyses` 輸出，內含 `clarify_payload`

Return:

```yaml
status: complete | needs_revision | blocked
produces:
  activity_analyses:
    clarify_payload:
      questions: []               # 步驟 24 產出；可空（無歧義即放行）
    items:
      # 每個 uat_flow 對應一筆；含當前是否本輪建模的 modeled flag
      - uat_flow_id: string
        modeled: true | false
        variation_role: happy_path | extreme_min | extreme_max | additional
        activity:
          name: string
          id: stable_id
          initial: Initial
          finals: Final[]
          actors: Actor[]
          nodes: [Action, Decision, Fork, Merge, Join]
        graph_gaps: []
        exit_status: complete | blocked
  uat_flows:
    # 偵測到的全部 UAT flow 清單；與 activity_analyses.items 1:1 對齊
    - name: string
      file_path: string
      entry_actor: string
      verification_actor: string
      modeled: true | false
      variation_role: happy_path | extreme_min | extreme_max | additional
traceability:
  inputs:
    - source_material_bundle
    - impact_scope
    - filename_axes
  derived:
    - Activity
    - Actor
    - Initial
    - Final
    - Action
    - Decision
    - Fork
    - Merge
    - Join
clarifications:
  - clarify_payload  # 步驟 24 產出；非空時由 SKILL.md Phase 2 Seam A 觸發 /clarify-loop
```
