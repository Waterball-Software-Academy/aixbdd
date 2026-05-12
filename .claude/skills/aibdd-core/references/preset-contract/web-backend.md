# web-backend

## Rules

- Physical assets for this preset live under `aibdd-core/assets/boundaries/web-backend/`.
- `handler-routing.yml` is the L4 policy SSOT for supported sentence parts, handler ids, keyword positions, and source-kind requirements.
- `/aibdd-plan` DSL synthesis MUST classify each candidate clause against `handler-routing.yml.routes` (Gherkin `keyword` + route `semantic`) before emitting `L4.preset.{sentence_part,handler}`.
- Planner MUST cite the matched route or `(sentence_part, handler)` tuple in the derivation trace; do not keep a parallel generic markdown classification SSOT.
- `handlers/*.md` documents rendering slots and narrative guidance; it does not override `handler-routing.yml`.
- `variants/*.md` defines runner/language/framework rendering contracts for a specific archetype.
- `shared-dsl-template.yml` defines canonical boundary-wide shared DSL entries.
- `L4.preset.name` MUST be `web-backend`.
- For `web-backend`, `L4.preset.sentence_part` MUST equal `L4.preset.handler`.
- Default variant is `python-e2e` unless boundary truth declares another supported variant.
- `L4.preset.variant` MUST resolve to a file under `aibdd-core/assets/boundaries/web-backend/variants/`.
- `L4.preset.handler` MUST resolve to a file under `aibdd-core/assets/boundaries/web-backend/handlers/`.
- `L4.preset.sentence_part` MUST be supported by `handler-routing.yml`.
- Handler routing MUST be resolved from `handler-routing.yml`; handler docs may clarify rendering but MUST NOT override routing.
- Supported handler ids are:
  - `aggregate-given`
  - `http-operation`
  - `success-failure`
  - `readmodel-then`
  - `aggregate-then`
  - `time-control`
  - `external-stub`
- Do not resolve `web-backend` through a `backend` alias.
- Do not synthesize handler docs from code or config key names.
- Do not let `L4.preset.handler` replace real L4 bindings, source refs, or callable mapping.
- Do not accept missing handler, missing variant, or unsupported sentence part silently.
- `check_handler_routing_consistency.py` SHOULD validate `aibdd-core/assets/boundaries/web-backend/handler-routing.yml`.
- `check_backend_preset_refs.py` SHOULD validate every DSL entry using `web-backend` against the core routing file.
- Missing `name`, `handler`, or `variant` assets MUST be fail-stop errors in `/aibdd-plan` and `/aibdd-red`.

### Preset Name Resolution Branches

- IF `L4.preset.name == web-backend`:
  - RESOLVE assets from `aibdd-core/assets/boundaries/web-backend/`.
- IF `L4.preset.name == backend`:
  - STOP with unsupported preset alias.
  - Do not map `backend` to `web-backend`.
- IF `L4.preset.name` points to any folder not present under `aibdd-core/assets/boundaries/`:
  - STOP with missing preset asset.
- IF config value `BACKEND_PRESET_CONTRACT_REF` points to this rule instance:
  - STILL read `L4.preset.name`; do not infer preset name from the config key.

### Handler Resolution Branches

- IF `L4.preset.handler` is missing:
  - STOP with missing handler.
- IF handler id is not listed in `handler-routing.yml`:
  - STOP with unsupported handler.
- IF `handlers/<handler>.md` is missing:
  - STOP with missing handler documentation.
- IF handler doc conflicts with `handler-routing.yml`:
  - TREAT `handler-routing.yml` as SSOT and report the conflict.
- IF handler id exists but required source kind is absent from the DSL entry:
  - STOP with source-kind mismatch.

### Sentence Part Resolution Branches

- IF `L4.preset.sentence_part` is missing:
  - STOP with missing sentence part.
- IF `sentence_part != handler` for `web-backend`:
  - STOP with handler mismatch.
- IF sentence part is not listed in `handler-routing.yml`:
  - STOP with unsupported sentence part.
