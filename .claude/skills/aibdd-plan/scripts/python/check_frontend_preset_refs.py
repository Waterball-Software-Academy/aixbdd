#!/usr/bin/env python3
"""Validate every web-frontend DSL entry against the core handler-routing.yml.

Frontend twin of `check_backend_preset_refs.py`. Mirrors the backend check shape
plus two boundary-invariant gates from `aibdd-core::preset-contract/web-frontend.md`:

  - I2 (OpenAPI schema auto-gate): `api-call-then` entries MUST NOT redeclare
    schema enforcement in `assertion_bindings`.
  - I4 (Storybook contract granularity): UI handlers (`ui-action`,
    `ui-readmodel-then`) require `L4.source_refs.component` to be a Story-export
    reference (`Foo.stories.ts::ExportName`), not a component file alone.

Out of scope for v1 (deferred):
  - Tier-2 enablement against the project's `test-strategy.yml`.
  - I1 cross-process callable_via heuristic (requires variant context).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, violation


FRONTEND_SURFACE_KINDS = {
    "route-navigator",
    "viewport-controller",
    "mock-loader",
    "clock",
    "mock-override",
    "ui-driver",
    "ui-feedback-verifier",
    "ui-state-verifier",
    "url-verifier",
    "mock-call-recorder",
    "mock-verifier",
}

# UI handlers that require Story-export-grade `source_refs.component` (I4).
UI_HANDLERS_REQUIRING_STORY = {"ui-action", "ui-readmodel-then"}

# Schema-related assertion kinds prohibited inside `api-call-then` (I2).
PROHIBITED_SCHEMA_ASSERTION_KINDS = {"schema_check", "openapi_schema", "schema_conformance"}


def entries_from(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return [x for x in data["entries"] if isinstance(x, dict)]
    return []


def load_routing(path: Path) -> tuple[set[str], set[str], list[dict[str, Any]]]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        return set(), set(), [violation("ROUTING_NOT_OBJECT", str(path), "handler-routing root must be a mapping")]
    handlers = data.get("handlers")
    routes = data.get("routes")
    violations: list[dict[str, Any]] = []
    handler_ids = set(handlers.keys()) if isinstance(handlers, dict) else set()
    route_sentence_parts = (
        {
            str(r.get("sentence_part"))
            for r in routes or []
            if isinstance(r, dict) and r.get("sentence_part")
        }
        if isinstance(routes, list)
        else set()
    )
    if not handler_ids:
        violations.append(
            violation("ROUTING_HANDLERS_EMPTY", str(path), "handler-routing handlers map is empty or missing")
        )
    return handler_ids, route_sentence_parts, violations


def default_routing_path() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent.parent
    return skill_dir.parent / "aibdd-core" / "assets" / "boundaries" / "web-frontend" / "handler-routing.yml"


def is_frontend_entry(l3: dict[str, Any], l4: dict[str, Any]) -> bool:
    """An entry is frontend-classified when either the explicit preset name is
    `web-frontend` OR `L4.surface_kind` falls in the frontend surface set."""
    preset = l4.get("preset")
    if isinstance(preset, dict) and preset.get("name") == "web-frontend":
        return True
    surface_kind = str(l4.get("surface_kind", "") or "")
    if surface_kind in FRONTEND_SURFACE_KINDS:
        return True
    return False


def check_storybook_granularity(
    entry_id: str, path: Path, l4: dict[str, Any], handler_id: str
) -> list[dict[str, Any]]:
    """I4: For UI handlers, `source_refs.component` MUST point to a Story export
    (contains '::<ExportName>'), not a component file alone."""
    if handler_id not in UI_HANDLERS_REQUIRING_STORY:
        return []
    source_refs = l4.get("source_refs")
    component = ""
    if isinstance(source_refs, dict):
        component = str(source_refs.get("component", "") or "")
    if not component:
        return [
            violation(
                "FRONTEND_STORY_REF_MISSING",
                str(path),
                f"{entry_id} ui handler {handler_id!r} requires L4.source_refs.component (Story export)",
            )
        ]
    if "::" not in component:
        return [
            violation(
                "FRONTEND_STORY_GRANULARITY_VIOLATION",
                str(path),
                (
                    f"{entry_id} ui handler {handler_id!r} L4.source_refs.component "
                    f"{component!r} must point to a Story export "
                    f"(suffix '::<ExportName>'); component file alone is not enough "
                    f"(boundary invariant I4)"
                ),
            )
        ]
    return []


def check_schema_gate_not_redeclared(
    entry_id: str, path: Path, l4: dict[str, Any], handler_id: str
) -> list[dict[str, Any]]:
    """I2: `api-call-then` MUST NOT redeclare schema enforcement; the mock layer
    auto-gates every dispatch."""
    if handler_id != "api-call-then":
        return []
    assertion_bindings = l4.get("assertion_bindings")
    if not isinstance(assertion_bindings, dict):
        return []
    out: list[dict[str, Any]] = []
    for binding_key, binding in assertion_bindings.items():
        if not isinstance(binding, dict):
            continue
        kind = str(binding.get("kind", "") or "")
        if kind in PROHIBITED_SCHEMA_ASSERTION_KINDS:
            out.append(
                violation(
                    "FRONTEND_SCHEMA_GATE_REDECLARED",
                    str(path),
                    (
                        f"{entry_id} api-call-then must not redeclare schema enforcement "
                        f"(assertion_bindings.{binding_key}.kind={kind!r}); schema conformance "
                        f"is auto-gated by the mock layer (boundary invariant I2)"
                    ),
                )
            )
    return out


def validate_entry(
    entry: dict[str, Any], path: Path, handler_ids: set[str], route_sentence_parts: set[str]
) -> list[dict[str, Any]]:
    entry_id = str(entry.get("id", "<missing-id>"))
    l4 = entry.get("L4") or {}
    l3 = entry.get("L3") or {}
    if not isinstance(l4, dict):
        return []
    if not is_frontend_entry(l3 if isinstance(l3, dict) else {}, l4):
        return []
    preset = l4.get("preset")
    if not isinstance(preset, dict):
        return [
            violation(
                "FRONTEND_PRESET_MISSING",
                str(path),
                f"{entry_id} frontend-like entry missing L4.preset",
            )
        ]
    out: list[dict[str, Any]] = []
    if preset.get("name") != "web-frontend":
        out.append(
            violation(
                "FRONTEND_PRESET_NAME_INVALID",
                str(path),
                f"{entry_id} preset.name must be web-frontend",
            )
        )
    handler_id = preset.get("handler")
    if handler_id not in handler_ids:
        out.append(
            violation(
                "FRONTEND_HANDLER_INVALID",
                str(path),
                f"{entry_id} invalid handler {handler_id!r}",
            )
        )
    sentence_part = preset.get("sentence_part")
    if sentence_part is not None and sentence_part != handler_id:
        out.append(
            violation(
                "FRONTEND_PRESET_SENTENCE_PART_HANDLER_MISMATCH",
                str(path),
                f"{entry_id} preset.sentence_part must equal preset.handler for web-frontend",
            )
        )
    if sentence_part not in route_sentence_parts:
        out.append(
            violation(
                "FRONTEND_SENTENCE_PART_UNROUTED",
                str(path),
                f"{entry_id} sentence_part {sentence_part!r} not found in handler-routing routes",
            )
        )
    if not preset.get("variant"):
        out.append(
            violation(
                "FRONTEND_VARIANT_MISSING",
                str(path),
                f"{entry_id} missing preset.variant",
            )
        )
    if isinstance(handler_id, str):
        out.extend(check_storybook_granularity(entry_id, path, l4, handler_id))
        out.extend(check_schema_gate_not_redeclared(entry_id, path, l4, handler_id))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: check_frontend_preset_refs.py [<handler-routing.yml>] <dsl.yml> [<dsl.yml>...]",
            file=sys.stderr,
        )
        return 2

    raw_args = [Path(arg).resolve() for arg in sys.argv[1:]]
    if raw_args and raw_args[0].name == "handler-routing.yml":
        routing_path = raw_args[0]
        dsl_paths = raw_args[1:]
    else:
        routing_path = default_routing_path()
        dsl_paths = raw_args

    handler_ids, route_sentence_parts, violations = load_routing(routing_path)

    for path in dsl_paths:
        for entry in entries_from(path):
            violations.extend(validate_entry(entry, path, handler_ids, route_sentence_parts))

    return emit(not violations, "frontend preset reference check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
