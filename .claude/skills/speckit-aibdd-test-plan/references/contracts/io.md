# speckit-aibdd-test-plan — I/O Contract

## Config (read from caller `arguments.yml`)

| Key | Default | Description |
|---|---|---|
| `SPECS_ROOT_DIR` | (required) | Current feature package root, e.g. `specs/###-feature/` |
| `ACTIVITIES_DIR` | `${SPECS_ROOT_DIR}/activities/` | Input Activity files (**`.activity`**, flat event-flow format) |
| `FEATURES_DIR` | `${SPECS_ROOT_DIR}/features/` | Input full Feature files (Phase 3) — reference only for cross-check |
| `DSL_CORE_PATH` | `.specify/memory/dsl.md` | Project-wide shared DSL（檔名 `dsl.md`） |
| `DSL_LOCAL_PATH` | `${SPECS_ROOT_DIR}/dsl.md` | Per-spec boundary DSL（檔名 `dsl.md`） |
| `CONTRACTS_DIR` | `${SPECS_ROOT_DIR}/contracts/` | SpecKit Phase 4 contracts |
| `BDD_PLAN_PATH` | `${SPECS_ROOT_DIR}/bdd-plan.md` | Phase 3 BDD reference |
| `BDD_CONSTITUTION_PATH` | `${BDD_CONSTITUTION_PATH}` | Project-scope BDD rules |
| `TEST_PLAN_OUT_DIR` | `${SPECS_ROOT_DIR}/test-plan/` | Output dir |
| `PATH_COVERAGE_POLICY` | `node-once` | Policy 1 (every Action Node at least once) |
| `PARSER_MODE` | `mermaid-flowchart-flat` | Activity DSL dialect |

## Inputs read during SOP

- `ACTIVITIES_DIR/*.activity` (canonical) / `ACTIVITIES_DIR/*.mmd` (legacy) — via Python activity-parser
- `DSL_CORE_PATH` + `DSL_LOCAL_PATH` — merged view
- `CONTRACTS_DIR/**/*.{yml,yaml,json}` — referenced from DSL entry L4 only
- `BDD_PLAN_PATH` — user-story mapping (informational)
- `test-plan-rules.md` (plugin repo root) — the R1–R12 normative spec

## Outputs written during SOP

- `TEST_PLAN_OUT_DIR/<activity-slug>.feature` per Activity
- `${SPECS_ROOT_DIR}/clarifications/<timestamp>.md` (if Step 4 runs)
- REPORT text back to caller

## Hard boundaries

- **Never** write to `${FEATURES_DIR}` (that belongs to Phase 3 BDD Analyze)
- **Never** mutate `DSL_CORE_PATH` (that belongs to `/speckit.aibdd.promote-dsl`)
- **Never** call AI semantic reasoning to pick paths — that is the parser's job
- **Never** surface channel names / endpoints / payload in Scenario text (R6, R9)
