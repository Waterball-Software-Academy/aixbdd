---
rp_type: reasoning_phase
id: skill-rca.00-trace-root-cause
context: skill-rca
slot: "00"
name: Trace Root Cause
variant: none
consumes:
  - name: DefectContext
    kind: required_axis
    source: skill_global
    required: true
  - name: ArtifactSet
    kind: required_axis
    source: skill_global
    required: true
  - name: ArtifactGraphAxis
    kind: required_axis
    source: skill_global
    required: true
  - name: LifecycleSignalAxis
    kind: required_axis
    source: skill_global
    required: true
  - name: StepIndex
    kind: required_axis
    source: skill_global
    required: true
produces:
  - name: RootCauseTrace
    kind: material_bundle
    terminal: false
downstream:
  - skill-rca.01-classify-defect
---

# Trace Root Cause

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: DefectContext
    source:
      kind: skill_global
      path: $$defect
    granularity: one defective skill output with expected behavior
    required_fields:
      - artifact
      - observed_problem
      - expected_behavior
    optional_fields:
      - reproduction_context
      - request_context
    completeness_check:
      rule: artifact, observed_problem, and expected_behavior are non-empty
      on_missing: STOP
    examples:
      positive:
        - A skill produced a malformed proposal and the request states the intended proposal behavior.
      negative:
        - A vague complaint with no defective artifact or expected behavior.
  - name: ArtifactSet
    source:
      kind: skill_global
      path: $$artifact_set
    granularity: all readable files in the target skill directory
    required_fields:
      - SKILL.md
      - references
      - assets
      - reasoning
      - scripts
    optional_fields:
      - clarify_log
    completeness_check:
      rule: SKILL.md is present and optional directories are represented when available
      on_missing: STOP
    examples:
      positive:
        - A parsed map containing SKILL.md and every existing support directory.
      negative:
        - A single copied excerpt without artifact paths.
  - name: ArtifactGraphAxis
    source:
      kind: skill_global
      path: $$artifact_graph
    granularity: one graph of skill artifacts and consumer edges
    required_fields:
      - ArtifactNode
      - ArtifactEdge
    optional_fields:
      - manifest_expectations
      - unknown_edges
    completeness_check:
      rule: every readable artifact has a node and every detected reference has an edge with evidence
      on_missing: STOP
    examples:
      positive:
        - A graph where SKILL.md Phase 3 consumes a reasoning file and the reasoning file consumes a template path.
      negative:
        - A flat file list with no consumer or reference edges.
  - name: LifecycleSignalAxis
    source:
      kind: skill_global
      path: $$lifecycle_signals
    granularity: one lifecycle drift signal or an explicit empty signal list
    required_fields:
      - signal
      - path
      - evidence
      - suggested_fix_kind
    optional_fields:
      - confidence
      - related_paths
    completeness_check:
      rule: every signal cites an ArtifactNode or explicit manifest expectation; empty list is allowed
      on_missing: STOP
    examples:
      positive:
        - orphan_asset signal pointing to an asset template with no inbound consumer edge.
      negative:
        - A vague note that the skill feels messy.
  - name: StepIndex
    source:
      kind: skill_global
      path: $$step_index
    granularity: ordered executable units from SKILL.md
    required_fields:
      - program_counter
      - step_text
      - source_path
      - line_range
    optional_fields:
      - legacy_step_label
      - produces
      - consumes
    completeness_check:
      rule: every executable unit has a stable source location
      on_missing: STOP
    examples:
      positive:
        - A program-counter entry with source path, line range, and step body.
      negative:
        - An unordered summary of what the skill does.
