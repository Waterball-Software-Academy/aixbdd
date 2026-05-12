# speckit-aibdd-test-plan — Axis Relevance

## When this Planner is the *first relevant* Planner to backtrack into

Triggers (upstream-first search order):

1. Any change to `activities/*.activity` that affects a Path (adding / removing /
   re-ordering nodes) → **re-run this Planner**
2. Any change to shared `dsl.md` or boundary `dsl.md` that removes / renames an
   entry used by a current `test-plan/*.feature` step → **re-run this Planner**
3. Any change to `contracts/` that affects a mock mapping used by a DSL
   entry that this Planner consumes (via L4) → **re-run this Planner**
4. A `test-plan-rules.md` amendment → **re-run this Planner**

## When *not* this Planner

- Change to `spec.md` body (User Story narrative) — irrelevant to Path
  extraction; does not trigger re-run
- Change to `plan.md` / `data-model.md` that doesn't affect `contracts/` —
  irrelevant
- Change to `tasks.md` — downstream of this Planner, never triggers back-flow
