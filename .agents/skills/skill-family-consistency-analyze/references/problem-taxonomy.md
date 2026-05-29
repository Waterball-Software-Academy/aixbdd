# Problem Taxonomy

## Rules

- `missing_reference_target` — skill / reference / script points to a file that does not exist.
- `broken_relative_path` — a relative path cannot resolve from the file that declares it.
- `stale_moved_file_reference` — a moved file still appears through an older path string.
- `duplicate_ssot` — the same rule or contract appears to be defined in multiple places.
- `ambiguous_ssot_ownership` — a rule or asset has no clear owner skill or owner file.
- `conflicting_rule_definitions` — two artifacts define incompatible behavior for the same topic.
- `private_copy_of_shared_rule` — one skill copies a shared rule instead of linking to the owner.
- `obsolete_reference_still_linked` — a superseded reference is still reachable from active skills.
- `unused_reference_file` — a reference file exists but is not linked by any skill or local reference.
- `unreachable_asset_file` — an asset exists but no resolver, template, or reference can reach it.
- `unowned_generated_artifact` — a generated artifact lacks clear ownership or update authority.
- `contract_drift_skill_script` — SKILL.md says one thing while scripts enforce another.
- `contract_drift_template_reference` — template output conflicts with its declared reference contract.
- `hardcoded_path_bypasses_config` — skill or script hardcodes a path that should come from config or a reference.
- `fallback_violates_fail_stop_policy` — loader falls back silently after a missing reference.
- `reference_type_confusion` — strategy, rule, language asset, runtime instruction, and asset contracts are mixed.
- `circular_dependency` — artifact A requires B while B requires A before either can be loaded.
- `hidden_transitive_dependency` — an artifact needs another file but does not declare it.
- `dead_escalation_target` — a STOP / DELEGATE / slash-command target does not exist.
- `inconsistent_naming_convention` — same kind of artifact uses inconsistent naming styles.
- `over_broad_reference_file` — one reference owns multiple responsibilities that should evolve separately.
- `under_specified_reference_contract` — a reference declares conclusions without inputs, outputs, forbidden cases, or validation.
- `analyzer_blind_spot` — the analyzer excludes a file type that participates in the skill family contract.

## Severity

- HARD FAIL: missing references, broken paths, dead escalation targets, circular dependencies, contradictory rules, silent fallback.
- WARN: unused files, naming inconsistency, over-broad references, under-specified contracts.
- INFO: analyzer blind spots and ownership gaps when no active consumer is affected yet.

## Classification Constraints

- Prefer concrete file-path evidence over semantic speculation.
- Do not report `.tests` oracle drift as a default problem class.
- Do not assume a specific skill family layout; infer skills by locating `SKILL.md`.
