---
rp_type: reasoning_phase
id: skill-rca.03-reformulate-decision
context: skill-rca
slot: "03"
name: Reformulate Decision
variant: none
consumes:
  - name: DefectClassification
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: CorrectionProposal
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: ProgramLikeContract
    kind: required_axis
    source: reference
    required: true
produces:
  - name: ReformulateDecision
    kind: decision
    terminal: true
downstream: []
---

# Reformulate Decision

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: ProgramLikeContract
    source:
      kind: reference
      path: references/process-detail.md
    granularity: one structural migration signal and preferred migration goal
    required_fields:
      - signal
      - criterion
      - migration_goal
    optional_fields:
      - evidence
    completeness_check:
      rule: every structural gap can map to convert-to-program-like, repair-existing-program-like, or none
      on_missing: STOP
    examples:
      positive:
        - reference_flow_drift maps to repair-existing-program-like for an already program-like skill.
      negative:
        - A generic preference for nicer structure without a compliance signal.
```

### 1.2 Search SOP

1. $classification = DERIVE DefectClassification from upstream RP
2. $proposal = DERIVE CorrectionProposal from upstream RP
3. $contract = READ `references/process-detail.md`
4. ASSERT $contract satisfies Required Axis completeness

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ReformulateDecision
  element_rules:
    element_vs_field:
      element: A migration decision independently consumed by the reporting or delegation phase.
      field: Evidence, payload fields, or mode-specific notes nested under the decision.
  elements:
    MigrationNeed:
      role: Whether program-like reformulation is necessary after the RCA fix.
      fields:
        needed: boolean
        migration_goal: convert-to-program-like | repair-existing-program-like | none
        evidence: list[string]
      invariants:
        - MigrationNeed.needed is true when 規章落差 is selected or program-like gaps remain.
    ReformulatePayload:
      role: The payload shape for `/programlike-skill-creator` when migration is needed.
      fields:
        target_skill_path: string
        rca_root_cause: string
        defect_types: list[string]
        required_behavior_to_preserve: list[string]
        artifact_changes_already_made: list[string]
        migration_goal: convert-to-program-like | repair-existing-program-like
      invariants:
        - ReformulatePayload exists only when MigrationNeed.needed is true.
    ReformulateDecision:
      role: The final decision consumed by SKILL.md Phase 7.
      fields:
        action: delegate | recommend | none
        migration_need: MigrationNeed
        payload: ReformulatePayload | null
        report_note: string
      invariants:
        - ReformulateDecision.action is none when MigrationNeed.needed is false.
```

## 3. Reasoning SOP

1. $migration_need = JUDGE DefectClassification and CorrectionProposal against ProgramLikeContract
2. $payload = DERIVE ReformulatePayload from $migration_need when migration is needed
3. $decision = CLASSIFY action into delegate, recommend, or none
4. $reformulate_decision = DERIVE ReformulateDecision from MigrationNeed, ReformulatePayload, and $decision
5. ASSERT MigrationNeed, ReformulatePayload, and ReformulateDecision are traceable to Required Axis inputs

## 4. Material Reducer SOP

1. $decision_bundle = DERIVE ReformulateDecision from MigrationNeed, ReformulatePayload, and ReformulateDecision
2. ASSERT $decision_bundle satisfies this reducer output schema:

```yaml
status: complete | blocked
produces:
  ReformulateDecision:
    MigrationNeed:
      needed: boolean
      migration_goal: convert-to-program-like | repair-existing-program-like | none
      evidence: list[string]
    ReformulatePayload:
      target_skill_path: string
      rca_root_cause: string
      defect_types: list[string]
      required_behavior_to_preserve: list[string]
      artifact_changes_already_made: list[string]
      migration_goal: convert-to-program-like | repair-existing-program-like
    ReformulateDecision:
      action: delegate | recommend | none
      migration_need: MigrationNeed
      payload: ReformulatePayload | null
      report_note: string
traceability:
  inputs:
    - DefectClassification
    - CorrectionProposal
    - ProgramLikeContract
  derived:
    - MigrationNeed
    - ReformulatePayload
    - ReformulateDecision
clarifications: []
```
