# Safety Guardrails

## Forbidden / Unknown Rewind Targets

Under the forward-checkpoint argument model (`/aibdd-rewind <phase-skill>`),
the skill MUST refuse any `phase_id` not registered in
`references/phase-rollback-rules.yml`. That single guard subsumes the older
"before-kickoff" prohibition: there is no rule entry whose checkpoint sits
before the kickoff baseline, so the kickoff scaffold cannot be wiped through
this skill.

The unknown-target branch is enforced by Phase 1 step 18.

## Path Sandbox

Every absolute path produced by `${VAR}` expansion of a rule's `delete_files`,
`delete_files_glob`, `delete_dirs`, or `revert_to_skeleton.path` entry MUST
resolve **strictly inside** the workspace root that owns `.aibdd/arguments.yml`.

If any resolved path escapes the workspace root (parent traversal, symlink,
absolute prefix outside the root), the skill MUST stop before executing any
deletion.

## Confirmation Gate

`/aibdd-rewind` MUST present the full preview (Phase 3) and receive an
explicit `apply` confirmation (Phase 4) before any destructive operation.
The skill MUST NOT short-circuit confirmation, even when invoked with a
target argument.

## What `aibdd-rewind` MUST NOT Touch

- `.git/` directory
- `app/`, `tests/`, `alembic/` (unless the rule table explicitly names a path under them)
- Any file outside the workspace that owns `.aibdd/arguments.yml`
- `.claude/skills/` (skill source code, never product output)

## Recovery from Partial Failure

If `execute_rollback.py` partially succeeds and Phase 6 verification fails,
the skill MUST stop and surface the residual delta. It MUST NOT auto-retry
destructive operations or attempt to "rebuild forward" the missing artifacts.
