# Web Frontend Binding Target Grammar

> **Owner**: `aibdd-core`; consumed by `/aibdd-plan` (writes targets into `dsl.yml`), `/aibdd-red-execute` (resolves targets into step code), and `prehandling-before-red-phase.md` §3.5 (validates target presence).
> **Scope**: web-frontend boundary preset only. Other boundaries declare their own grammars.

This document is the SSOT for the `target:` field syntax used inside `L4.param_bindings`, `L4.datatable_bindings`, `L4.default_bindings`, and `L4.assertion_bindings` entries for web-frontend handlers. Any target string that does not parse against this grammar MUST be rejected at plan time.

---

## §1 EBNF

```ebnf
binding_target  ::= source_ns ":" path
source_ns       ::= "story_arg" | "route" | "schema" | "test_strategy"
                  | "contract" | "calls" | "store" | "ui" | "literal"
path            ::= path_segment { "." path_segment } { selector }
path_segment    ::= identifier
selector        ::= "[" ( integer | string_literal ) "]"
identifier      ::= /[A-Za-z_][A-Za-z0-9_]*/
integer         ::= /-?[0-9]+/
string_literal  ::= "'" /[^']*/ "'" | "\"" /[^"]*/ "\""
```

JSONPath-style root sigil `$` is the implicit starting node for every namespace; explicit `$.` prefix is allowed but optional.

---

## §2 Namespaces

| `source_ns` | Resolves to | Used in | Used by handlers |
|---|---|---|---|
| `story_arg` | Storybook Story export `args.*` field | `param_bindings`, `assertion_bindings` | `ui-action`, `ui-readmodel-then`, `success-failure` |
| `route` | Route map entry under `L4.source_refs.route` | `param_bindings`, `assertion_bindings` | `route-given`, `url-then` |
| `schema` | Zod schema field under `L4.source_refs.data` | `param_bindings`, `datatable_bindings`, `default_bindings` | `mock-state-given`, `mock-state-then` |
| `test_strategy` | `test-strategy.yml` key under any §-section | `param_bindings`, `default_bindings` | `viewport-control`, `time-control`, `api-stub` |
| `contract` | OpenAPI operation field under `L4.source_refs.contract` | `assertion_bindings` | `success-failure`, `api-call-then` |
| `calls` | `RecordedCall[]` returned by `mockApi.calls(op)` | `assertion_bindings` | `api-call-then` |
| `store` | `mockApi.inspect<E>` return value | `assertion_bindings` | `mock-state-then` |
| `ui` | Rendered DOM via Story-derived locator | `assertion_bindings` | `ui-readmodel-then` |
| `literal` | Inline scalar value | any | any (constants only) |

---

## §3 Resolution rules

### story_arg

```
story_arg:args.primaryAction.label
story_arg:args.inputs[0].name
```

Resolves against the Story export named in `L4.source_refs.component`. Renderer reads the export at plan-resolve time; the resolved value is inlined into step code.

### route

```
route:pathname
route:searchParams.tab
route:hash
```

Resolves against the route map entry named in `L4.source_refs.route`. `route:pathname` returns the dynamic-segment-aware path template (e.g., `'/rooms/:roomCode'`).

### schema

```
schema:roomCode
schema:seatsTaken
schema:players[0].name
```

Resolves to a field path inside the Zod schema named in `L4.source_refs.data`. The renderer uses this path to derive both the seed argument key and TypeScript type. **Optional/nullable semantics** follow [`handlers/mock-state-given.md`](handlers/mock-state-given.md) §Zod Schema Field Requirements.

### test_strategy

```
test_strategy:viewport_profiles.mobile
test_strategy:time_control.named_instants.expiry
test_strategy:tier2_handlers.api-stub
```

Resolves against the project's `test-strategy.yml`. Schema enforced by [`test-strategy-schema.md`](test-strategy-schema.md). Missing key → renderer STOPs with `TEST_STRATEGY_KEY_MISSING`.

### contract

```
contract:requestBody.properties.roomCode
contract:responses.201.headers.Location
```

Resolves against the OpenAPI operation referenced by `L4.source_refs.contract`. Used only for shape derivation — actual schema enforcement is layer-level (boundary invariant I2).

### calls

```
calls:[0].body.roomCode
calls:[0].pathParams.roomCode
calls:where(body.action == 'join').body.roomCode
```

Resolves against `mockApi.calls(operationId)` at step-execution time. The `[N]` form selects the Nth call (0-based); the `where(<predicate>)` form selects the first call matching a shallow predicate against `body`, `pathParams`, `query`, or `headers`. Ambiguity (predicate matches multiple calls) → `AMBIGUOUS_CALL_PREDICATE`.

### store

```
store:rooms[roomCode=='R-001'].seatsTaken
store:players[id=='P-42']
```

Resolves against `mockApi.inspect<E>(where)`. Inside `[…]`, a single predicate `key=='value'` is allowed; complex queries belong in step code.

### ui

```
ui:role=button[name='Submit'].disabled
ui:label='Room Code'.value
ui:testid='room-code-display'.text
```

Resolves against the rendered DOM through a Story-derived Playwright locator. The selector after `:` MUST start with a role / label / test-id qualifier — raw CSS / nth-child / class selectors are rejected at parse time.

### literal

```
literal:'R-001'
literal:42
literal:true
```

Inline constant. Only allowed for genuinely scenario-local values (room codes generated by the scenario, dates that are decorative). For any value that has a source-of-truth elsewhere, that source MUST be used instead.

---

## §4 Validation checks (enforced by `check_frontend_preset_refs.py`)

1. **Namespace whitelist** — `source_ns` MUST be one of the 9 listed in §2.
2. **Path syntax** — `path` MUST parse against the EBNF in §1.
3. **Source-ref resolvability** — for any namespace that references a `L4.source_refs.*` key, that key MUST be non-null in the same DSL entry.
4. **Schema field existence** — `schema:` targets MUST resolve to a field that exists in the Zod schema (typechecker resolves at plan time).
5. **Story arg existence** — `story_arg:` targets MUST resolve to a defined arg path in the bound Story export.
6. **Test-strategy key existence** — `test_strategy:` targets MUST resolve to a key present in the project's `test-strategy.yml`.
7. **Selector legality** — `ui:` targets MUST start with `role=` / `label=` / `testid=` / `name=` qualifier.

Violations are HARD STOPs at plan time — fixture / step rendering does not proceed until the binding target resolves cleanly.

---

## §5 Forbidden

- CSS / nth-child selectors in `ui:` targets — only role / label / test-id / accessible-name qualifiers are legal.
- Computation in target paths (e.g., `schema:roomCode + suffix`) — bindings resolve to source values verbatim; transformations live in step body.
- Cross-namespace expressions (e.g., `calls:[0].body == schema:roomCode`) — comparisons happen in step code via `expect(...)`, not inside target paths.
- `literal:` targets for values that have an upstream truth source (OpenAPI, Zod schema, Story args, test-strategy). Use the appropriate namespace instead.
- Trailing `?.` / safe-navigation — target paths are validated for existence at plan time; nullable handling is the namespace's responsibility.
