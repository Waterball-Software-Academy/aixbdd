---
rp_type: reasoning_phase
id: discovery.02-sourcing-clarify
context: discovery
slot: "02"
name: Sourcing Clarify (Seam 0)
variant: post_sourcing
consumes:
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
    note: 偵測到 Class 1 lexical 腦補（raw 中「可能/大概/像/例如/左右/這只是例子」修飾的數字或概念）時輸出題目；無 marker 則 questions 為空
downstream:
  - discovery.03-activity-analyze
---

# Sourcing Clarify — Seam 0（lexical sweep + demo-anchor）

本 RP 在 RP01 sourcing 完成後、`reports/discovery-sourcing.md` 落筆前執行，目的是攔截 **Class 1 — raw 主動標示為示意但 AI 卻寫死成 SSOT** 的腦補。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: discovery.01-source-material
    granularity: raw idea + impact scope；含 raw_material_pointers 與 normalized_excerpts
    required_fields:
      - raw_material_pointers
      - normalized_excerpts
    optional_fields: []
    completeness_check:
      rule: source_material_bundle 已由 RP01 落定
      on_missing: STOP
```

> 註：`hallucination_detection_checklist` 不在 Required Axis（屬靜態 reference doc，非 data axis）；caller 已於 frontmatter `consumes` 標註 `kind: reference`。本 RP 僅引用 §Pattern1（lexical-marker）+ §Pattern3（demo-anchor）。

### 1.2 Search SOP

1. 先把上游交下來的 source material bundle 與腦補檢查表讀進來，確認這一輪有足夠材料可掃。
   `$bundle` = READ source_material_bundle
   `$checklist` = READ hallucination_detection_checklist

2. 這一輪至少要拿得到 raw material pointers；如果連這個都沒有，就不應該進 lexical sweep。
   ASSERT `$bundle.raw_material_pointers` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: clarify_payload
  element_rules:
    element_vs_field:
      element: "PM 需要被回問的歧義問題單位（題目）"
      field: "題目的屬性（id / concern / options / default）"
  elements:
    ClarifyQuestion:
      role: "sourcing 階段一個待回問的歧義題目"
      fields:
        id: stable_id
        concern: string
        options: option[]
        default: option_id
      invariants:
        - "id 形如 src-Q<n>"
        - "options 至少 2 項，預設含 OTHER"
        - "concern 用自然語言描述命中的 marker 與對應數字／概念"
      nested_fields:
        option:
          id: A | B | OTHER
          label: string
          impact: string
```

## 3. Reasoning SOP

1. 先從 raw material pointers 裡找出所有 lexical-marker 命中，包含「可能 / 大概 / 像 / 例如 / 左右 / 這只是例子」這類明示示意性的說法。
   `$markers` = MATCH `$bundle.raw_material_pointers` against `$checklist.Pattern1` 關鍵字（可能 / 大概 / 像 / 例如 / 左右 / 這只是例子 / 實際.*要看 / maybe / probably / about / e.g.）

2. 再從這些 marker 往後抓數字、範圍、切點這類 demo-anchor 候選，避免把示意內容誤升格成 SSOT。
   `$demo_anchors` = DERIVE 根據 `$checklist.Pattern3` 從 `$markers` 延伸出的示意數字／範圍／切點候選

3. 把命中的 marker 與 demo-anchor 整理成 findings，讓每筆 finding 都能回溯到具體 raw 片段與 sourcing 上下文。
   `$findings` = DERIVE 根據 `$markers` 與 `$demo_anchors` 整理出的歧義 findings 清單，每筆含「marker 詞 + 後接 token + sourcing 上下文」

4. 逐筆 findings 組成 clarify 題目；沒有 findings 就讓 questions 保持空陣列。
   LOOP per `$finding` in `$findings` (budget=count(`$findings`)；exit when 每個 finding 都已組成題目)
   4.1 `$question` = CLASSIFY `$finding` into `ClarifyQuestion`，其中 `id=src-Q<n>`、`concern=<finding 描述>`、`options=[A:升格為明確事實, B:保留為示意, OTHER:重新描述]`、`default=B`
   4.2 APPEND `$question` to `$questions`
   END LOOP

5. 收尾檢查題目 id 是否穩定且唯一。
   ASSERT 所有 `$questions[*].id` unique

## 4. Material Reducer SOP

1. 把這一輪組好的題目收成 `clarify_payload`；沒有命中也要明確回傳空陣列，而不是省略欄位。
   `$reducer_output` = DERIVE 由 `$questions` 組成的 `clarify_payload`

2. 最後確認輸出形狀穩定，讓 caller 可以一致地檢查這一輪要不要進 `/clarify-loop`。
   ASSERT `$reducer_output.questions` 為 list（可空，代表無 marker 命中）
   ASSERT 每題滿足 `ClarifyQuestion` invariants

Return:

```yaml
status: complete | blocked
produces:
  clarify_payload:
    questions: []                # 0..N 筆 ClarifyQuestion；空時主流程繼續
traceability:
  inputs:
    - source_material_bundle
    - hallucination_detection_checklist
  derived:
    - ClarifyQuestion
clarifications:
  - clarify_payload  # caller (SKILL.md Phase 2 Seam 0) 觸發 /clarify-loop
```

## 5. Anti-Pattern

- ❌ 對 raw 中無 marker 的 hard claim 數字（如「7 項條件」「3 個 actor」）丟題目
- ❌ 對非 sourcing-stage 概念（HTTP method、版本號）丟題目（屬 Seam B atomic 範疇）
- ❌ 自行擴增 marker 清單；僅依 hallucination-detection-checklist §Pattern1 為準
- ❌ 重複命中（同 marker 在 raw 多處出現只列一題；以最早出現位置為 anchor）
