# Spec-by-Example — Reconcile Relevance

## Owned Truth

`/aibdd-spec-by-example-analyze` owns example-layer behavior artifacts derived from accepted
Discovery and Plan truth:

- concrete Scenarios / Scenario Outlines
- Examples tables
- clause bindings to plan DSL entries
- example coverage rows

If a trigger changes only those artifacts while upstream rule and plan truth stay valid,
Spec-by-Example is the earliest valid reconcile start.

## Classify As Spec-by-Example

Choose `aibdd-spec-by-example-analyze` as earliest when the trigger implies any of the following:

- an existing atomic rule needs more or fewer examples, but the rule text itself stays correct
- a Scenario Outline needs different example rows or data-table values
- Given / When / Then phrasing must be refactored to match an existing DSL preset or variant
- coverage rows or example-level edge cases need to be added, removed, or regrouped
- the example file shape changes only because already accepted plan DSL entries changed in wording or variant, without requiring new technical truth

## Classify As Not Spec-by-Example

Do **not** choose Spec-by-Example when the trigger is actually about:

- atomic rule wording, rule split / merge, flow changes, actor changes, or operation partition changes
- API contract, data model, persistence ownership, dependency edge, test strategy, or DSL truth changes

Those belong to `aibdd-discovery` or `aibdd-plan`.

## Mixed Trigger Rule

If example breakage is caused by a missing or wrong plan-level DSL / contract / data truth,
Plan wins because Spec-by-Example may not invent upstream truth.

If example breakage is caused by a wrong rule or wrong flow, Discovery wins because that is the
earliest affected planner.

## Fallback Rule

If the trigger explicitly says the rule is still correct and only the examples are wrong or incomplete,
classify it as Spec-by-Example.
