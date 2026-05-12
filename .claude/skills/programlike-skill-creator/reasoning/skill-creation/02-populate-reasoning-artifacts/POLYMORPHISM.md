---
rp_type: polymorphism
id: skill-creation.02-populate-reasoning-artifacts
context: skill-creation
slot: "02"
name: Populate Reasoning Artifacts
selector:
  param: reasoning_complexity
  source: skill_global
consumes:
  - name: reasoning_plan
    kind: decision
    source: upstream_rp
    required: true
produces:
  - name: reasoning_artifact_set
    kind: material_bundle
    terminal: true
variants:
  - id: simple-skill
    path: simple-skill.md
    when: reasoning plan has zero or one RP and no polymorphic slot
  - id: reasoning-heavy-skill
    path: reasoning-heavy-skill.md
    when: reasoning plan has multiple RPs or polymorphic slots
downstream: []
---

# Populate Reasoning Artifacts

## Interface Contract

- `SKILL.md` selects exactly one variant from `reasoning_complexity`.
- Both variants consume `reasoning_plan`.
- Both variants produce `reasoning_artifact_set`.
- Variant-specific intermediate axes must reduce back into the shared output contract.

## Variants

| Variant | Path | Use when |
|---|---|---|
| `simple-skill` | `simple-skill.md` | generated skill needs a minimal or optional reasoning layer |
| `reasoning-heavy-skill` | `reasoning-heavy-skill.md` | generated skill needs multiple RPs or polymorphic reasoning |

## Shared Output Shape

Return:

```yaml
selected_variant: simple-skill | reasoning-heavy-skill
produces:
  reasoning_artifact_set: material_bundle
```
