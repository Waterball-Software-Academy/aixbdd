---
rp_type: reasoning_phase
id: discovery.07-clarification-dimensions
context: discovery
slot: "07"
name: Clarification Dimensions
variant: post_formulation
note: scope 收斂為跨 artifact 殘留 sweep；Seam 0/A/B（02 / 04 / 06）已分擔早期歧義
consumes:
  - name: discovery_sourcing
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: activity_analysis
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: atomic_rule_draft
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: formulation_reasoning_package
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: quality_verdict
    kind: gate_result
    source: caller
    required: true
produces:
  - name: clarify_payload
    kind: derived_axis
    terminal: false
---

# Clarification Dimensions

本 RP 在 Discovery 初版 Activity / rule-only Feature 通過 quality gate 後執行。目的不是阻擋初版產物，而是把已成形 artifact 暴露出的產品決策缺口整理成 `/clarify-loop` 批次問題，讓下一輪修正有明確來源。

## 1. Required Axis

```yaml
required_axis:
  - name: discovery_sourcing
    source: discovery.01-source-material
    required_fields:
      - source_material_bundle
      - impact_scope
  - name: activity_analysis
    source: discovery.03-activity-analyze
    required_fields:
      - activity
  - name: atomic_rule_draft
    source: discovery.05-atomic-rules
    required_fields:
      - features
      - rules_by_operation
  - name: formulation_reasoning_package
    source: caller
    required_fields:
      - features
  - name: quality_verdict
    source: discovery Phase 4
    completeness_check:
      rule: only run after quality_verdict.ok == true
      on_missing: STOP
```

## 2. Dimension Catalog

Generate questions across these dimensions when the current artifacts leave a meaningful product decision open:

| dimension_id | Question focus | Typical kind |
|---|---|---|
| `journey_state_model` | journey / stage state machine, allowed transitions, terminal stages | BDY |
| `stage_sop_binding` | whether a stage has zero / one / many SOPs, SOP ordering, inheritance | BDY |
| `actor_permission` | which UI-facing roles can view, edit, or advance a journey | BDY |
| `temporal_versioning` | effective dates, version pinning, historical SOP visibility | CON |
| `exception_paths` | missing journey, missing SOP, invalid transition, deleted stage | GAP |
| `concurrency` | simultaneous edits, stale stage updates, conflict resolution | CON |
| `audit_history` | stage history, SOP execution history, who changed what | BDY |
| `cross_entity_rules` | list / journey / stage / SOP consistency boundaries | BDY |

## 3. Reasoning SOP

1. 先把可能值得回問的缺口都收進來，來源包含 sourcing gaps、activity graph gaps、atomic rule 草稿、以及已落出的 feature Rules。
   `$candidate_questions` = DERIVE 根據 `discovery_sourcing.gaps`、`activity_analysis.graph_gaps`、`$atomic_rule_draft`、已落出的 feature Rules 整理出的候選問題

2. 每個 candidate 都要被歸到唯一一個 `dimension_id`，避免同一個問題在多個維度重複出現。
   CLASSIFY every candidate into exactly one `dimension_id` from §2

3. 已經被乾淨 Rule 或明確 Activity edge 解掉的問題，要在這裡先丟掉，不要再回問一次。
   DROP candidates already resolved by a clean Rule or explicit Activity edge

4. 依下游影響面積排序，先問最會影響產品決策的問題。
   PRIORITIZE candidates by downstream blast radius:
   4.1 state machine / transition 問題優先
   4.2 SOP binding / versioning 次之
   4.3 permission / exception / concurrency / audit / cross-entity 之後

5. 題目數量要收斂在 round budget 內；若未指定 budget，預設上限 10 題。
   LIMIT output to `${MAX_QUESTIONS_PER_ROUND}` if present, otherwise 10

6. 組題前先過一次 `/clarify-loop` payload schema 檢查，確保每題都具備必要欄位。
   ASSERT every output question conforms to `/clarify-loop` `references/payload-schema.md`:
   - `id`
   - `location`
   - `kind ∈ {GAP, ASM, BDY, CON}`
   - `context`
   - `question`
   - `options` count between 2 and 4
   - `recommendation`
   - `recommendation_rationale`
   - `priority_score`

7. 把 trace-only metadata 跟 user-visible wording 嚴格分開。
   ASSERT `id`, `location`, `kind`, `dimension_id`, and `priority_score` are trace-only metadata; they MUST NOT be concatenated into `context`, `question`, `options[].label`, `options[].impact`, or `recommendation_rationale`

8. 再做一輪 user-facing wording gate，確認題目真的像在問產品決策，而不是在暴露 artifact 結構。
   ASSERT every user-visible field is natural language:
   - `context` 像一段短提醒，讓使用者立刻知道現在在談哪個產品情境
   - `question` 像一句非技術 stakeholder 也能回答的問題
   - `options[].label` 用日常產品語言，不用 artifact 名或內部 enum
   - `options[].impact` 講的是產品 / 使用者後果，不是檔案或實作後果
   - `recommendation_rationale` 要說出為什麼這個選項對產品流程最簡單或最安全

