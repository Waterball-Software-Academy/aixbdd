# `/aibdd-rewind` Role and Contract

## Role

`/aibdd-rewind` rewinds an AIBDD pipeline on the current working tree to a forward-pointing checkpoint — the moment a chosen phase skill JUST FINISHED. The argument is the **skill name** of that phase (e.g. `aibdd-discovery`). That skill's outputs are preserved; every downstream phase's outputs are deleted, and any kickoff-shape files that downstream phases mutated are reverted to their kickoff skeletons.

It does **not** re-run any AIBDD skill, regenerate any truth, or create new artifacts beyond skeleton reverts.

## Required Inputs

- `.aibdd/arguments.yml` at the workspace root (resolves all path keys via `${VAR}` expansion).
- A target phase-skill name, supplied either as the skill's `ARGUMENTS` payload (e.g. `aibdd-discovery`) or interactively via Phase 1 ASK.
- `references/phase-rollback-rules.yml` — the SSOT mapping from `phase_id` (the phase skill that just finished) to the artifacts produced by the immediate downstream phase that must be erased to reach the checkpoint.

## Outputs

- Filesystem state: downstream phases' artifacts removed; downstream files reverted to kickoff skeletons; downstream-mutated `.feature` files reduced back to their rule-only shape.
- A short user-facing report (deleted/reverted/rule-only counts; chain order; suggested next step = re-run `erases_skill`).
- No reports, no logs, no shadow truth files written.

## Rule Schema

Each entry in `references/phase-rollback-rules.yml` may declare any of:

| Key | Kind | Effect |
|---|---|---|
| `delete_files` | list of literal paths | Remove file if it exists. |
| `delete_files_glob` | list of glob patterns | Remove every matching file. |
| `delete_dirs` | list of directory paths | Remove directory recursively. |
| `revert_to_skeleton` | list of `{path, body}` | Overwrite file with the kickoff-shape body. Idempotent — skipped if content already matches. |
| `revert_feature_to_rule_only` | list of `.feature` glob patterns | Reduce each matching feature file to its rule-only shape per `aibdd-form-feature-spec/references/patterns/rule-only-format.md`: strip Background / Scenario / Scenario Outline / Examples blocks; strip reducer comments (`# @dsl_entry`, `# @binding_keys`, `# @type`, `# @techniques`, `# @dimensions`, `# @given_values`, `# @when_values`, `# @then_values`, `# @values_na`, `# @setup_required`, `# @merge_decision`, `# @cic`, `# @dimension_na`); re-add `@ignore` to the feature header tag line if absent (preserve operation/actor tags); keep `Feature:` line + description + every `Rule:` line (with body). Idempotent — re-running on an already rule-only file is a no-op. |
| `chain_before` | list of `phase_id`s | Prerequisite checkpoints whose rules must be applied first (recursively, depth-first). Used when reaching a checkpoint requires undoing later phases on top of this one's own deletions. |

## Argument Semantic

`/aibdd-rewind <phase-skill-name>` reads as: **"return the workspace to the state it had right after `<phase-skill-name>` completed".** Concretely:

| Argument | What is preserved | What is erased |
|---|---|---|
| `aibdd-kickoff` | `.aibdd/`, `specs/architecture/`, boundary skeleton scaffold | All `/aibdd-discovery` outputs and beyond |
| `aibdd-discovery` | All kickoff state + `activities/`, `features/`, `spec.md`, `discovery-sourcing.md` | All `/aibdd-plan` outputs and beyond |
| `aibdd-plan` | All discovery state + boundary-map / contracts / data / dsl / test-strategy / implementation diagrams | All `/aibdd-spec-by-example-analyze` side artifacts (reports + package coverage) AND every feature file is reduced back to its rule-only shape |
| `aibdd-spec-by-example-analyze` | Same as `aibdd-plan` (terminal phase — exists so chains can target it explicitly) | Nothing further downstream yet |

The argument may be passed with or without a leading slash (`aibdd-plan` and `/aibdd-plan` both resolve).

## Non-Goals

- It does not re-execute the named phase skill or any downstream skill.
- It does not modify `.aibdd/arguments.yml`, `specs/architecture/*`, or any kickoff-owned scaffold.
- It does not delete `app/`, `tests/`, `alembic/`, or any non-AIBDD project file unless the rule table explicitly names it.
- It does not commit, push, or otherwise touch git state.
- It does not rebuild or regenerate any deleted artifact — re-running the appropriate AIBDD skill (`erases_skill`) is the user's next step.

## Completion Contract

The skill is complete when:

1. The selected `phase_id` rule entry has been fully applied (every named file deleted, every named directory removed recursively, every skeleton revert written), including any `chain_before` prerequisite rules.
2. A re-run of the same preview returns an empty delta (idempotency check).
3. The user has received a summary of what changed.

## Idempotency

`/aibdd-rewind` MUST be safe to re-invoke against an already-rewound filesystem. The expected behavior in that case is Phase 4's "nothing to do" branch — the skill emits a notice and exits without writing.

## Forbidden Targets

See `references/safety-guardrails.md`. The skill refuses any `phase_id` not registered in the rule table; it never wipes the kickoff baseline.