- IF keyword position conflicts with the routing policy:
  - STOP with keyword / sentence part mismatch.

### Variant Resolution Branches

- IF `L4.preset.variant` is present:
  - RESOLVE `variants/<variant>.md`.
- IF `L4.preset.variant` is absent and boundary truth declares a supported default:
  - USE that boundary default.
- IF `L4.preset.variant` is absent and no boundary default exists:
  - USE `python-e2e`.
- IF the selected variant file is missing:
  - STOP with missing variant.
- IF the variant does not support the handler or source kind required by routing:
  - STOP with variant incompatibility.

### Binding Boundary Branches

- IF a handler provides rendering slots:
  - USE the slots to render step definitions.
- IF a handler tries to replace `L4.source_refs`, `param_bindings`, `assertion_bindings`, `datatable_bindings`, or `default_bindings`:
  - REJECT because handler docs cannot replace DSL physical truth.
- IF a handler needs extra stack instructions:
  - READ project-owned runtime refs, not this preset rule instance.

## Examples

### Good: complete preset tuple

```yaml
L4:
  source_refs:
    - contracts/crm-student-journey.openapi.yml#/paths/~1students~1{studentId}~1journey-stage/post
  param_bindings:
    student_id:
      target: data/domain.dbml#students.id
  preset:
    name: web-backend
    sentence_part: http-operation
    handler: http-operation
    variant: python-e2e
```

Why good:

- Preset name maps directly to `aibdd-core/assets/boundaries/web-backend/`.
- Sentence part and handler are aligned.
- Variant resolves to `variants/python-e2e.md`.
- Real L4 bindings remain in the DSL entry.

### Good: aggregate state setup

```yaml
L4:
  datatable_bindings:
    student_name:
      target: data/domain.dbml#students.name
  preset:
    name: web-backend
    sentence_part: aggregate-given
    handler: aggregate-given
    variant: python-e2e
```

Why good:

- `aggregate-given` is a supported routing handler.
- Business setup uses explicit datatable bindings.

### Bad: `backend` alias

```yaml
L4:
  preset:
    name: backend
    sentence_part: http-operation
    handler: http-operation
    variant: python-e2e
```

Why bad:

- `backend` is not a valid preset folder name.
- There is no alias from `backend` to `web-backend`.

Better:

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: http-operation
    handler: http-operation
    variant: python-e2e
```

### Bad: handler mismatch

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: readmodel-then
    handler: aggregate-then
    variant: python-e2e
```

Why bad:

- For `web-backend`, sentence part and handler must match.
- Response/read model verification and persisted aggregate verification use different handlers.

### Bad: missing variant

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: success-failure
    handler: success-failure
```

Why bad when no boundary default exists:

- The selected rendering contract is ambiguous.
- `/aibdd-plan` must choose an explicit supported variant or use the declared default.

Better:

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: success-failure
    handler: success-failure
    variant: python-e2e
```

### Bad: handler replaces L4 bindings

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: http-operation
    handler: http-operation
    variant: python-e2e
  handler_notes: "call POST /students/{id}/journey-stage with the stage name from the scenario"
```

Why bad:

- Handler notes are prose and cannot replace `source_refs` or parameter bindings.
- `/aibdd-red` would have to parse prose to synthesize a legal red.

Better:

```yaml
L4:
  source_refs:
    - contracts/crm-student-journey.openapi.yml#/paths/~1students~1{studentId}~1journey-stage/post
  param_bindings:
    student_id:
      target: data/domain.dbml#students.id
    stage_name:
      target: data/domain.dbml#journey_stages.name
  preset:
    name: web-backend
    sentence_part: http-operation
    handler: http-operation
    variant: python-e2e
```

### Bad: unsupported handler id

```yaml
L4:
  preset:
    name: web-backend
    sentence_part: api-call
    handler: api-call
    variant: python-e2e
```

Why bad:

- `api-call` is not listed in `handler-routing.yml`.
- Consumers must fail-stop instead of inventing a handler.
