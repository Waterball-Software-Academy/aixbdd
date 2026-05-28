---
rp_type: reasoning_phase
id: skill-rca.02-propose-correction
context: skill-rca
slot: "02"
name: Propose Correction
variant: none
consumes:
  - name: RootCauseTrace
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: DefectClassification
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: ArtifactGraphAxis
    kind: required_axis
    source: skill_global
    required: true
  - name: LifecycleSignalAxis
    kind: required_axis
    source: skill_global
    required: true
  - name: PublicContract
    kind: required_axis
    source: skill_global
    required: true
  - name: BackwardVerificationRule
    kind: required_axis
    source: reference
    required: true
produces:
  - name: CorrectionProposal
    kind: material_bundle
    terminal: false
downstream:
  - skill-rca.03-reformulate-decision
---

# Propose Correction

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: PublicContract
    source:
      kind: skill_global
      path: $$public_contract
    granularity: externally visible and downstream-facing behavior to preserve
    required_fields:
      - name
      - triggers
      - user_invocable
      - downstream_contract
    optional_fields:
      - compatibility_notes
    completeness_check:
      rule: every externally visible behavior is named or explicitly absent
      on_missing: STOP
    examples:
      positive:
        - Skill name, trigger phrases, invocation flag, and delegate payload shape.
      negative:
        - Only the current implementation files with no behavior summary.
  - name: BackwardVerificationRule
    source:
      kind: reference
      path: references/defect-types.md
    granularity: one mental replay question and pass/fail interpretation
    required_fields:
      - replay_question
      - fail_meaning
      - pass_meaning
    optional_fields:
      - examples
    completeness_check:
      rule: the rule can decide whether the original defect would still occur after the proposed change
      on_missing: STOP
    examples:
      positive:
        - If the skill already had this patch, the observed defect would not be produced.
      negative:
        - A generic statement that changes should be safe.
  - name: ArtifactGraphAxis
    source:
      kind: skill_global
      path: $$artifact_graph
    granularity: graph evidence needed to choose the smallest lifecycle correction
    required_fields:
      - ArtifactNode
      - ArtifactEdge
    optional_fields:
      - manifest_expectations
      - unknown_edges
    completeness_check:
      rule: every lifecycle-targeting proposal can name affected nodes and edges
      on_missing: STOP
    examples:
      positive:
        - A duplicate SSOT proposal can point to both competing artifact nodes and their consumers.
      negative:
        - A cleanup proposal without the files it will affect.
  - name: LifecycleSignalAxis
    source:
      kind: skill_global
      path: $$lifecycle_signals
    granularity: one lifecycle drift signal with suggested fix kind
    required_fields:
      - signal
      - path
      - evidence
      - suggested_fix_kind
    optional_fields:
      - related_paths
      - confidence
    completeness_check:
      rule: fix kind can map to delete, deprecate, add-consumer, choose-ssot-and-link, split-lazy-load, move-to-owner-bucket, or remove-reference-or-restore-active-owner
      on_missing: STOP
    examples:
      positive:
        - monolith_template_candidate maps to split-lazy-load.
      negative:
        - A proposed refactor with no lifecycle signal.
