---
rp_type: reasoning_phase
id: aibdd-spec-by-example-analyze.01-index-input-truth
context: aibdd-spec-by-example-analyze
slot: "01"
name: Index Plan Output Truth
variant: plan-output-consumer
consumes:
  - name: PlanOutputAxis
    kind: required_axis
    source: caller
    required: true
  - name: ConstitutionAxis
    kind: required_axis
    source: filesystem
    required: true
  - name: DslL1PatternAxis
    kind: derived_axis
    source: plan_dsl
    required: true
produces:
  - name: IndexedTruthModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-spec-by-example-analyze.02-classify-rule-test-strategy
---

# Index Plan Output Truth

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: PlanOutputAxis
    source:
      kind: caller
      resolver: ".claude/skills/aibdd-plan/scripts/python/resolve_plan_paths.py <arguments.yml>"
    granularity: "one resolved /aibdd-plan output bundle"
    required_fields:
      - features_dir
      - truth_function_package
      - boundary_package_dsl
      - boundary_shared_dsl
      - truth_boundary_root
      - test_strategy_file
      - plan_reports_dir
      - plan_implementation_dir
    optional_fields:
      - contracts_dir
      - data_dir
    completeness_check:
      rule: "all downstream truth paths are resolved by /aibdd-plan, not guessed"
      on_missing: STOP
  - name: ConstitutionAxis
    source:
      kind: filesystem
      path: "${BDD_CONSTITUTION_PATH}"
    granularity: "one BDD constitution document"
    required_fields:
      - filename.convention
      - filename.title_language
    completeness_check:
      rule: "filename axes are resolvable and not TODO/unknown"
      on_missing: STOP
  - name: PlanDslAxis
    source:
      kind: filesystem
      paths:
        - "${BOUNDARY_PACKAGE_DSL}"
        - "${BOUNDARY_SHARED_DSL}"
    granularity: "dsl.yml entries produced by /aibdd-plan"
    required_fields:
      - entries[].id
      - entries[].L1
      - entries[].L4.surface_kind
      - entries[].L4.preset
      - entries[].L4.source_refs
      - entries[].L4.param_bindings
      - entries[].L4.datatable_bindings
      - entries[].L4.default_bindings
      - entries[].L4.assertion_bindings
    completeness_check:
      rule: "each feature file under FEATURE_SPECS_DIR has a non-empty candidate DSL pool (package registry)"
      on_missing: cic
