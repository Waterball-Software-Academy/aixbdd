# Frontend Context Vector Contract

## §1 Purpose

A `FrontendContextVector` makes frontend examples readable and executable by preserving the userflow context that backend-style Spec-by-Example tends to hide in L4 trace.

It is not a UI design brief. It is the minimal scenario context required for a frontend BDD example to answer:

1. Where is the user now?
2. What data or mock state exists before the interaction?
3. What visible UI state/mode is active before the interaction?
4. What operation is the user performing?
5. What observable surface proves the result?

## §2 Slot Definitions

| Slot | Meaning | Requiredness |
|---|---|---|
| `route_context` | Current page URL/route/dialog container where the target operation happens | Hard-required for `ui-action`, `ui-readmodel-then`, `success-failure`, and `url-then` examples unless the operation itself is route landing |
| `actor_context` | Role/session/auth-visible context that changes available steps or expected result | v1 soft/CiC: inherited from feature tags/auth binding unless the DSL declares an explicit actor setup surface |
| `data_context` | Mock backend/store/API fixture data needed before the UI action/read model | Required when UI content, validation, or result depends on existing data |
| `ui_context` | Active UI mode not implied by route/data alone: modal open, selected tab, filter applied, selected row, wizard step, edit mode | v1 soft/CiC: emit trace/CiC when missing, but do not block unless caller later promotes it to hard |
| `viewport_time_context` | Viewport profile or browser-visible clock state | v1 soft/CiC unless rule/test strategy explicitly makes responsive/time behavior the target assertion |
| `operation_context` | Target frontend operation (usually `When` `ui-action`) | Hard-required for every renderable frontend context vector |
| `observable_result` | User-visible or test-observable result: feedback, DOM read model, URL, outgoing API call, mock store mutation | Hard-required for every renderable frontend context vector |

## §3 Handler Mapping

| Context slot | Preferred handlers |
|---|---|
| `route_context` | `route-given` |
| `actor_context` | feature tag / auth binding; no generic Given unless DSL declares an actor setup surface |
| `data_context` | `mock-state-given`, `api-stub` when behavior override is the state source |
| `ui_context` | Given-capable `ui-action`; occasionally `viewport-control` / `time-control` |
| `viewport_time_context` | `viewport-control`, `time-control` |
| `operation_context` | `ui-action`, route/navigation action where declared |
| `observable_result` | `success-failure`, `ui-readmodel-then`, `url-then`, `api-call-then`, `mock-state-then` |

## §4 Hard Gates

- A frontend `ui-action` example without `route_context` is blocked unless the action itself is the route landing operation.
- A frontend example whose Then reads UI data must have either `data_context` or a declared reason that the data is produced entirely by the target operation.
- A frontend example whose When requires modal/tab/filter/selection/wizard state should emit `ui_context` bound to existing DSL; in v1, missing UI context emits CiC but does not fail `exit_ok` unless promoted by caller.
- Every rendered context clause must trace to an existing DSL/shared DSL entry and one of its L1 patterns.
- Tier-2 handlers (`api-stub`, `url-then`, `api-call-then`, `mock-state-then`) require test-strategy enablement.
- Authentication/session is not invented as a generic Given. Use actor tags or `aibdd-core::authentication-binding.md` unless the flow itself is authentication.
- Business-readable Gherkin text must not expose fixture API, Playwright calls, CSS selectors, OpenAPI operation ids, Zod schemas, or mock implementation names.

## §5 CiC Policy

If a hard-required slot cannot bind to DSL truth, return `CiC(GAP)` and `exit_ok=false`. In v1, hard-required slots are (v1 hard-required):

- `route_context` for frontend `ui-action` / readmodel / feedback examples.
- `data_context` only when the UI/example is data-dependent.
- `observable_result` for every renderable frontend example.

`actor_context`, `ui_context`, and `viewport_time_context` are soft/CiC by default (soft / CiC).

Allowed CiC examples:

```yaml
- kind: GAP
  where: route_context
  text: ui-action requires current route, but no route-given DSL/shared entry or route source_ref is available
- kind: GAP
  where: data_context
  text: UI list read model depends on existing items, but no mock-state-given builder exists for the item schema
- kind: CON
  where: ui_context
  text: Modal-open setup would need a new Given sentence not present in plan DSL; v1 records this as soft context unless caller promotes ui_context to hard
```