```

### 1.2 Search SOP

1. $trace = DERIVE RootCauseTrace from upstream RP
2. $classification = DERIVE DefectClassification from upstream RP
3. $artifact_graph = DERIVE ArtifactGraphAxis from $$artifact_graph
4. $lifecycle_material = DERIVE LifecycleSignalAxis from $$lifecycle_signals
5. $contract = DERIVE PublicContract from $$public_contract
6. $verification_rule = READ `references/defect-types.md`
7. ASSERT $artifact_graph, $lifecycle_material, $contract, and $verification_rule satisfy Required Axis completeness

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: CorrectionProposal
  element_rules:
    element_vs_field:
      element: A patchable correction unit or verification result that can be independently reviewed.
      field: A path, diff note, rationale, or risk nested under that correction unit.
  elements:
    ArtifactChange:
      role: One proposed modification to a skill artifact.
      fields:
        target_path: string
        change_summary: string
        before_after_summary: string
        root_cause_link: string
      invariants:
        - ArtifactChange targets only skill artifacts, never generated product output.
    LifecycleFixPattern:
      role: The smallest correction pattern for a lifecycle drift signal.
      fields:
        signal: orphan_asset | duplicate_ssot_candidate | monolith_template_candidate | misbucketed_runtime_flow | deprecated_still_referenced
        fix_kind: delete | deprecate | add-consumer | choose-ssot-and-link | split-lazy-load | move-to-owner-bucket | remove-reference-or-restore-active-owner
        affected_paths: list[string]
        rationale: string
      invariants:
        - LifecycleFixPattern is present when the proposal addresses a lifecycle defect type.
        - fix_kind must match the suggested_fix_kind unless the proposal explains a safer smaller correction.
    VerificationResult:
      role: The compatibility and backward replay result for the proposed change set.
      fields:
        preserves_public_contract: boolean
        prevents_original_defect: boolean
        clears_lifecycle_signal: boolean
        risk_notes: list[string]
      invariants:
        - VerificationResult applies the BackwardVerificationRule.
    CorrectionProposal:
      role: The complete proposal that can be reviewed or applied in auto mode.
      fields:
        artifact_changes: list[ArtifactChange]
        verification_result: VerificationResult
        explanation: string
      invariants:
        - CorrectionProposal names every target file.
        - CorrectionProposal explains how the root cause is eliminated.
```

## 3. Reasoning SOP

1. $artifact_changes = DRAFT ArtifactChange set from RootCauseTrace and DefectClassification
2. $lifecycle_fix_patterns = CLASSIFY LifecycleSignalAxis against DefectClassification into LifecycleFixPattern elements
3. $artifact_changes2 = DERIVE minimal ArtifactChange set from $artifact_changes and $lifecycle_fix_patterns:
   - orphan_asset → delete, deprecate, or add-consumer
   - duplicate_ssot_candidate → choose one SSOT and convert the others to thin entry, link, or deprecated note
   - monolith_template_candidate → split into lazy-load child files and keep a thin entry
   - misbucketed_runtime_flow → move runtime flow to SKILL.md or reasoning, leaving references declarative
   - deprecated_still_referenced → remove active reference or restore active ownership
4. $contract_ok = JUDGE ArtifactChange set preserves PublicContract
5. $prevents_defect = JUDGE ArtifactChange set against BackwardVerificationRule
6. $clears_lifecycle = JUDGE ArtifactChange set removes the causal LifecycleSignal without introducing a new duplicate or orphan
7. $verification = DERIVE VerificationResult from $contract_ok, $prevents_defect, and $clears_lifecycle
8. $proposal = DRAFT CorrectionProposal from ArtifactChange set, LifecycleFixPattern set, and VerificationResult
9. ASSERT ArtifactChange, LifecycleFixPattern, VerificationResult, and CorrectionProposal are traceable to Required Axis inputs

## 4. Material Reducer SOP

1. $correction_proposal = DERIVE CorrectionProposal bundle from ArtifactChange, VerificationResult, and CorrectionProposal
2. ASSERT $correction_proposal satisfies this reducer output schema:

```yaml
status: complete | needs_revision | blocked
produces:
  CorrectionProposal:
    ArtifactChange:
      - target_path: string
        change_summary: string
        before_after_summary: string
        root_cause_link: string
    LifecycleFixPattern:
      - signal: orphan_asset | duplicate_ssot_candidate | monolith_template_candidate | misbucketed_runtime_flow | deprecated_still_referenced
        fix_kind: delete | deprecate | add-consumer | choose-ssot-and-link | split-lazy-load | move-to-owner-bucket | remove-reference-or-restore-active-owner
        affected_paths: list[string]
        rationale: string
    VerificationResult:
      preserves_public_contract: boolean
      prevents_original_defect: boolean
      clears_lifecycle_signal: boolean
      risk_notes: list[string]
    CorrectionProposal:
      artifact_changes: list[ArtifactChange]
      verification_result: VerificationResult
      explanation: string
traceability:
  inputs:
    - RootCauseTrace
    - DefectClassification
    - ArtifactGraphAxis
    - LifecycleSignalAxis
    - PublicContract
    - BackwardVerificationRule
  derived:
    - ArtifactChange
    - LifecycleFixPattern
    - VerificationResult
    - CorrectionProposal
clarifications: []
```
