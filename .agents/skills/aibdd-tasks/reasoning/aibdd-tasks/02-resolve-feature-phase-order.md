# 02 — Resolve Feature Phase Order

## Goal

Produce the ordered feature list that becomes the middle phases of `tasks.md`.

## Primary Input

Start from matrix-derived membership: `${IMPACT_MATRIX_YML}` query for `.feature` entries with `change_type` in `{add, update}`.

## Ordering Method

Use `plan.md`, `research.md`, `boundary-map.yml`, and `discovery-sourcing.md` only to sort and group dependencies.

Do not add or remove features beyond matrix membership.

## Constraints

- keep order stable once chosen
- prefer `${TRUTH_BOUNDARY_ROOT}`-relative feature paths
- do not silently drop a matrix-listed feature
- if dependency order is ambiguous, prefer function package charter order from discovery sourcing, then lexicographic path order within each package