```

### 1.2 Search SOP

1. $defect_material = DERIVE DefectContext from $$defect
2. $artifact_material = DERIVE ArtifactSet from $$artifact_set
3. $artifact_graph = DERIVE ArtifactGraphAxis from $$artifact_graph
4. $lifecycle_material = DERIVE LifecycleSignalAxis from $$lifecycle_signals
5. $step_material = DERIVE StepIndex from $$step_index
6. ASSERT $defect_material, $artifact_material, $artifact_graph, $lifecycle_material, and $step_material satisfy Required Axis completeness

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: RootCauseTrace
  element_rules:
    element_vs_field:
      element: A traceable unit that can be cited, revised, and consumed by downstream RCA phases.
      field: A source location, status flag, or explanatory phrase nested under a traceable unit.
  elements:
    TraceNode:
      role: One examined skill execution point in the causal path.
      fields:
        program_counter: string
        source_path: string
        line_range: string
        input_state: correct | faulty | unknown
        output_state: correct | faulty | unknown
        rationale: string
      invariants:
        - Every TraceNode cites a concrete source_path and line_range.
    ArtifactNode:
      role: One skill artifact participating in the causal graph.
      fields:
        source_path: string
        bucket: skill | references | assets | reasoning | scripts | manifest | other
        role_guess: string
        line_range: string
      invariants:
        - Every readable skill artifact has at most one ArtifactNode identity by source_path.
    ArtifactEdge:
      role: One consumer, producer, or reference relation between skill artifacts.
      fields:
        from_path: string
        to_path: string
        edge_kind: consumer | producer | reference | manifest_expectation | unknown
        evidence: string
      invariants:
        - Every ArtifactEdge evidence points to a link, inline cite, manifest item, path literal, or script path usage.
    LifecycleTraceNode:
      role: One examined artifact lifecycle signal in the causal path.
      fields:
        signal: orphan_asset | duplicate_ssot_candidate | monolith_template_candidate | misbucketed_runtime_flow | deprecated_still_referenced
        source_path: string
        line_range: string
        input_state: correct | faulty | unknown
        output_state: correct | faulty | unknown
        rationale: string
      invariants:
        - LifecycleTraceNode cites the artifact whose lifecycle state caused or failed to prevent the defect.
    RootCause:
      role: The earliest artifact location that introduced the observed defect.
      fields:
        source_path: string
        line_range: string
        program_counter: string
        cause_summary: string
        evidence_nodes: list[TraceNode | LifecycleTraceNode]
      invariants:
        - RootCause must be supported by at least one TraceNode or LifecycleTraceNode.
        - RootCause marks the earliest faulty output whose inputs were still correct or sufficient.
```

## 3. Reasoning SOP

1. $candidate_nodes = CLASSIFY StepIndex by responsibility for DefectContext
2. $graph_nodes = CLASSIFY ArtifactGraphAxis into ArtifactNode and ArtifactEdge elements relevant to DefectContext
3. $lifecycle_nodes = CLASSIFY LifecycleSignalAxis into LifecycleTraceNode elements relevant to DefectContext
4. $trace_nodes = CLASSIFY $candidate_nodes into TraceNode elements
5. $root_step = JUDGE earliest TraceNode where input_state is correct and output_state is faulty
6. $root_lifecycle = JUDGE earliest LifecycleTraceNode where input_state is correct or unknown and output_state is faulty
7. $fallback_root = CLASSIFY ArtifactSet and ArtifactGraphAxis for non-step artifact cause when $root_step and $root_lifecycle are absent
8. $root_cause = DERIVE RootCause from $root_step, $root_lifecycle, or $fallback_root
9. ASSERT TraceNode, LifecycleTraceNode, ArtifactNode, ArtifactEdge, and RootCause are traceable to Required Axis inputs

## 4. Material Reducer SOP

1. $root_cause_trace = DERIVE RootCauseTrace from TraceNode set and RootCause
2. ASSERT $root_cause_trace satisfies this reducer output schema:

```yaml
status: complete | blocked
produces:
  RootCauseTrace:
    ArtifactNode:
      - source_path: string
        bucket: skill | references | assets | reasoning | scripts | manifest | other
        role_guess: string
        line_range: string
    ArtifactEdge:
      - from_path: string
        to_path: string
        edge_kind: consumer | producer | reference | manifest_expectation | unknown
        evidence: string
    TraceNode:
      - program_counter: string
        source_path: string
        line_range: string
        input_state: correct | faulty | unknown
        output_state: correct | faulty | unknown
        rationale: string
    LifecycleTraceNode:
      - signal: orphan_asset | duplicate_ssot_candidate | monolith_template_candidate | misbucketed_runtime_flow | deprecated_still_referenced
        source_path: string
        line_range: string
        input_state: correct | faulty | unknown
        output_state: correct | faulty | unknown
        rationale: string
    RootCause:
      source_path: string
      line_range: string
      program_counter: string
      cause_summary: string
      evidence_nodes: list[TraceNode | LifecycleTraceNode]
traceability:
  inputs:
    - DefectContext
    - ArtifactSet
    - ArtifactGraphAxis
    - LifecycleSignalAxis
    - StepIndex
  derived:
    - ArtifactNode
    - ArtifactEdge
    - TraceNode
    - LifecycleTraceNode
    - RootCause
clarifications: []
```
