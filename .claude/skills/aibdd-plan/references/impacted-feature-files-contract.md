# Impacted Feature Files Contract

## Purpose

Define how `/aibdd-plan` records the feature-file subset that the current plan package is expected to drive, so downstream skills can consume a stable scope anchor instead of inferring from free-form prose.

## Output Shape

`plan.md` MUST contain a dedicated `## Impacted Feature Files` section.

Inside that section:

- Each impacted feature file MUST be listed as one bullet.
- Each bullet MUST contain the canonical repo-relative feature path.
- Ordering MUST reflect intended downstream TDD phase order for the current plan package.
- A short rationale MAY be appended after the path, but the path itself is mandatory.

## Selection Rules

1. The list MUST be derived from the current plan scope, not copied blindly from every feature in the package.
2. Every listed path MUST resolve under `${FEATURE_SPECS_DIR}`.
3. When a plan covers the full function package, listing the full ordered feature set is valid.
4. When multiple features share one operation or service slice, list each impacted feature separately; downstream task planning still needs per-feature TDD phases.
5. If the plan cannot confidently narrow the scope below the whole package, it SHOULD emit the full ordered feature list rather than an ambiguous partial subset.

## Downstream Use

- `/aibdd-tasks` treats this section as the primary feature-phase scope source.
- Missing or malformed entries are a plan-quality issue and force downstream fallback reasoning instead of silent omission.
