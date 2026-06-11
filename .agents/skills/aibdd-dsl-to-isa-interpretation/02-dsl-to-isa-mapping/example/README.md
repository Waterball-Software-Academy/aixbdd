# dsl_to_isa — runnable example

Smallest end-to-end check that the translator works, independent of the behave
suite. Feeds a fake `isa.yml` + `dsl.yml` through the real CLI and prints the
ISA-augmented `dsl.yml`.

## Run

```bash
./run.sh
```

`run.sh` copies `input/` → `.work/` (gitignored), runs the translator on the
copy (it mutates `dsl.yml` in place), and prints before/after. `input/` is never
touched, so it is re-runnable.

## Inputs (`input/`)

- `contracts/isa.yml` — the ISA instruction catalog (`format` = `re` patterns).
  In a real project this is the project-authored `contracts/isa.yml`.
- `data/entity_to_table_mapping.yml` — DB table → domain entity map (used by
  `state-builder` / `state-verifier`).
- `specs/p1/dsl.yml` — DSL input with three steps exercising distinct handlers:
  `time-control`, `state-builder`, `state-verifier`.

## What you should see

Each step gains `params:` + `isa_steps:`; every other field is preserved.

| step | handler → instruction | params | table |
|------|-----------------------|--------|-------|
| `time.freeze` | time-control → `現在時間為 "{{時間}}"` | `[]` | `{}` |
| `rooms.state-builder` | state-builder → `準備一個rooms, with table:` | `{房號:, 狀態: "waiting"}` | `room_code` / `status` placeholders |
| `rooms.state-verifier` | state-verifier → `應該存在一個rooms, with table:` | `[房號]` | `room_code` placeholder |

`default_value` is carried into `params` (a bare key = required). The entity
name (`rooms`) comes from `entity_to_table_mapping.yml`.

## Manual invocation (no run.sh)

```bash
CONTRACTS_DIR=<dir with isa.yml> \
DATA_DIR=<dir with entity_to_table_mapping.yml> \
BOUNDARY_SHARED_DSL=<path to one dsl.yml> \
uv run ../scripts/cli/dsl_to_isa.py
```

Exit codes: `0` + `summary: first_write_count=… idempotent_skip_count=…` on
success; `0` + `無 dsl.yml 待翻譯` when nothing to do; non-zero + stderr pointer
when `contracts/isa.yml` is missing, a handler is unknown, or an entity is
absent from the map.

## Other handlers

`operation-invoke` / `operation-response-*` (api_call / response_validate) also
need OpenAPI contract files (parsed via the shared Spec Parser), so they are not
in this minimal demo. See the behave suite under `../scripts/tests/dsl_to_isa/`
for those.
