# GREEN Wave Allocation Rules

## Purpose

Define how `/aibdd-tasks` slices plan-level implementation waves into each feature phase.

## Rules

1. Do not paste the full global topology into every feature phase.
2. Allocate only the waves that are necessary or strategically beneficial for the current feature.
3. Shared scaffolding may be pulled earlier when it clearly unlocks later features.
4. If multiple feature files share one operation or service spine, say so explicitly in task wording.
5. A wave title should describe a coherent implementation slice, not just list class names.
6. A task item should point at one responsibility, class, module, or collaborator at a time.
7. When parser output is missing, semantic fallback must still produce feature-specific waves rather than generic placeholders.

## Guess-Number Bias

For the guess-number baseline, `05` to `09` share the `createRoomGuess` / `maybeResolveBossTurn` spine.

That means:

- feature `05` may establish the common command backbone
- features `06` to `09` should usually refine boss-action branches instead of pretending they are isolated vertical slices
