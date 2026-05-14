---
rp_type: reasoning_phase
id: aibdd-frontend-context-analyze.03-build-context-handoff
context: aibdd-frontend-context-analyze
slot: "03"
name: Build Frontend Context Handoff
variant: web-frontend-only
consumes:
  - name: FrontendContextVectorBundle
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: FrontendContextTruthIndex
    kind: derived_axis
    source: upstream_rp
    required: true
produces:
  - name: FrontendContextHandoff
    kind: derived_axis
    terminal: true
downstream: []
---

# Build Frontend Context Handoff

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: FrontendContextVectorBundle
    required_fields:
      - context_vectors[]
  - name: FrontendContextTruthIndex
    required_fields:
      - dsl_l1_pattern_index
      - handler_groups
```

### 1.2 Search SOP

1. `$vectors` = READ `FrontendContextVectorBundle.context_vectors[]`
2. `$truth` = READ `FrontendContextTruthIndex`
3. LOOP per `$vector` in `$vectors`
   3.1 `$ordered_slots` = DERIVE slot order:
       1. `actor_context` when represented by explicit legal DSL clause; otherwise tag/inherited only
       2. `route_context`
       3. `viewport_time_context`
       4. `data_context`
       5. `ui_context`
       6. `operation_context`
       7. `observable_result`
   3.2 LOOP per `$slot` in `$ordered_slots`
       3.2.1 IF `$slot.status ∈ {not_required,inherited}`: CONTINUE
       3.2.2 IF `$slot.status ∈ {cic_gap,cic_con}`: carry CiC, do not render executable clause
       3.2.3 IF `$slot.status == bound`: create clause candidate from `$slot.dsl_entry_id`, `$slot.dsl_l1_pattern`, `$slot.parameters`, `$slot.binding_keys`
       END LOOP
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: FrontendContextHandoff
  elements:
    FrontendContextHandoff:
      role: "Terminal payload returned to Spec-by-Example caller"
      fields:
        status: "ok|not_applicable|blocked"
        exit_ok: "boolean"
        context_vectors: "FrontendContextVector[]"
        required_clause_candidates: "ContextClauseCandidate[]"
        context_binding_trace: "ContextBindingTrace[]"
        cic_markers: "CiCMarker[]"
      invariants:
        - "No executable candidate exists for a cic_gap/cic_con slot"
        - "Every executable candidate instantiates an existing DSL L1 pattern"
        - "Candidate order preserves userflow context before target operation"
    ContextClauseCandidate:
      role: "A legal frontend context clause candidate for caller to merge into ClauseBinding"
      fields:
        candidate_id: "string"
        context_id: "string"
        order: "integer"
        keyword: "Given|When|Then|And"
        handler: "string"
        preset_name: "web-frontend"
        dsl_entry_id: "string"
        dsl_l1_pattern: "string"
        generated_sentence: "string|null"
        parameters: "dict"
        binding_keys: "string[]"
        requiredness: "hard|conditional|optional"
        reason: "string"
      invariants:
        - "keyword must be compatible with handler-routing.yml"
        - "Gherkin-facing generated_sentence, if present, is business-readable only"
    ContextBindingTrace:
      role: "Trace context slots back to DSL bindings without mutating DSL"
      fields:
        context_id: "string"
        slot: "string"
        dsl_entry_id: "string"
        binding_key: "string"
        binding_kind: "param|datatable|default|assertion|response|data|route|ui"
        target: "string"
```

## 3. Reasoning SOP

1. LOOP per `$vector` in `FrontendContextVectorBundle.context_vectors[]`
   1.1 IF `$vector.exit_ok == false`:
       1.1.1 COPY vector CiC markers into handoff
       1.1.2 CONTINUE candidate creation for bound non-conflicting slots, but final handoff remains `exit_ok=false`
   1.2 `$candidates` = DERIVE ordered executable candidates from bound slots
   1.3 LOOP per `$candidate` in `$candidates`
       1.3.1 ASSERT `$candidate.dsl_l1_pattern` appears in `FrontendContextTruthIndex.dsl_l1_pattern_index[$candidate.dsl_entry_id]`
       1.3.2 `$keyword_ok` = JUDGE `$candidate.keyword` against handler-routing keyword policy for `$candidate.handler`
       1.3.3 IF `$keyword_ok == false`: ADD CiC(CON) and mark handoff `exit_ok=false`
       1.3.4 `$surface_ok` = JUDGE generated Gherkin-facing text contains no raw locator/API/fixture internals
       1.3.5 IF `$surface_ok == false`: ADD CiC(CON) and mark handoff `exit_ok=false`
       END LOOP
   1.4 `$trace` = DERIVE `ContextBindingTrace[]` for every candidate binding key
   END LOOP
2. `$status` = DERIVE:
   - `ok` if vectors non-empty and no hard CiC
   - `blocked` if any hard CiC exists
   - `not_applicable` only when upstream produced no frontend vectors
3. `$exit_ok` = DERIVE `$status == ok`
4. `$handoff` = DERIVE `FrontendContextHandoff`

## 4. Material Reducer SOP

1. EMIT `FrontendContextHandoff`
2. ASSERT every candidate has unique `candidate_id`
3. ASSERT every candidate has `preset_name == web-frontend`
4. ASSERT every candidate is traceable to one DSL entry and one L1 pattern
5. ASSERT `exit_ok=false` whenever unresolved hard context CiC exists
6. ASSERT no `.feature` text is written by this RP
