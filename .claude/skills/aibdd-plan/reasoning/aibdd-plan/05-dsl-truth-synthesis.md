---
rp_type: reasoning_phase
id: aibdd-plan.05-dsl-truth-synthesis
context: aibdd-plan
slot: "05"
name: DSL Truth Synthesis
variant: none
consumes:
  - name: BoundaryDispatchModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ExternalSurfaceModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ImplementationModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: HandlerRoutingAxis
    kind: required_axis
    source: reference
    required: true
  - name: DSLContractAxis
    kind: required_axis
    source: reference
    required: true
produces:
  - name: DSLDeltaModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-plan.06-handoff-graph
---

# DSL Truth Synthesis

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: HandlerRoutingAxis
    source:
      kind: reference
      path: .claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml
    granularity: one clause or candidate L1 line → matched `routes[]` (`keyword` ∪ `sentence_part` ∪ `handler` ∪ semantic)
    required_behavior:
      - CLASSIFY each candidate business clause by matching its Gherkin keyword position (`Given`/`When`/`Then`/`Background`) against `routes[].keyword`
      - CHOOSE `sentence_part` and `handler` only from the matched route policy (for `web-backend`, `sentence_part` MUST equal `handler`)
      - FORBID implicit handler selection without citing the matched route index or `sentence_part` in the derivation trace
    maps_to:
      - L3.type
      - L4.surface_kind
      - L4.preset.handler
      - L4.preset.sentence_part
    on_missing: STOP
  - name: DSLContractAxis
    source:
      kind: reference
      path: references/dsl-output-contract.md and references/preset-contract.md
    granularity: one DSL entry contract
    required_fields:
      - L1
      - L2
      - L3
      - L4
      - param_bindings
      - assertion_bindings
      - source_refs
      - preset_reference_when_backend
    optional_fields:
      - datatable_bindings
      - default_bindings
      - fixture_upload
      - external_stub
    completeness_check:
      rule: every changed entry can be consumed by red without guessing
      on_missing: STOP
    examples:
      positive:
        - DSL entry with operation surface, contract refs, parameter and assertion bindings
      negative:
        - DSL entry with only L1 sentence and summary text
```

### 1.2 Search SOP

1. `$dispatch` = READ BoundaryDispatchModel
2. `$external` = READ ExternalSurfaceModel
3. `$implementation` = READ ImplementationModel
4. `$handler_routing` = READ HandlerRoutingAxis (`routes[]` keyword policy + `handlers.*` L4 binding requirements)
5. `$contract` = READ DSLContractAxis
6. `$locale` = READ planner binding `$$dsl_key_locale` (`prefer_spec_language` or BCP 47 language tag). When `prefer_spec_language`, L1 `{tokens}` labels and YAML map keys SHOULD align with localized spec wording (natural zh-Hant wording with embedded English identifiers allowed). Contract operation field names referenced in binding **targets** stay technical English paths.
7. ASSERT `$contract` defines binding source kinds

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: DSLDeltaModel
  element_rules:
    element_vs_field:
      element: independently reusable DSL entry or no-op decision
      field: binding, source pointer, or preset field under an entry
  elements:
    DSLEntry:
      role: exact business sentence to physical surface mapping
      fields:
        id: string
        scope: local | shared
        source: map
        L1: map
        L2: map
        L3: map
        L4: map
    ParameterPressureProfile:
      role: atomic-rule-driven readability plan for an operation-backed DSL entry
      fields:
        operation_ref: string
        required_inputs: list
        sentence_parameters: list
        datatable_parameters: list
        default_parameters: list
        atomic_rule_basis: map
        sentence_parameter_count: integer
        datatable_parameter_count: integer
        required_input_coverage: complete | blocked
        stateless_identity:
          subject: string
          lookup_identity: list
          expected_data_or_effect: list
          status: complete | blocked
    ParameterBinding:
      role: value injection from sentence placeholder to callable source
      fields:
        placeholder: string
        binding_kind: contract_field | data_field | response_path | fixture_path | stub_payload_field | literal
        target: string
    DatatableBinding:
      role: explicit scenario table value injection for operation inputs that are business-relevant but not sentence-critical
      fields:
        column: string
        binding_kind: contract_field | data_field | response_path | fixture_path | stub_payload_field | literal
        target: string
        override_allowed: true
    DSLDefaultBinding:
      role: business-common value for required inputs whose variation does not affect the atomic rule under test
      fields:
        name: string
        binding_kind: contract_field | data_field | response_path | fixture_path | stub_payload_field | literal
        target: string
        value: scalar | map | list
        reason: string
        override_via: datatable | disallowed
    AssertionBinding:
      role: expected value mapping for Then verification
      fields:
        expected_name: string
        binding_kind: contract_field | data_field | response_path | fixture_path | stub_payload_field | literal
        target: string
    DSLNoOp:
      role: explicit no-change result when all required DSL entries already exist
      fields:
        reason: string
        verified_existing_entries: list
```

