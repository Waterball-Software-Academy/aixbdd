# Refactor Move Policy

Refactor changes structure without changing externally observable behavior.

## Protected Behavior

These surfaces must not change:

- API contract
- DB schema
- IPC name or contract
- runtime feature content
- step-def matcher
- fixture contract
- BDD stack runtime references
- testability-plan anchor signature

## Candidate Priority

Candidate moves are considered in this order:

- SOLID: single responsibility, dependency direction, and open-closed pressure
- DRY: only three or more real repetitions justify abstraction
- naming: business language, consistent terminology, no unclear abbreviation
- layering: constitution-defined module and boundary ownership
- meta cleanup: stale TODOs and comments that no longer explain behavior

Two repetitions are not enough to extract a helper automatically.

## Move Size

- One move changes one structural idea.
- Each move is immediately followed by the target acceptance runner.
- A red runner after a move means the move is reverted immediately.
- Reverted moves are recorded as risky and not stacked with later moves.

## Interaction Gates

These require explicit user approval before execution:

- cross-file move
- helper extraction
- test or step-def refactor
- fixture contract change
- any cleanup outside the target feature-file protection scope

## Scope Shrink

After repeated risky moves, scope narrows from multi-feature target set to one
feature file, then to the smallest related product-code region. Refactor stops
instead of forcing a broad structural change through a weak safety net.