```

### 1.2 Search SOP

1. `$plan_paths` = READ `PlanOutputAxis`
2. `$constitution` = READ `ConstitutionAxis`
3. `$features` = ENUM `*.feature` under `$plan_paths.features_dir`
4. `$package_dsl` = READ `$plan_paths.boundary_package_dsl`
5. `$shared_dsl` = READ `$plan_paths.boundary_shared_dsl` if exists
6. `$contracts` = READ OpenAPI documents under `$plan_paths.truth_boundary_root/contracts` if exists
7. `$data_truth` = READ DBML files under `$plan_paths.truth_boundary_root/data` if exists
8. `$test_strategy` = READ `$plan_paths.test_strategy_file`
9. `$plan_quality` = READ `${plan_reports_dir}/aibdd-plan-quality.md` if exists
10. ASSERT `$features` is non-empty
11. ASSERT `$package_dsl.entries[]` is present
12. `$dsl_entries` = MERGE package and shared DSL entries（full registry for lookup）
13. `$dsl_l1_pattern_index` = DERIVE canonical Given/When/Then strings from each `entry.L1` in `$dsl_entries`（`given` / `when` / `then[]`），keyed by `entry.id`
14. LOOP per `$feature_path` in `$features` until all target files are scanned
    14.1 `$feature_text` = READ `$feature_path`
    14.2 `$rules` = PARSE exact `Rule:` blocks byte-for-byte
    14.3 `$operation_gate` = JUDGE `$feature_text` is operation-wise
    14.4 `$rel` = path of `$feature_path` relative to `$plan_paths.features_dir`
    14.5 `$matching_dsl_entries` = ALL `entries[]` from `$package_dsl`（package-local candidate pool；後續 RP 依 operation / sentence scope 收窄）
    14.6 IF `$matching_dsl_entries` is empty:
         14.6.1 `$cic` = DERIVE CiC(GAP) "package DSL registry empty — cannot bind feature"
    14.7 ASSERT `$rules` preserves rule title and body text byte-for-byte
    END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: IndexedTruthModel
  element_rules:
    element_vs_field:
      element: "An independently traceable input truth unit consumed by later RP phases"
      field: "A scalar attribute or raw text slice nested under an indexed truth unit"
  elements:
    PlanPathIndex:
      role: "Resolved /aibdd-plan output paths"
      fields:
        features_dir: "path"
        truth_function_package: "path"
        boundary_package_dsl: "path"
        boundary_shared_dsl: "path"
        contracts_dir: "path|null"
        data_dir: "path|null"
        test_strategy_file: "path"
        plan_quality_report: "path|null"
    PlanDslIndex:
      role: "Plan-owned DSL entries and physical binding surface"
      fields:
        entries: "DslEntry[]"
        feature_to_entries: "dict<feature_relative_path,DslEntry[]>"
        preset_names: "string[]"
      invariants:
        - "BDD Analyze may read and reference entries, never create or mutate them"
        - "Operation entry bindings are the only legal When/Then physical mapping source"
        - "feature_to_entries lists package-local candidates; downstream RPs must not assume one-to-one without narrowing"
    ContractIndex:
      role: "OpenAPI operation and schema lookup"
      fields:
        operations: "dict<operationId,OpenApiOperation>"
        required_inputs: "dict<operationId,string[]>"
        response_fields: "dict<operationId,string[]>"
    DataIndex:
      role: "DBML state/persistence lookup"
      fields:
        tables: "dict<table,fields[]>"
        refs: "string[]"
    DslL1PatternIndex:
      role: "Canonical plan DSL L1 step patterns per entry id — mechanical compliance with check_preset_compliance.py"
      fields:
        patterns_by_entry_id: "dict<entry_id,set<canonical_l1>>"
      invariants:
        - "No RP may invent a Gherkin step absent from the selected DSL entry L1 set or shared DSL support entry"
    FeatureRuleIndex:
      role: "Preserve target feature files and exact Rule blocks"
      fields:
        files: "FeatureRuleFile[]"
      nested_fields:
        FeatureRuleFile:
          path: "path"
          relative_path: "path"
          dsl_entry_ids: "string[]"
          rules: "RuleSlice[]"
          operation_gate_ok: "boolean"
        RuleSlice:
          rule_id_hint: "string"
          raw_rule_title_line: "string"
          body_lines: "string[]"
```

## 3. Reasoning SOP

1. `$plan_path_index` = DERIVE `PlanPathIndex` from `PlanOutputAxis`
2. `$plan_dsl_index` = DERIVE `PlanDslIndex` from package/shared DSL entries + per-feature candidate pool（§1.2 step 15）
3. ASSERT every DSL entry has `L4.preset.name`, `L4.surface_kind`, and `L4.source_refs`
4. `$contract_index` = DERIVE OpenAPI operation index from contract files
5. `$data_index` = DERIVE DBML table/field index from data files
6. `$dsl_l1_pattern_index` = DERIVE `DslL1PatternIndex` from merged DSL `L1` blocks
7. `$feature_rule_index` = DERIVE `FeatureRuleIndex` from scanned feature files
8. LOOP per `$file` in `$feature_rule_index.files` until all files checked
   8.1 ASSERT `$file.rules` is not empty, else mark CiC(CON)
   8.2 ASSERT `$file.operation_gate_ok == true`, else mark CiC(CON)
   8.3 ASSERT `$file.dsl_entry_ids` is not empty, else mark CiC(GAP) and stop this file
   8.4 ASSERT each `$file.rules[]` preserves exact rule wording
   END LOOP
9. `$indexed_truth_model` = DERIVE `IndexedTruthModel` from path, DSL, contract, data, L1 pattern index, test-strategy, and feature indexes
10. ASSERT `$indexed_truth_model` contains all elements declared in Modeling Element Definition

## 4. Material Reducer SOP

1. EMIT `IndexedTruthModel` with:
   1.1 `plan_paths`: `PlanPathIndex`
   1.2 `plan_dsl_index`: `PlanDslIndex`
   1.3 `contract_index`: `ContractIndex`
   1.4 `data_index`: `DataIndex`
   1.5 `test_strategy`: parsed strategy truth
   1.6 `dsl_l1_pattern_index`: `DslL1PatternIndex`
   1.7 `files[]`: `FeatureRuleIndex.files[]`
   1.8 `cic_markers[]`: CiC(GAP|CON) emitted during sourcing
2. ASSERT every `files[].rules[]` has `rule_id_hint`, `raw_rule_title_line`, and `body_lines`
3. ASSERT every `files[].dsl_entry_ids[]` points to a real DSL entry
4. ASSERT every CiC marker has `kind`, `where`, and `text`
