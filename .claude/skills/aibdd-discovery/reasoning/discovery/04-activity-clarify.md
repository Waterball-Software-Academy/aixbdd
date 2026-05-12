---
rp_type: reasoning_phase
id: discovery.04-activity-clarify
context: discovery
slot: "04"
name: Activity Clarify (Seam A)
variant: post_activity_analyze
consumes:
  - name: activity_analyses
    kind: required_axis
    source: upstream_rp
    required: true
    cardinality: list
  - name: source_material_bundle
    kind: required_axis
    source: upstream_rp
    required: true
  - name: hallucination_detection_checklist
    kind: reference
    source: reference
    required: true
produces:
  - name: clarify_payload
    kind: derived_axis
    terminal: false
    note: 偵測到 Class 2 流程結構腦補（DECISION 分支多出 raw 沒提的選項、actor 自生、流程環節無 traceback）時輸出題目；無歧義則 questions 為空
downstream:
  - discovery.05-atomic-rules
---

# Activity Clarify — Seam A（流程結構歧義）

本 RP 在 RP02 activity-analyze 完成後、RP03 atomic-rules 開始前執行。目的是攔截 **Class 2 — raw 完全留白但 AI 自生流程規則** 的腦補（流程結構層）。RP02 已先做 ambiguity detection；本 RP 把 detection 結果整理成 `clarify_payload`。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: activity_analyses
    source:
      kind: upstream_rp
      path: discovery.03-activity-analyze
    granularity: 每個 modeled=true uat_flow 的 Activity model 清單（actors / decisions / steps）
    required_fields:
      - items
      - items[].activity.actors
      - items[].activity.nodes
    optional_fields:
      - clarify_payload
    completeness_check:
      rule: RP02 已輸出 activity_analyses 與初步 ambiguity findings
      on_missing: STOP
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + normalized_excerpts，用於 traceback 比對
    required_fields:
      - raw_material_pointers
      - normalized_excerpts
    optional_fields: []
    completeness_check:
      rule: RP01 source_material_bundle 已落定
      on_missing: STOP
```

> 註：`hallucination_detection_checklist` 不在 Required Axis（屬靜態 reference doc）；本 RP 僅引用 §Pattern2（inference-without-source）。

### 1.2 Search SOP

1. 先把這一輪要檢查的 Activity 清單、source material、與腦補檢查表讀進來。
   `$activities` = READ `activity_analyses.items`
   `$bundle` = READ `source_material_bundle`
   `$checklist` = READ `hallucination_detection_checklist`

2. 這一輪至少要有 Activity 可掃；如果連 `items` 都沒有，就不該進 Activity Clarify。
   ASSERT `$activities` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: clarify_payload
  element_rules:
    element_vs_field:
      element: "Activity 結構層待回問的歧義題目"
      field: "題目的屬性（id / concern / options / default）"
  elements:
    ClarifyQuestion:
      role: "activity 階段一個待回問的歧義題目"
      fields:
        id: stable_id
        concern: string
        options: option[]
        default: option_id
      invariants:
        - "id 形如 act-Q<n>"
        - "concern 描述命中的元素類別（actor / branch / step / variation）與其在 activity 中的位置"
      nested_fields:
        option:
          id: A | B | OTHER
          label: string
          impact: string
```

## 3. Reasoning SOP

1. 先從空的 findings 開始，逐張 Activity 掃描「哪些結構是 raw 沒講、但模型自己長出來的」。
   `$findings` = DERIVE 空清單

2. 逐張 Activity 掃 actor、branch、step 的 traceback。
   LOOP per `$activity` in `$activities` (budget=count(`$activities`)；exit when 每個 activity 都已掃描)
   2.1 LOOP per `$actor` in `$activity.actors`
       2.1.1 `$actor_in_raw` = MATCH `$actor.name` against `$bundle.normalized_excerpts`（含 substring / synonym / paraphrase）
       2.1.2 IF `$actor_in_raw` == false: APPEND `{kind:actor, ref:$actor.id, activity:$activity.name}` to `$findings`
       END LOOP
   2.2 LOOP per `$decision` in `$activity.nodes` where type==decision
       2.2.1 LOOP per `$branch` in `$decision.paths`
             2.2.1.1 `$branch_in_raw` = MATCH `$branch.guard` against `$bundle.normalized_excerpts`
             2.2.1.2 IF `$branch_in_raw` == false: APPEND `{kind:branch, ref:$branch.stable_id, activity:$activity.name}` to `$findings`
             END LOOP
       END LOOP
   2.3 LOOP per `$step` in `$activity.nodes` where type==action
       2.3.1 `$action_in_raw` = MATCH `$step.name` against `$bundle.normalized_excerpts`
       2.3.2 IF `$action_in_raw` == false: APPEND `{kind:step, ref:$step.id, activity:$activity.name}` to `$findings`
       END LOOP
   END LOOP

3. 把 findings 組成 `ClarifyQuestion`；沒有 finding 就讓 questions 保持空陣列。
   LOOP per `$finding` in `$findings` (budget=count(`$findings`))
   3.1 `$question` = CLASSIFY `$finding` into `ClarifyQuestion`，其中 `id=act-Q<n>`、`concern=<finding 描述>`、`options=[A:刪除回 raw 範圍, B:保留並補充來源, OTHER:重新描述]`、`default=A`
   3.2 APPEND `$question` to `$questions`
   END LOOP

4. 收尾檢查每個題目 id 是否穩定且唯一。
   ASSERT 所有 `$questions[*].id` unique

## 4. Material Reducer SOP

1. 把這輪整理好的題目收成 `clarify_payload`；沒有題目也要回空陣列。
   `$reducer_output` = DERIVE 由 `$questions` 組成的 `clarify_payload`

2. 最後確認輸出形狀穩定，讓 caller 能直接判斷要不要進 Seam A 的 `/clarify-loop`。
   ASSERT `$reducer_output.questions` 為 list（可空）
   ASSERT 每題滿足 `ClarifyQuestion` invariants

Return:

```yaml
status: complete | blocked
produces:
  clarify_payload:
    questions: []                # 0..N 筆 ClarifyQuestion
traceability:
  inputs:
    - activity_analyses
    - source_material_bundle
    - hallucination_detection_checklist
  derived:
    - ClarifyQuestion
clarifications:
  - clarify_payload  # caller (SKILL.md Phase 2 Seam A) 觸發 /clarify-loop
```

## 5. Anti-Pattern

- ❌ 對 raw 中明確提及的流程環節丟題目（屬 Class 3 失讀，由 Phase 4 P5 sweep 處理）
- ❌ 對規則層歧義（HTTP method / hedging / 欄位細節）丟題目（屬 Seam B atomic 範疇）
- ❌ 重複 Seam 0 的 lexical-marker 偵測（已由 RP02 上游處理）
- ❌ 越界進 entity 欄位 schema 提問（屬 plan 階段）
