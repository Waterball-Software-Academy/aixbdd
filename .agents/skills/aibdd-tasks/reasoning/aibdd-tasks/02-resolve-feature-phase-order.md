# 02 — Resolve Feature Phase Order

## Goal

Produce the ordered feature list that becomes the middle phases of `tasks.md`.

## Primary Input

Start from matrix-derived membership: every `.feature` spec present in `${IMPACT_MATRIX_YML}`, obtained via `read --spec-path '\.feature$'` and collecting the returned `impacts[].specs[].path`.

## Ordering Method

Use `plan.md`, `research.md`, `boundary-map.yml`, and `function-packaging.md` only to sort and group dependencies.

Do not add or remove features beyond matrix membership.

## Constraints

- keep order stable once chosen
- prefer `${TRUTH_BOUNDARY_ROOT}`-relative feature paths
- do not silently drop a matrix-listed feature
- if dependency order is ambiguous, prefer the function package order as listed in `function-packaging.md` (`## packages/NN-<slug>` section order), then lexicographic path order within each package
