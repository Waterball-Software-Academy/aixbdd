# Diagram File Naming — Mermaid compound extensions

> LOAD target: skills that write Mermaid under `specs/**` (kickoff architecture, plan package implementation diagrams).
> Aligns with IDE routing: **basename must end with** `*.class.mmd` or `*.sequence.mmd` where the editor distinguishes diagram kind by compound extension before `.mmd`.

## Rules

1. **Class / component class diagrams** (`classDiagram` content)  
   - Filename **must** end with `.class.mmd`.

2. **Sequence diagrams** (`sequenceDiagram` content)  
   - Filename **must** end with `.sequence.mmd`.

3. **Do not** use plain `something.mmd` for class or sequence editor targeting when the toolchain expects compound extensions.

## Canonical AIBDD paths

| Artifact | Path pattern | Owner skill |
|----------|--------------|-------------|
| Boundary topology class diagram | `${TRUTH_ARCHITECTURE_DIR}/component-diagram.class.mmd` | `/aibdd-kickoff` |
| Plan package sequence (per path × kind) | `${PLAN_SEQUENCE_DIR}/<slug>.<kind>.sequence.mmd` where `<kind>` ∈ `happy \| alt \| err` | `/aibdd-plan` |
| Internal structure (structural union of sequences) | `${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd` | `/aibdd-plan` |

`PLAN_SEQUENCE_DIR` / `PLAN_IMPLEMENTATION_DIR` resolve from `arguments.yml` (see `aibdd-core::spec-package-paths.md`).

## Cross References

- Path variables: `aibdd-core::spec-package-paths.md`
- Plan vs boundary ownership: `aibdd-core::artifact-partitioning.md`
