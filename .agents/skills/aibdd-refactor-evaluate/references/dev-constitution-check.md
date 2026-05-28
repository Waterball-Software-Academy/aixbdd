# Dev Constitution Check

Refactor evaluation treats `${DEV_CONSTITUTION_PATH}` as a strict contract.

## Rule Sources

The evaluator reads the resolved `${DEV_CONSTITUTION_PATH}` supplied by the
Worker artifact pointers. It must not guess the path.

## Mandatory Rule Classes

The evaluator extracts clauses that are expressed as:

- `MUST`, `MUST NOT`, `REQUIRED`, `FORBIDDEN`, or equivalent mandatory wording
- directory ownership rules
- boundary and layering rules
- protected surface rules
- rules that prohibit changes to API contracts, schemas, runtime references,
  testability anchors, or infrastructure contracts

## Strict Standard

A rule violates when the post-Refactor product codebase or changed-file scope
contradicts the constitution. A violation is always a Veto; it is not advisory.

## Evidence Standard

Each finding should cite:

- the constitution clause or heading
- the affected code path
- a short reason why the product code contradicts the clause

The evaluator does not replay move history. It judges the final state.
