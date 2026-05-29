# Quality Gate Contract

## Deterministic Gates

`/aibdd-tasks` fails deterministic validation when scaffold or `tasks.md` violates any of these:

- file missing
- feature phase scaffold missing or malformed
- `Phase 1 - Infra setup` missing
- final `Integration` phase missing
- feature phase count does not match impacted feature count
- any feature phase lacks `RED`, `GREEN`, or `Refactor`
- feature phase order does not match impacted feature order
- code-reality wording check fails

## Semantic Veto Conditions

- The artifact is a planning summary instead of an actionable checklist.
- GREEN sections do not contain feature-specific waves.
- Global topology is copied into every feature phase without allocation.
- RED / GREEN / Refactor mention the execute skills but omit the evaluator retry loop.
- Infra or Integration silently disappear instead of rendering an explicit no-work sentence.
- Parser failure causes the skill to stop rather than switch to semantic fallback.
- The model is forced to re-decide deterministic phase scaffold instead of consuming a script-built feature phase scaffold.
- GREEN task wording describes a non-existent class as if it already exists, or describes an already-existing method as if it is certainly missing without existence-aware wording.

## Pass Shape

A passing artifact is concise, structured, repeatable, and directly usable by a downstream implementing agent.
