# 01 — Semantic Planning When Parse Fails

## Goal

Recover a usable implementation-wave approximation when `internal-structure.class.mmd` cannot be parsed mechanically.

## Inputs

- `plan.md`
- `research.md`
- `boundary-map.yml`
- feature files

## Method

1. Extract implementation nouns from `plan.md` and `research.md`:
   - routers / handlers
   - services / domain logic
   - repositories / persistence
   - shared DTO / response builders
2. Use `boundary-map.yml` topology when available as a secondary structural hint.
3. Group responsibilities into coarse implementation waves:
   - persistence / shared state first
   - service / domain rules next
   - router / integration exposure later
4. Prefer approximate but meaningful waves over fake precision.

## Output

- fallback wave hints
- parser failure explanation to be surfaced in the final report
