# Reasoning Phase Template

> 純 declarative 樣板。用於產生 `reasoning/<context>/<slot>-<name>.md`。

---

~~~markdown
---
rp_type: reasoning_phase
id: <context>.<slot>-<reasoning-phase-name>
context: <reasoning-context>
slot: "<00|01|02|...>"
name: <Reasoning Phase Name>
variant: none
consumes:
  - name: <input-axis-or-bundle>
    kind: material_bundle | required_axis | derived_axis | config | reference
    source: caller | skill_global | upstream_rp | reference | filesystem
    required: true
produces:
  - name: <output-axis-or-bundle>
    kind: material_bundle | derived_axis | decision | cic
    terminal: false
downstream:
  - <next-rp-id>
---

# <Reasoning Phase Name>

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: <AxisName>
    source:
      kind: caller | skill_global | upstream_rp | reference | filesystem
      path: <optional path or RP id>
    granularity: <one precise unit>
    required_fields:
      - <field>
    optional_fields:
      - <field>
    completeness_check:
      rule: <machine-readable or prose invariant>
      on_missing: STOP | ASK | fallback | mark_unknown | cic
    examples:
      positive:
        - <what counts as this axis>
      negative:
        - <what does not count as this axis>
```

### 1.2 Search SOP

1. `$source` = READ <input source>
2. `$material` = EXTRACT <axis candidates> from `$source`
3. ASSERT `$material` satisfies Required Axis completeness
4. IF information gap exists:
   4.1 `$clarification` = ASK "<minimal clarification question>"
   4.2 `$material2` = DERIVE clarified material from `$material` and `$clarification`

## 2. Modeling Element Definition

Define the output model elements as YAML, using `references/modeling-element-definition-schema.md`:

```yaml
modeling_element_definition:
  output_model: <output-axis-or-bundle>
  element_rules:
    element_vs_field:
      element: <what counts as an independently modeled unit>
      field: <what must remain nested under an element>
  elements:
    <ElementName>:
      role: <domain-native purpose>
      fields:
        <field_name>: <type or nested element ref>
      invariants:
        - <semantic invariant>
```

Rules:

- Use the domain's existing nouns. Do not invent synonym layers when a clear domain term already exists.
- Include only model elements that can appear in `<output-axis-or-bundle>` emitted by Material Reducer SOP.
- Put element attributes under `fields`; do not promote fields into standalone elements.
- A concept is an element only if it can be independently referenced, traced, revised, or consumed downstream. Otherwise it is a field.
- Do not include intermediate reasoning variables such as `<Thing>Verdict`, `<Thing>Check`, temporary classifications, scoring passes, or validation booleans unless they are explicit output elements.
- Do not include render / format / projection concepts unless this RP's output is itself a render / format / projection artifact.
- Do not add `source_of_truth` or `classify_rule`; those are process metadata, not schema fields.
- Put process-only judgments in `## 3. Reasoning SOP`, not here.

## 3. Reasoning SOP

1. `$classified` = CLASSIFY `$material` into `modeling_element_definition.elements`
2. `$result_elements` = DERIVE `<ElementName>` set from `$classified`
3. ASSERT `$result_elements` traceable to Required Axis inputs

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE `<output-axis-or-bundle>` from `$result_elements`
2. ASSERT any ASK result that changed downstream behavior is represented in `$reducer_output`
3. ASSERT `$reducer_output` satisfies this reducer output schema:

```yaml
status: complete | needs_clarification | blocked
produces:
  <output-axis-or-bundle>: <value>
traceability:
  inputs:
    - <RequiredAxis>
  derived:
    - <ElementName>
clarifications:
  - <ASK binding or none>
```
~~~

## 填值規則

- `rp_type` must be `reasoning_phase`.
- `id` must be stable and match downstream references.
- `Required Axis` must be machine-readable YAML under `### 1.1 Required Axis`.
- `consumes[*].kind == required_axis` must have a same-named Required Axis entry.
- ASK is allowed, but ASK outputs must be traceable in reducer output.
- Modeling Element Definition must be YAML with `modeling_element_definition.elements`.
- Modeling Element Definition must separate elements from fields. If a term cannot be independently referenced / traced / revised, make it a field under its parent element.
- Modeling Element Definition must not include forbidden schema keys from `references/modeling-element-definition-schema.md`.
- If a name ends in `Verdict`, `Check`, `Pass`, `Score`, `Draft`, or `Candidate`, verify it is truly part of the output contract; otherwise move it to Reasoning SOP.
