# Reasoning Polymorphism Template

> 純 declarative 樣板。用於產生 `reasoning/<context>/<slot>-<name>/POLYMORPHISM.md`。

---

~~~markdown
---
rp_type: polymorphism
id: <context>.<slot>-<polymorphic-slot>
context: <reasoning-context>
slot: "<NN>"
name: <Polymorphic Reasoning Slot>
selector:
  param: <variant-selector-name>
  source: caller | skill_global | upstream_rp
consumes:
  - name: <shared-input>
    kind: material_bundle | required_axis | derived_axis | config | reference
    source: caller | skill_global | upstream_rp | reference | filesystem
    required: true
produces:
  - name: <shared-output>
    kind: material_bundle | derived_axis | decision | cic
    terminal: false
variants:
  - id: <variant-a>
    path: <variant-a-file.md>
    when: <selector predicate>
  - id: <variant-b>
    path: <variant-b-file.md>
    when: <selector predicate>
downstream:
  - <next-rp-id>
---

# <Polymorphic Reasoning Slot>

## Interface Contract

- Selector is controlled by `SKILL.md`, not by this RP.
- Every variant must consume the shared input contract.
- Every variant must produce the shared output contract.
- Variant-specific intermediate axes are allowed but must be reduced back into shared output.

## Variants

| Variant | Path | Use when |
|---|---|---|
| `<variant-a>` | `<variant-a-file.md>` | `<selector predicate>` |
| `<variant-b>` | `<variant-b-file.md>` | `<selector predicate>` |

## Shared Output Shape

Return the selected variant path and shared output shape:

```yaml
selected_variant: <variant-id>
selected_path: <variant-file.md>
produces:
  <shared-output>: <value>
```
~~~

## 填值規則

- `rp_type` must be `polymorphism`.
- `variants[*].path` must resolve relative to this `POLYMORPHISM.md` file.
- `SKILL.md` owns selector resolution and lazy-loads exactly one variant path.
- Variant RP files use `reasoning-phase.template.md` and should set `variant` to the corresponding variant id.
