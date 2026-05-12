# Discovery — Reconcile Relevance

## Owned Truth

`/aibdd-discovery` owns the behavior-side truth for one function package:

- user-visible flows
- actor legality and actor participation
- atomic rules
- operation partition at the feature-rule level

If a trigger touches any of those truths, Discovery is the earliest valid reconcile start.

## Classify As Discovery

Choose `aibdd-discovery` as earliest when the trigger implies any of the following:

- add / remove / reorder a user-visible flow
- add / remove / rewrite an atomic rule
- add a new actor or change which actor may perform an action
- split / merge / rename feature-rule files because the operation partition itself changed
- describe a new behavior that cannot be anchored to existing activity / rule truth yet

## Classify As Not Discovery

Do **not** choose Discovery when the trigger is only about:

- API contract request / response shape
- data model / persistence / table / field shape
- dependency edges or test-double policy
- implementation sequencing or internal structure planning
- example rows, scenario outlines, coverage rows, or Given/When/Then phrasing for an already accepted rule

Those belong to `aibdd-plan` or `aibdd-spec-by-example-analyze`.

## Mixed Trigger Rule

If the trigger mixes Discovery concerns with downstream planning or example concerns,
Discovery still wins because it is the earliest affected planner.

## Fallback Rule

If the trigger language is too vague to tell whether the change is behavior-level or only
technical/example-level, classify it as `uncertain` and conservatively start from Discovery.
