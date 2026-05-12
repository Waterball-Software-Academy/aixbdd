# Reconcile Path and Session Contract

## Target Plan Package

A valid reconcile target must satisfy all of the following:

- the path resolves under `${SPECS_ROOT_DIR}`
- the basename starts with a numeric package prefix such as `01-foo` or `000-bar`
- the resolved path is a directory

The target may be:

- the current plan package (`parent(PLAN_SPEC)`)
- any other numbered plan package inside `specs/`
- a numbered package nested under a boundary package tree such as `specs/backend/packages/01-foo`

## Derived Paths

Given `TARGET_PLAN_PACKAGE`, derive:

- `ARCHIVE_DIR = ${TARGET_PLAN_PACKAGE}/archive`
- `ACTIVE_SESSION_PATH = ${ARCHIVE_DIR}/.reconcile-active.json`
- `RECORD_PATH = ${TARGET_PLAN_PACKAGE}/RECONCILE_RECORD.md`

`archive/` is a permanent sibling of future plan artifacts and is never itself archived.

## Session Lifecycle

### New session

1. create `ACTIVE_SESSION_PATH`
2. mint one UTC timestamp session id (`YYYYMMDDTHHMMSSZ`)
3. archive current root entries into `archive/<session_id>/`
4. keep appending runtime state into the active session JSON
5. when cascade completes, write the final session JSON into `archive/<session_id>/RECONCILE_SESSION.json`
6. remove `ACTIVE_SESSION_PATH`

### In-flight retrigger

1. read `ACTIVE_SESSION_PATH`
2. append the new trigger event
3. recompute earliest planner and replay pointer
4. overwrite `ACTIVE_SESSION_PATH`
5. do not create a new `archive/<timestamp>/`

## Session JSON Shape

```json
{
  "version": 1,
  "session_id": "20260507T161200Z",
  "status": "running",
  "target_plan_package": "specs/backend/packages/01-foo",
  "record_path": "specs/backend/packages/01-foo/RECONCILE_RECORD.md",
  "archive_path": "specs/backend/packages/01-foo/archive/20260507T161200Z",
  "earliest_planner": "aibdd-plan",
  "replay_from": "aibdd-plan",
  "current_pointer": "aibdd-plan",
  "cascade_chain": [
    "aibdd-plan",
    "aibdd-spec-by-example-analyze"
  ],
  "triggers": [
    {
      "at": "2026-05-07T16:12:00Z",
      "kind": "initial",
      "text": "API 回傳缺欄位"
    },
    {
      "at": "2026-05-07T16:14:10Z",
      "kind": "retrigger",
      "text": "同時需要補一條 edge-case example"
    }
  ],
  "events": [
    {
      "at": "2026-05-07T16:12:00Z",
      "type": "classified",
      "earliest_planner": "aibdd-plan",
      "cascade_chain": [
        "aibdd-plan",
        "aibdd-spec-by-example-analyze"
      ]
    }
  ]
}
```

## Pointer Ordering

Planner order is fixed:

1. `aibdd-discovery`
2. `aibdd-plan`
3. `aibdd-spec-by-example-analyze`

`replay_from` is computed by comparing the new earliest planner against `current_pointer`:

- if `new_earliest` is more upstream than `current_pointer`, replay from `new_earliest`
- otherwise replay from `current_pointer`

## Record Lifecycle

`RECONCILE_RECORD.md` is a root-level, human-readable projection of the active or final session JSON.
It is rewritten after:

- session start
- retrigger merge
- archive execution
- session finish
