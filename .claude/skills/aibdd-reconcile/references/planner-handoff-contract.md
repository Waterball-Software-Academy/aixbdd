# Planner Handoff Contract

`/aibdd-reconcile` is the caller. The cascaded planner is the callee.

## Shared Payload Shape

Every cascaded planner receives a payload with these fields:

| Field | Required | Meaning |
|---|---|---|
| `arguments_path` | yes | Absolute path to `.aibdd/arguments.yml`. |
| `plan_package_path` | yes | Absolute path to the target plan package being reconciled. |
| `trigger_description` | yes | The merged trigger text for the current session. |
| `reconciliation.session_id` | yes | UTC timestamp id for the current session. |
| `reconciliation.earliest_planner` | yes | Earliest planner chosen for this reconcile session. |
| `reconciliation.replay_from` | yes | Planner this invocation should replay from. |
| `reconciliation.cascade_chain` | yes | Ordered suffix chain for this session. |
| `reconciliation.archive_path` | yes | Archive snapshot path for this session. |
| `reconciliation.record_path` | yes | Root-level `RECONCILE_RECORD.md` path. |
| `reconciliation.mode` | yes | `start_new` or `merge_existing`. |

## Discovery Payload

`/aibdd-discovery` may ignore the reconciliation object if it does not need it for runtime decisions,
but the payload must still echo the shared fields so downstream phases have one stable caller contract.

## Plan Payload

`/aibdd-plan` must treat the `reconciliation` object as optional input context.
When present, its `plan.md` output should include a reconciliation narrative block that records:

- trigger description
- earliest planner
- cascade chain
- archive path

When absent, `/aibdd-plan` behaves like a normal forward planning run.

## Spec-by-Example Payload

`/aibdd-spec-by-example-analyze` may ignore the reconciliation object for generation logic,
but it must tolerate the extra fields and must not reject the payload as malformed merely because
reconcile-specific keys are present.
