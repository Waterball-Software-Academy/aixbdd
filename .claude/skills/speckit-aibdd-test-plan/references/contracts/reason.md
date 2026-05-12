# speckit-aibdd-test-plan — Reason Contract

## What reasoning happens where

| Where | Kind | Actor |
|---|---|---|
| Step 2 Reason = Phase 5a Skeleton | **Structural** (AST → Paths) | Python activity-parser (no AI) |
| Step 3 Initial Formulate = Phase 5b Step-fill | **Semantic** (Step → DSL entry match by L2 semantics) | AI |
| Step 4 Clarify | **Interactive** (ask user about missing DSL entries) | `/clarify-loop` skill + user |
| Step 5 Quality Gate | **Validation** (R1–R12 compliance, path coverage, DSL reference integrity) | Script + subagent |

## Step 2 Reason: Structural only

The activity-parser consumes Activity DSL (flat event-flow dialect defined in
`sf-desktop-app-electron/To-Be-整合/README.md`). Node types it recognises:

- `[STEP:N]` — sequential action node
- `[DECISION:Nx]` — branch point
- `[BRANCH:Nx:<guard>]` — branch edge
- `[FORK:Nx]` — split
- `[PARALLEL:Nx]` — parallel fragment
- Start / End markers

Policy 1 path extraction guarantees every Action Node participates in at
least one Path. Policy 2 (exhaustive) is TBD.

## Step 3 Initial Formulate: Semantic step-fill rules

1. For each skeleton step, derive intent (the natural-language annotation the
   parser attached from the Activity node label).
2. Match to a DSL entry by comparing intent to `L2 DSL Semantics`
   (context / role / scope).
3. Use entry's `L1` pattern literally, filling `{param}` placeholders from
   the Activity node annotation (including Data Payload if present).
4. If L3 = `mock`, **do not** embed L4 contract into Scenario text — reviewer
   can inspect the DSL entry to discover the mapping. Test infra applies the
   mock via step def at runtime.

## Step 5: Validator roles

Script-level checks cover objective invariants (tags present, no Scenario
Outline, filename naming). Subagent-level checks cover judgement-heavy R9 /
R11 etc.
