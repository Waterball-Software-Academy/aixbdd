# Handler: state-relationship-verifier

## Role

`state-relationship-verifier` renders persisted relationship verification — it
asserts that a row's reference column resolves to an existing referenced row
(a DBML `Ref:` / SQL `FOREIGN KEY` relationship).

The relationship is composed from one single-table `entity_validate` per
endpoint: the from-column row must exist and the to-column row must exist.
The two ends are supplied via `param_bindings` (from-column, to-column) order.
The `<entity>` word is each target's table name resolved through
`entity_to_table_mapping` (fallback: the table name itself), so it renders
identically to `state-verifier`.

It belongs to:

- `part`: `state-relationship-verifier`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the sentence verifies a relationship between two persisted
entities — that the from-side reference column maps to the to-side key.

Distinct from `state-verifier`, which verifies a single entity's own column
values. This handler is generated from a `RefPart`, and its `target_part_path`
is a relationship anchor (`<spec>#ref:<from_table>.<from_col><op><to_table>.<to_col>`).

## Context Contract

Reads `context.db_session` and `context.repos`.

The two relationship ends are supplied as `param_bindings` (the from-column and
the to-column), not `datatable_bindings`.

Writes no behavior state.

## Forbidden

- Do not call backend API.
- Do not read `context.last_response` as the assertion source.
- Do not mutate persisted state.
- Do not require `data/entity_to_table_mapping.yml`. The anchor carries the
  table/column names directly; the map is consulted only to render the `<entity>`
  word consistently with `state-verifier`, and a missing entry falls back to the
  table name (this handler is never gated on the map in `validate_step`).
- Do not infer entity fields outside data truth.