## 3. Reasoning SOP

1. `$classified` = FOR each atomic-rule or feature clause candidate, CLASSIFY against `$handler_routing.routes` using the clause’s Gherkin keyword line **and** the route `semantic` text until exactly one `(sentence_part, handler)` tuple is justified; EMIT explicit `sentence_part` + route justification per candidate for traceability
2. FOR each classified clause, PROJECT `(sentence_part, handler)` → initial (`L3.type`, `L4.surface_kind`, `L4.preset.handler`) using `handlers.<handler>` requirements in `$handler_routing`; ADJUST only when `DSLContractAxis` forces a narrower surface compatible with that handler (document reason in derivation trace)
3. `$entries` = DERIVE DSLEntry set from `$classified`, rule dispatch, provider operations, implementation targets, and existing DSL
3.A `$persistence_entities` = PARSE every aggregate-root entity from `boundary-map.yml#persistence_ownership` ∪ every top-level `Table` declared in `${TRUTH_BOUNDARY_ROOT}/data/*.dbml`
3.B `$entity_builder_coverage` = MATCH each `$persistence_entities[*]` against `$entries`：required match condition = `entry.L4.preset.handler == "aggregate-given"` AND `entry.L4.source_refs.data` 指向該 entity 的 primary table
3.C **Composite aggregate-given 不豁免規則**：若一條 aggregate-given entry 同時 seed 多個 entity rows（譬如 `student-assigned` 同時影響 student / journey / stage / assignment），其底層 base entity（student / journey / stage）**仍須各自有獨立的 base aggregate-given entry**。Composite 只代表「組合語意」，不代表「base entity 已有 builder」
3.D ASSERT `$entity_builder_coverage` 對每個 `$persistence_entities` 都標記為 `covered`；任一 `not_covered` 視為 plan-level gap，不得繼續落 DSL（fail back to caller / `/aibdd-plan` Phase 6 ASSERT 19.A）
4. `$required_inputs` = DERIVE operation required inputs for each operation-backed DSLEntry from contract request params/body/headers after deterministic transport-header exclusions
5. `$pressure_profiles` = DERIVE ParameterPressureProfile set by classifying each required input against the feature's atomic rules:
   5.1 sentence-critical → the input value changes the rule being tested
   5.2 datatable-worthy → the input is business-relevant variation but not the sentence focus
   5.3 defaultable → the input value does not affect the majority system behavior covered by the atomic rules and can use a business-common value
6. LOOP per `$profile` in `$pressure_profiles` (max 3 refinement passes)
   6.1 IF count(`$profile.sentence_parameters`) <= 3:
       6.1.1 KEEP those parameters as L1 placeholders
   6.2 IF count(`$profile.sentence_parameters`) > 3:
       6.2.1 MOVE non-core atomic-rule parameters from sentence to datatable until sentence count <= 3
   6.3 IF count(`$profile.sentence_parameters`) + count(`$profile.datatable_parameters`) > 6 OR any parameter is atomic-rule-unrelated:
       6.3.1 DERIVE DSLDefaultBinding candidates with explicit atomic-rule reason and business-common value
       6.3.2 MOVE valid defaultable parameters to `$profile.default_parameters`
       6.3.3 RE-RUN #6.1 from the refined explicit parameter set
   END LOOP
