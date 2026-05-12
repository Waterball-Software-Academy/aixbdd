# Topology Contract

## Primary Input

`${PLAN_INTERNAL_STRUCTURE}` is the primary implementation topology source.

The preferred path is a Python parser that reads Mermaid `classDiagram` content and returns:

- classes
- dependency pairs
- implementation-order waves

## Output Semantics

`plan_level_waves` means implementation order, not raw arrow order.

If `A` depends on `B`, then `B` must appear in an earlier or same-valid wave than `A`.

## Supported Parser Behavior

The parser should try to handle common class-diagram relations, including:

- direct dependency arrows
- inheritance-like arrows
- aggregation / composition-like arrows

It is acceptable to normalize all supported relations into dependency pairs as long as the resulting wave order is deterministic and documented.

## Fallback Rule

If parsing fails, `/aibdd-tasks` MUST NOT stop.

Instead it must fall back to semantic planning using:

- `plan.md`
- `research.md`
- sequence diagrams when present
- `boundary-map.yml`
- feature files

Parser failure reduces precision but must not prevent `tasks.md` generation.
