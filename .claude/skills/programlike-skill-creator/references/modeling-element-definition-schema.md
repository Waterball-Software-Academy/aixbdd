# Modeling Element Definition Schema

`Modeling Element Definition` 是每個 Reasoning Phase 的輸出模型邊界。它必須用 YAML 撰寫，並只描述最後會進入 Material Reducer output bundle 的模型元素。

## Required Shape

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
      nested_fields:
        <NestedFieldName>:
          <field_name>: <type>
```

## Required Keys

- `modeling_element_definition.output_model`
- `modeling_element_definition.element_rules.element_vs_field.element`
- `modeling_element_definition.element_rules.element_vs_field.field`
- `modeling_element_definition.elements`
- `modeling_element_definition.elements.<ElementName>.role`
- `modeling_element_definition.elements.<ElementName>.fields`

## Optional Keys

- `modeling_element_definition.elements.<ElementName>.invariants`
- `modeling_element_definition.elements.<ElementName>.nested_fields`

## Forbidden Keys

These keys are process metadata, not model schema:

- `source_of_truth`
- `classify_rule`

## Element vs Field Rule

An `ElementName` is valid only if it can be independently referenced, traced, revised, or consumed downstream. If a concept cannot stand alone under that test, it must be a field under its parent element.

Examples:

- Good: `Actor.fields.ref`
- Bad: `ActorRef` as a standalone element
- Good: `Step.fields.label`
- Bad: `StepLabel` as a standalone element
- Good: `Branch.fields.guard`
- Bad: `BranchGuard` as a standalone element

## Naming Rule

Use domain-native names. Avoid wrapper terms, intermediate verdict names, and render-format terms unless they are actual output elements.
