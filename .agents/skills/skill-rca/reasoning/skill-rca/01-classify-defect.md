---
rp_type: reasoning_phase
id: skill-rca.01-classify-defect
context: skill-rca
slot: "01"
name: Classify Defect
variant: none
consumes:
  - name: RootCauseTrace
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: DefectTaxonomy
    kind: required_axis
    source: reference
    required: true
  - name: ProgramLikeContract
    kind: required_axis
    source: reference
    required: true
  - name: ArtifactGraphAxis
    kind: required_axis
    source: skill_global
    required: true
  - name: LifecycleSignalAxis
    kind: required_axis
    source: skill_global
    required: true
produces:
  - name: DefectClassification
    kind: material_bundle
    terminal: false
downstream:
  - skill-rca.02-propose-correction
---

# Classify Defect

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: DefectTaxonomy
    source:
      kind: reference
      path: references/defect-types.md
    granularity: one Traditional Chinese defect type name and definition
    required_fields:
      - type_name
      - definition
      - typical_fix
    optional_fields:
      - composite_examples
    completeness_check:
      rule: 決策樹盲區, 模板誤導, 參考膚淺, 自驗缺失, 繼承遺漏, 規章落差, 孤兒資產, 雙重真值來源, 過胖模板未 lazy-load, 分桶錯誤, and 資產生命週期漂移 are all available as type names
      on_missing: STOP
    examples:
      positive:
        - 決策樹盲區 maps to an uncovered SOP branch and its typical fix.
      negative:
        - A prose-only list with no stable Traditional Chinese type names.
  - name: ProgramLikeContract
    source:
      kind: reference
      path: references/process-detail.md
    granularity: one program-like compliance signal
    required_fields:
      - signal
      - criterion
    optional_fields:
      - migration_status
    completeness_check:
      rule: contract includes missing sections, glossary, phase shape, SSA, reasoning drift, and reference flow drift signals
      on_missing: STOP
    examples:
      positive:
        - missing_ssa indicates productive steps lack SSA binding.
      negative:
        - A generic recommendation to improve structure.
  - name: ArtifactGraphAxis
    source:
      kind: skill_global
      path: $$artifact_graph
    granularity: one artifact graph with consumer and reference edges
    required_fields:
      - ArtifactNode
      - ArtifactEdge
    optional_fields:
      - manifest_expectations
      - unknown_edges
    completeness_check:
      rule: graph evidence can support lifecycle defect classification without guessing
      on_missing: STOP
    examples:
      positive:
        - An asset template node has no inbound consumer edge and no manifest retention reason.
      negative:
        - A prose statement that some files may be unused.
  - name: LifecycleSignalAxis
    source:
      kind: skill_global
      path: $$lifecycle_signals
    granularity: one lifecycle signal from references/process-detail.md
    required_fields:
      - signal
      - path
      - evidence
      - suggested_fix_kind
    optional_fields:
      - related_paths
      - confidence
    completeness_check:
      rule: signal names come from the artifact lifecycle detection contract or the list is explicitly empty
      on_missing: STOP
    examples:
      positive:
        - monolith_template_candidate signal for one template containing several RP-specific sections.
      negative:
        - A generic cleanup suggestion without signal name or artifact path.
```

### 1.2 Search SOP

1. $root_material = DERIVE RootCauseTrace from upstream RP
2. $taxonomy = READ `references/defect-types.md`
3. $program_contract = READ `references/process-detail.md`
4. $artifact_graph = DERIVE ArtifactGraphAxis from $$artifact_graph
5. $lifecycle_material = DERIVE LifecycleSignalAxis from $$lifecycle_signals
6. ASSERT $taxonomy, $program_contract, $artifact_graph, and $lifecycle_material satisfy Required Axis completeness

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: DefectClassification
  element_rules:
    element_vs_field:
      element: A defect type assignment or program-like gap that downstream proposal drafting can independently consume.
      field: Supporting evidence, confidence, or local notes nested under that assignment.
  elements:
    DefectType:
      role: One selected skill defect category from the stable taxonomy.
      fields:
        type_name: 決策樹盲區 | 模板誤導 | 參考膚淺 | 自驗缺失 | 繼承遺漏 | 規章落差 | 孤兒資產 | 雙重真值來源 | 過胖模板未 lazy-load | 分桶錯誤 | 資產生命週期漂移
        definition: string
        evidence: list[string]
        typical_fix: string
      invariants:
        - At least one DefectType is present.
        - Every DefectType type_name comes from DefectTaxonomy.
        - DefectType must not expose shorthand abbreviations.
    ProgramLikeGap:
      role: A structural compliance gap relevant to migration or reformulation.
      fields:
        signal: string
        evidence: list[string]
        migration_goal: convert-to-program-like | repair-existing-program-like | none
      invariants:
        - ProgramLikeGap is present when 規章落差 is selected.
```

## 3. Reasoning SOP

1. $defect_types = CLASSIFY RootCauseTrace against DefectTaxonomy into DefectType elements
2. $program_gaps = CLASSIFY RootCauseTrace against ProgramLikeContract into ProgramLikeGap elements
3. $lifecycle_types = CLASSIFY LifecycleSignalAxis and ArtifactGraphAxis against DefectTaxonomy into lifecycle DefectType elements
4. $pl_needed = JUDGE ProgramLikeGap or artifact_lifecycle_drift indicates structural compliance drift
5. $defect_types2 = DERIVE DefectType set with 規章落差 included when $pl_needed is true and 資產生命週期漂移 included when lifecycle signals are causal
6. ASSERT DefectType and ProgramLikeGap are traceable to RootCauseTrace, ArtifactGraphAxis, or LifecycleSignalAxis

## 4. Material Reducer SOP

1. $classification = DERIVE DefectClassification from DefectType set and ProgramLikeGap set
2. ASSERT $classification satisfies this reducer output schema:

```yaml
status: complete | blocked
produces:
  DefectClassification:
    DefectType:
      - type_name: 決策樹盲區 | 模板誤導 | 參考膚淺 | 自驗缺失 | 繼承遺漏 | 規章落差 | 孤兒資產 | 雙重真值來源 | 過胖模板未 lazy-load | 分桶錯誤 | 資產生命週期漂移
        definition: string
        evidence: list[string]
        typical_fix: string
    ProgramLikeGap:
      - signal: string
        evidence: list[string]
        migration_goal: convert-to-program-like | repair-existing-program-like | none
traceability:
  inputs:
    - RootCauseTrace
    - DefectTaxonomy
    - ProgramLikeContract
    - ArtifactGraphAxis
    - LifecycleSignalAxis
  derived:
    - DefectType
    - ProgramLikeGap
clarifications: []
```