7. `$param_bindings` = DERIVE ParameterBinding set for every L1 placeholder, fixture parameter, and stub payload field that remains sentence-critical
8. `$datatable_bindings` = DERIVE DatatableBinding set for explicit business parameters moved out of L1 but still scenario-visible
9. `$default_bindings` = DERIVE DSLDefaultBinding set for required inputs proven defaultable by atomic-rule analysis; each default MUST be overrideable by datatable unless the contract forbids variation
10. `$assertion_bindings` = DERIVE AssertionBinding set for every Then expected value and response/state verifier
11. `$stateless_profiles` = DERIVE for every L1 sentence:
    11.1 business subject
    11.2 lookup identity visible in L1 or same-step datatable
    11.3 expected data/effect for assertions
    11.4 ID-like keys named with `ID`
    11.5 dynamic ID references only in `$<unique business identifier>.id` form
12. `$datatable_projection` = DERIVE whether datatable bindings are business projections:
    12.1 raw JSON/YAML/DTO/DB-shaped cells are blocked
    12.2 nested aggregates use grouped business columns with `group` and `item_field`
13. `$shared_template_entries` = DERIVE canonical backend shared DSL entries from `aibdd-core/assets/boundaries/web-backend/shared-dsl-template.yml` when `BOUNDARY_SHARED_DSL` is missing those entries; resolve `<backend-variant-id>` from boundary variant
14. `$no_op` = DERIVE DSLNoOp only when all needed local and shared entries already exist and are red-usable under the readability, coverage, statelessness, and shared-template gates
15. ASSERT each DSLEntry has all four layers
16. ASSERT each placeholder has exactly one ParameterBinding or is explicitly an assertion placeholder
17. ASSERT sentence parameter count <= 3 for each operation-backed DSLEntry
18. ASSERT datatable parameter count <= 6 for each operation-backed DSLEntry after defaults
19. ASSERT union(ParameterBinding targets, DatatableBinding targets, DSLDefaultBinding targets) covers every non-excluded required operation input
20. ASSERT every DSLDefaultBinding has atomic-rule justification, target, value, and override policy
21. ASSERT each Then expected value has AssertionBinding
22. ASSERT each L1 satisfies Stateless DSL discipline
23. ASSERT datatable bindings do not carry raw technical payloads
24. ASSERT backend entries reference `web-backend` handler and variant when applicable
25. ASSERT external dependency entries use `external-stub`, not internal mock
26. ASSERT fixture upload entries define fixture source, invocation, response, state/file verifier, and missing-file behavior
27. ASSERT every aggregate-root entity declared in `boundary-map.yml#persistence_ownership` ∪ `${TRUTH_BOUNDARY_ROOT}/data/*.dbml` 都對應至少一條 base aggregate-given DSL entry；composite aggregate-given **不豁免**底層 entity 的獨立 builder 義務（`$entity_builder_coverage` 全 covered）

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE DSLDeltaModel from `$entries`, `$pressure_profiles`, `$param_bindings`, `$datatable_bindings`, `$default_bindings`, `$assertion_bindings`, `$stateless_profiles`, `$shared_template_entries`, `$no_op`
2. ASSERT `$reducer_output` can render local/shared DSL files
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  DSLDeltaModel:
    entries: list[DSLEntry]
    pressure_profiles: list[ParameterPressureProfile]
    no_op: DSLNoOp | null
traceability:
  inputs:
    - BoundaryDispatchModel
    - ExternalSurfaceModel
    - ImplementationModel
    - HandlerRoutingAxis
    - DSLContractAxis
  derived:
    - DSLEntry
    - ParameterPressureProfile
    - ParameterBinding
    - DatatableBinding
    - DSLDefaultBinding
    - AssertionBinding
    - DSLNoOp
clarifications: []
```
