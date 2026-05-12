---
rp_type: reasoning_phase
id: aibdd-plan.01-bind-planning-context
context: aibdd-plan
slot: "01"
name: Bind Planning Context
variant: none
consumes:
  - name: ArgumentsAxis
    kind: required_axis
    source: filesystem
    required: true
  - name: DiscoverySummaryAxis
    kind: required_axis
    source: filesystem
    required: true
produces:
  - name: PlanningContext
    kind: material_bundle
    terminal: false
downstream:
  - aibdd-plan.02-technical-boundary-dispatch
---

# Bind Planning Context

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: ArgumentsAxis
    source:
      kind: filesystem
      path: .aibdd/arguments.yml
    granularity: one AIBDD project argument file
    required_fields:
      - PLAN_SPEC
      - PLAN_REPORTS_DIR
      - TRUTH_BOUNDARY_ROOT
      - TRUTH_FUNCTION_PACKAGE
      - BOUNDARY_PACKAGE_DSL
      - BOUNDARY_SHARED_DSL
      - TEST_STRATEGY_FILE
    optional_fields:
      - BDD_CONSTITUTION_PATH
      - DEV_CONSTITUTION_PATH
    completeness_check:
      rule: all required fields resolve to non-empty paths
      on_missing: STOP
    examples:
      positive:
        - arguments.yml with bound TRUTH_FUNCTION_PACKAGE after Discovery
      negative:
        - arguments.yml that only contains old FEATURE_DIR-style paths
  - name: DiscoverySummaryAxis
    source:
      kind: filesystem
      path: ${PLAN_SPEC} and ${PLAN_REPORTS_DIR}/discovery-sourcing.md
    granularity: one accepted Discovery scope
    required_fields:
      - impacted_boundary
      - function_package_pointer
      - flow_or_rule_indexes
      - blocking_gaps
    optional_fields:
      - relevant_existing_packages
    completeness_check:
      rule: summary points to sourcing report and target function package
      on_missing: STOP
    examples:
      positive:
        - Discovery Sourcing Summary with function package pointer
      negative:
        - raw idea without Discovery sourcing report
```

### 1.2 Search SOP

1. `$args` = READ ArgumentsAxis source
2. `$summary` = READ DiscoverySummaryAxis source
3. `$paths` = DERIVE resolved plan/truth paths from `$args`
4. ASSERT `$paths.truth_function_package` is bound

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: PlanningContext
  element_rules:
    element_vs_field:
      element: independently referenced planning scope or path bundle
      field: scalar path, display name, or status under a scope
  elements:
    PlanPackage:
      role: session-only planning artifact container
      fields:
        root: path
        spec: path
        reports: path
    BoundaryTruth:
      role: long-lived boundary truth root
      fields:
        root: path
        boundary_map: path
        contracts_dir: path
        data_dir: path
        shared_dsl: path
        test_strategy: path
    FunctionPackage:
      role: target function module truth package
      fields:
        root: path
        activities_dir: path
        features_dir: path
        local_dsl: path
    DiscoveryScope:
      role: accepted behavior scope feeding technical planning
      fields:
        impacted_rules: list
        impacted_flows: list
        blocking_gaps: list
```

## 3. Reasoning SOP

1. `$plan_package` = DERIVE PlanPackage from ArgumentsAxis
2. `$boundary_truth` = DERIVE BoundaryTruth from ArgumentsAxis
3. `$function_package` = DERIVE FunctionPackage from ArgumentsAxis
4. `$discovery_scope` = DERIVE DiscoveryScope from DiscoverySummaryAxis
5. ASSERT every derived path belongs to either plan package or truth layer, never both

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE PlanningContext from `$plan_package`, `$boundary_truth`, `$function_package`, `$discovery_scope`
2. ASSERT `$reducer_output` has no unbound target package
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  PlanningContext:
    plan_package: PlanPackage
    boundary_truth: BoundaryTruth
    function_package: FunctionPackage
    discovery_scope: DiscoveryScope
traceability:
  inputs:
    - ArgumentsAxis
    - DiscoverySummaryAxis
  derived:
    - PlanPackage
    - BoundaryTruth
    - FunctionPackage
    - DiscoveryScope
clarifications: []
```
