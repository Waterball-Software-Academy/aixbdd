
---
name: aibdd-dsl-to-isa-interpretation
description: Build the entity-to-table mapping from schema specs, then translate each dsl.yml in place into the active boundary's runtime ISA (params + isa_steps).
metadata:
  user-invocable: true
  source: project-level
---

# SOP
1. EXECUTE 01-table-to-entity/SOP.md
2. EXECUTE 02-dsl-to-isa-mapping/SOP.md