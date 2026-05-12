# red-usable-l1-l4

## Rules

- `dsl.yml` MUST be YAML with top-level `entries: []`.
- Every entry MUST contain `id`, `source`, `L1`, `L2`, `L3`, and `L4`.
- `L4.source_refs` is normative; top-level `source_refs` is not valid for new work.
- `DSL_KEY_LOCALE` accepts BCP 47 language tags plus `prefer_spec_language`.
- When `DSL_KEY_LOCALE: prefer_spec_language`, L1 placeholders and binding keys SHOULD follow the specification language while physical `target` strings stay technical.
- Every `{placeholder}` in L1 MUST map to exactly one key in either `L4.param_bindings` or `L4.assertion_bindings`.
- `L4.datatable_bindings` is for scenario-visible business inputs intentionally kept out of L1.
- `L4.default_bindings` is for required inputs whose values do not affect the atomic rule; each item MUST include `target`, `value`, `reason`, and `override_via`.
- Operation entries MUST bind every required contract request param/body/header input except excluded transport or ambient headers.
- Binding target prefixes are limited to:
  - `contracts/<file>.yml#...`
  - `data/<file>.dbml#table.column`
  - `data/<file>.yml#entity_id.field`
  - `response:...`
  - `fixture:...`
  - `stub_payload:...`
  - `literal:...`
- `web-backend` entries SHOULD include `L4.preset` with `name`, `sentence_part`, `handler`, and `variant`.
- Operation-backed L1 sentence parameters SHOULD be `<= 3`.
- Datatable parameters SHOULD be `<= 6` after defaults.
- Every L1 sentence MUST be stateless enough for `/aibdd-red` to identify subject, lookup identity, and expected data from that line plus its same-step datatable.
- Do not require `/aibdd-red` to parse `plan.md` prose to find physical mappings.
- Do not translate contract field names, DB anchors, response probes, or operationIds.
- Do not add placeholders only to satisfy technical binding if the placeholder is not meaningful to the rule or lookup.
- Do not omit required operation inputs without an explicit default binding or documented transport exclusion.
- Do not use raw JSON/YAML/object literals as Gherkin datatable cells.
- Deterministic validation MUST enforce placeholder coverage, operation required input coverage, contract/data target existence, DBML anchors, default binding shape, and response-probe consistency.
- Deterministic validation MUST enforce `dsl.yml` file extension for DSL registries.
- Semantic validation SHOULD reject non-stateless L1 sentences and bindings whose key language conflicts with the configured locale.

### Placeholder Binding Branches

- IF `L1` contains `{placeholder}`:
  - BIND the same placeholder name exactly once in `L4.param_bindings` or `L4.assertion_bindings`.
  - TARGET must point to contract, data, response, fixture, stub payload, or literal source.
- IF one placeholder needs multiple physical writes:
  - USE one binding key with multiple explicit targets only when the handler contract supports multi-target binding.
  - OTHERWISE split the business sentence or use datatable/default bindings.
- IF a binding key exists but the placeholder is absent from `L1`:
  - REJECT unless the key is in `datatable_bindings` or `default_bindings`.
- IF a placeholder only exposes a technical transport detail:
  - REMOVE the placeholder.
  - Use `default_bindings` or transport exclusion instead.

### Required Operation Input Branches

- IF the contract operation has required path, query, header, or body fields:
  - EACH required business input MUST be covered by `param_bindings`, `datatable_bindings`, or `default_bindings`.
- IF a required input is transport-only or ambient infrastructure:
  - DOCUMENT it as an explicit exclusion in `L4.transport_exclusions` or equivalent handler-supported field.
- IF a required input has no rule-level meaning and can be deterministic:
  - PUT it in `L4.default_bindings`.
- IF a required input affects the atomic rule or expected behavior:
  - EXPOSE it through `L1` placeholder or same-step datatable.
- IF a required input is hidden in narrative prose:
  - REJECT because `/aibdd-red` cannot synthesize a legal red from prose.

### Datatable And Default Binding Branches

- IF a step needs multiple business fields:
  - USE Gherkin DataTable and `L4.datatable_bindings`.
- IF a cell value would need raw JSON/YAML/object syntax:
  - REJECT and normalize into business columns.
- IF a value is required but invariant across examples:
  - USE `L4.default_bindings` with `target`, `value`, `reason`, and `override_via`.
- IF a default can be overridden by an Example row or DataTable column:
  - DECLARE the override path in `override_via`.
- IF a default changes the business rule being tested:
  - REJECT and expose it in the scenario.

### Stateless L1 Branches

- IF `/aibdd-red` can identify the subject, lookup identity, operation, and expected data from `L1` plus same-step datatable:
  - ALLOW the L1 sentence.
