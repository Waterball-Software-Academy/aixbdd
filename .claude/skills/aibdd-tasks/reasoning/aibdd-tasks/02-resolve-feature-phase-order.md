# 02 — Resolve Feature Phase Order

## Goal

Produce the ordered feature list that becomes the middle phases of `tasks.md`.

## Primary Rule

Use `plan.md` section `## Impacted Feature Files` as the primary feature-phase scope source.

## Fallback

If the section is missing or malformed:

1. scan `features/`
2. sort by file numbering
3. filter semantically using `plan.md`, `research.md`, and `boundary-map.yml`

## Constraints

- keep order stable
- prefer repo-relative feature paths
- do not silently drop an evidently related feature
- if scope cannot be narrowed confidently, prefer the full ordered package list
