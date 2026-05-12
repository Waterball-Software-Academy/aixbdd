# `/aibdd-tasks` Role and Contract

## Role

`/aibdd-tasks` is an optional downstream planning skill that converts one completed AIBDD plan package into a structured `tasks.md`.

It does not invent a new architecture. It consumes the current plan package, impacted feature scope, implementation structure, and feature package truth, then rewrites them into a task list that interleaves:

- plan-level implementation topology
- feature-driven TDD phase order
- fixed RED / GREEN / Refactor execution template

## Required Inputs

- `.aibdd/arguments.yml`
- current plan package `plan.md`
- current plan package `research.md` when present
- current plan package `implementation/internal-structure.class.mmd`
- target function package `features/`
- target boundary `boundary-map.yml`

## Outputs

- `${CURRENT_PLAN_PACKAGE}/tasks.md`

## Non-Goals

- It does not replace `/aibdd-plan`.
- It does not write contracts, DSL, DBML, or sequence diagrams.
- It does not directly execute `/aibdd-red-execute`, `/aibdd-green-execute`, or `/aibdd-refactor-execute`.
- It does not write product code, tests, step definitions, or runtime fixtures.

## Completion Contract

The skill is complete when `tasks.md` gives the user a stable markdown task list with:

- `Infra setup` at the start
- one TDD phase per impacted feature
- `Integration` at the end
- `RED` / `GREEN` / `Refactor` sections for every feature phase
- feature-specific GREEN waves rather than a copy-pasted global topology
