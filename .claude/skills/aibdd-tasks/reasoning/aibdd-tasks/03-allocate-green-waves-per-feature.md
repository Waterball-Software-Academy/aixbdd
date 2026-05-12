# 03 — Allocate GREEN Waves Per Feature

## Goal

Map plan-level implementation topology into feature-specific GREEN waves.

## Inputs

- ordered feature paths
- feature texts
- `plan.md`
- `research.md`
- `boundary-map.yml`
- parser verdict
- plan-level waves when available
- code symbol index

## Allocation Rules

1. Start from the feature's own behavior slice.
2. Pull in only the implementation slices needed to make that feature green.
3. If a shared backbone unlocks later features, state that explicitly in the current feature phase.
4. Do not repeat the same whole-topology wave list for every feature.
5. Prefer 1-3 waves per feature unless the plan gives a strong reason for more.
6. For every task item, reason about current code reality:
   - class missing -> wording must say create the class
   - class exists but method missing -> wording may say extend the existing class
   - class and method both exist -> wording should say inspect / adjust / reinforce the existing implementation

## Guess-Number Hint

For the guess-number baseline:

- `01` should usually establish room entry persistence + service + router
- `05` often establishes the main guess command backbone
- `06` to `09` often extend boss-action branches on top of `05`
- `10` often emphasizes read model / state reporting