- IF understanding the L1 requires reading `plan.md`, prior scenario prose, or hidden context:
  - REJECT as non-stateless.
- IF the sentence says "the record", "that item", or "the above data" without a same-step identity:
  - REJECT or rewrite with explicit subject identity.
- IF the sentence requires cross-step memory that is not encoded in bindings:
  - REJECT or move the data into the step table.
- IF the sentence is a shared generic Then:
  - It MAY stay short only when `L4.assertion_bindings` or handler source refs supply the precise expected target.

## Examples

### Good: complete DSL entry

```yaml
entries:
  - id: assign-student-to-journey-stage
    source:
      feature: 02-指派學員至旅程階段.feature
      rule: "前置（狀態） - 學員與階段必須存在"
    L1: 顧問將學員「{student_name}」指派至「{stage_name}」階段
    L2:
      keyword: When
      sentence_part: http-operation
    L3:
      operation_id: assignStudentToJourneyStage
    L4:
      source_refs:
        - contracts/crm-student-journey.openapi.yml#/paths/~1students~1{studentId}~1journey-stage/post
      param_bindings:
        student_name:
          target: data/domain.dbml#students.name
          lookup: student_id
        stage_name:
          target: data/domain.dbml#journey_stages.name
          lookup: stage_id
      default_bindings:
        - target: contracts/crm-student-journey.openapi.yml#/components/schemas/AssignStageRequest/properties/requestedBy
          value: consultant
          reason: caller role is invariant for this operation rule
          override_via: examples.requested_by
      preset:
        name: web-backend
        sentence_part: http-operation
        handler: http-operation
        variant: python-e2e
```

Why good:

- Every L1 placeholder has a physical binding.
- Required invariant input is explicit as a default.
- `/aibdd-red` does not need to parse plan prose.

### Good: datatable binding for business fields

```yaml
L1: CRM 中已有以下學員旅程資料
L2:
  keyword: Given
  sentence_part: aggregate-given
L4:
  datatable_bindings:
    student_name:
      target: data/domain.dbml#students.name
    current_stage:
      target: data/domain.dbml#student_journey.stage_name
    intent:
      target: data/domain.dbml#student_journey.intent
  preset:
    name: web-backend
    sentence_part: aggregate-given
    handler: aggregate-given
    variant: python-e2e
```

Why good:

- Multi-field business setup lives in DataTable bindings.
- Columns remain business-level and readable.

### Bad: missing placeholder binding

```yaml
L1: 顧問將學員「{student_name}」指派至「{stage_name}」階段
L4:
  param_bindings:
    student_name:
      target: data/domain.dbml#students.name
```

Why bad:

- `{stage_name}` has no binding.
- `/aibdd-red` cannot derive the stage identifier.

### Bad: hidden required input

```yaml
L1: 顧問安排學員預約
L4:
  source_refs:
    - contracts/crm-student-journey.openapi.yml#/paths/~1appointments/post
  param_bindings:
    student_name:
      target: data/domain.dbml#students.name
```

Why bad:

- Required appointment time is neither a placeholder, datatable binding, default, nor explicit transport exclusion.

Better:

```yaml
L1: 顧問為學員「{student_name}」安排「{appointment_time}」預約
L4:
  param_bindings:
    student_name:
      target: data/domain.dbml#students.name
    appointment_time:
      target: contracts/crm-student-journey.openapi.yml#/components/schemas/CreateAppointmentRequest/properties/appointmentTime
```

### Bad: raw JSON datatable cell

```gherkin
Given CRM 中已有以下學員資料：
  | student_name | profile_json                         |
  | 王小明       | {"intent":"high","source":"trial"}   |
```

Why bad:

- Raw JSON cell hides business columns from DSL bindings.

Better:

```gherkin
Given CRM 中已有以下學員資料：
  | student_name | intent | source |
  | 王小明       | high   | trial  |
```

### Bad: non-stateless Then

```yaml
L1: 系統應保存上述資料
L2:
  keyword: Then
  sentence_part: aggregate-then
```

Why bad:

- The L1 sentence depends on prior prose instead of identifying subject and expected state.

Better:

```yaml
L1: CRM 應保存學員「{student_name}」位於「{stage_name}」階段
L2:
  keyword: Then
  sentence_part: aggregate-then
L4:
  assertion_bindings:
    student_name:
      target: data/domain.dbml#students.name
    stage_name:
      target: data/domain.dbml#student_journey.stage_name
```

### Bad: translated operationId target

```yaml
L3:
  operation_id: 指派學員至旅程階段
```

Why bad:

- Physical contract identifiers must not be translated.

Better:

```yaml
L3:
  operation_id: assignStudentToJourneyStage
```
