# tasks.md Shape Contract

## Required Global Shape

`tasks.md` MUST always use this top-level phase order:

1. `# Phase 1 - Infra setup`
2. one feature phase per impacted feature
3. final `# Phase N+1 - Integration`

The document-level shell belongs to `assets/templates/tasks-md.template.md`.

## Per-Feature Phase Shape

Every feature phase MUST contain these second-level headings in order:

1. `## RED`
2. `## GREEN`
3. `## Refactor`

The fixed per-feature shell belongs to `assets/templates/feature-phase.template.md`.

## RED Requirements

- Must mention `/aibdd-red-execute`
- Must mention looping `/aibdd-red-evaluate`
- Must treat evaluator rejection as a retry loop, not a one-shot check

## GREEN Requirements

- Must mention `/aibdd-green-execute`
- Must mention `${CURRENT_PLAN_PACKAGE}/implementation/`
- Must contain one or more `Wave N` groups
- Every wave must contain one or more concrete task items
- Must mention regression / report verification
- Must mention looping `/aibdd-green-evaluate`

## Refactor Requirements

- Must mention `/aibdd-refactor-execute`
- Must mention looping `/aibdd-refactor-evaluate`

## Explicit No-Work Sentences

If there is no extra infra or integration work, `tasks.md` MUST still render an explicit sentence:

- Infra: `本 plan 無額外 Infra setup tasks。`
- Integration: `本 plan 無額外 Integration tasks，僅需完整 acceptance regression。`