9. 任何會暴露內部結構的字樣，都不得出現在 user-visible 欄位。
   ASSERT user-visible fields contain none of these internal tokens or patterns:
   - `GAP`, `ASM`, `BDY`, `CON`
   - `dimension_id`, `journey_state_model`, `stage_sop_binding`, `actor_permission`, `temporal_versioning`, `exception_paths`, `concurrency`, `audit_history`, `cross_entity_rules`
   - `location`, `位置`, `file:line`, `.feature`, `.activity`, `Rule`, `STEP`, `AtomicRule`, `payload`, `artifact`, `feature file`
   - slash-heavy paths such as `specs/...`, `features/...`, `activities/...`

10. 雖然 user-visible wording 要乾淨，但 trace-only `location` 仍必須保留最近的 artifact 錨點，方便下一輪修正。
    ASSERT every question still cites an artifact location in the trace-only `location` field, using the nearest Activity line, Feature Rule, sourcing report gap, or plan spec summary pointer

11. 這一輪只問產品決策缺口，不問實作設計、資料庫 schema、API shape、BDD Examples、或 test data。
    ASSERT no question asks for implementation design, database schema, API shape, BDD Examples, or test data; those belong to later phases

12. 把最終題目依優先度排序後收成 `clarify_payload`。
    `$clarify_payload` = DERIVE `{questions: [...]}` sorted by priority

## 4. User-Facing Wording Gate

### Before — reject

```yaml
questions:
  - id: journey-state-terminal-stage
    location: specs/backend/packages/NN-feature/features/crm/03-更新名單當前階段.feature:Rule
    kind: BDY
    context: journey_state_model / BDY；位置：03-更新名單當前階段.feature
    question: 名單 journey 的 state transition 要先採哪種規則？
    options:
      - id: NO_REVERT
        label: 單向推進
        impact: 狀態機較單純；Rule 留在 03-更新名單當前階段.feature
      - id: CUSTOM_STATE_MACHINE
        label: 每個 journey 自訂狀態機
        impact: 需新增 transition policy 與 state machine rule
    recommendation: NO_REVERT
    recommendation_rationale: 降低初版狀態機分歧
    priority_score: 20
```

Reject reasons:

- `context` exposes `journey_state_model`, `BDY`, file location, and `.feature`.
- `question` uses mixed English domain jargon (`journey`, `state transition`).
- `impact` talks about Rule placement instead of the user's product consequence.
- `recommendation_rationale` is abstract and not conversational.

### After — accept

```yaml
questions:
  - id: journey-state-terminal-stage
    location: specs/backend/packages/NN-feature/features/crm/03-更新名單當前階段.feature:Rule
    kind: BDY
    context: 客服會把學員名單從一個階段移到另一個階段
    question: 名單走到某個階段後，客服可以怎麼調整它的位置？
    options:
      - id: NO_REVERT
        label: 只能往下一關走，不能跳關也不能退回去
        impact: 初版流程最單純，客服照順序推進名單，不會出現跳關或倒退造成的混亂
      - id: SKIP_FORWARD
        label: 可以跳到後面的關卡，但不能退回前面
        impact: 客服能處理進度較快的名單，但要說清楚哪些關卡可以被略過
      - id: MOVE_ANY_ALLOWED
        label: 可以往後走，也可以退回前面的關卡
        impact: 操作最彈性，但需要清楚記錄誰把名單移去哪裡
    recommendation: NO_REVERT
    recommendation_rationale: 建議先選最單純的做法，客服只要照順序推進名單，初版比較不會混亂
    priority_score: 20
```

Accept reasons:

- `location`, `kind`, and internal id stay machine-readable but are not repeated in user-visible fields.
- `context`, `question`, labels, impacts, and recommendation read like natural product language.
- Each option explains what the user experience changes, not what artifact changes.

## 5. Output Example Shape

```yaml
questions:
  - id: journey-state-terminal-stage
    location: specs/backend/packages/NN-feature/features/crm/03-更新名單當前階段.feature:Rule
    kind: BDY
    context: 客服會把學員名單從一個階段移到另一個階段
    question: 名單走到某個階段後，客服可以怎麼調整它的位置？
    options:
      - id: NO_REVERT
        label: 只能往下一關走，不能跳關也不能退回去
        impact: 初版流程最單純，客服照順序推進名單，不會出現跳關或倒退造成的混亂
      - id: ALLOW_REVERT
        label: 可以往後走，也可以退回前面的關卡
        impact: 操作最彈性，但需要清楚記錄誰把名單移去哪裡
    recommendation: NO_REVERT
    recommendation_rationale: 建議先選最單純的做法，客服只要照順序推進名單，初版比較不會混亂
    priority_score: 20
```

## 6. Reducer SOP

1. 把這一輪整理好的題目收成最終輸出；這個 RP 只產題組，不直接修改 artifact。
   `$reducer_output` = DERIVE 由 `$clarify_payload` 組成的最終輸出 package

2. 最後確認題目數沒有超出 round budget，也確認 clean artifact 沒有被這個 RP 直接改動。
   ASSERT question count is within round budget
   ASSERT no clean artifact content is modified by this RP; writes are owned by `/clarify-loop`

Return:

```yaml
status: complete | skipped | blocked
produces:
  clarify_payload:
    questions: []
traceability:
  inputs:
    - discovery_sourcing
    - activity_analysis
    - atomic_rule_draft
    - formulation_reasoning_package
    - quality_verdict
```
