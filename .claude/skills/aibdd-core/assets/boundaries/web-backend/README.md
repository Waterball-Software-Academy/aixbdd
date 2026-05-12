# Web Backend Boundary Preset

Canonical boundary-wise preset assets for the backend HTTP E2E surface live in this directory.

This directory is the SSOT for `L4.preset.name: web-backend`. It defines handler routing, handler narrative docs, shared DSL template entries, and stack-specific variant rendering contracts. It is framework-shipped preset source under `aibdd-core`; it is not generated boundary truth under `${TRUTH_BOUNDARY_ROOT}`.

Machine checks should validate `aibdd-core/assets/boundaries/web-backend/handler-routing.yml`.

## Ownership

- Owner: `aibdd-core`
- Consumers: `/aibdd-plan`, `/aibdd-red`

## Layout

| Path | Role |
|------|------|
| `handler-routing.yml` | SSOT: `routes` (`sentence_part` + `keyword` + `handler`) and `handlers` (`required_source_kinds`, `optional_source_kinds`, `l4_requirements`) |
| `handlers/*.md` | Handler narrative and rendering guidance; does not override `handler-routing.yml` |
| `variants/*.md` | Stack-specific rendering contracts such as `python-e2e` |
| `shared-dsl-template.yml` | Boundary-wide canonical shared DSL entries |

## Forbidden Content

- No Gherkin scenario text
- No Examples table
- No feature file path
- No atomic rule instance
- No concrete operation id
- No concrete contract anchor
- No concrete DB entity instance
- No generated `dsl.yml` entry

Concrete operation, data, and contract references belong to `dsl.yml` entries under `L4.source_refs`. This preset only tells consumers how to classify backend sentence parts and render a matched `L4.preset` tuple.
