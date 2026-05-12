#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, violation


BACKEND_SURFACE_KINDS = {
    "loader",
    "operation",
    "state-verifier",
    "response-verifier",
    "external-stub",
    "fixture-upload",
    "time-control",
}


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
    route_sentence_parts = {
        str(r.get("sentence_part"))
        for r in routes or []
        if isinstance(r, dict) and r.get("sentence_part")
    } if isinstance(routes, list) else set()
    if not handler_ids:
        violations.append(violation("ROUTING_HANDLERS_EMPTY", str(path), "handler-routing handlers map is empty or missing"))
    return handler_ids, route_sentence_parts, violations


def default_routing_path() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent.parent
    return skill_dir.parent / "aibdd-core" / "assets" / "boundaries" / "web-backend" / "handler-routing.yml"


def is_backend_entry(l3: dict[str, Any], l4: dict[str, Any]) -> bool:
    preset = l4.get("preset")
    surface_kind = str(l4.get("surface_kind", "") or "")
    l3_type = str(l3.get("type", "") or "")
    return (
        isinstance(preset, dict)
        or surface_kind in BACKEND_SURFACE_KINDS
        or l3_type in {"operation", "assertion", "external", "state", "fixture"}
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_backend_preset_refs.py [<handler-routing.yml>] <dsl.yml> [<dsl.yml>...]", file=sys.stderr)
        return 2

    violations = []
    raw_args = [Path(arg).resolve() for arg in sys.argv[1:]]
    if raw_args and raw_args[0].name == "handler-routing.yml":
        routing_path = raw_args[0]
        dsl_paths = raw_args[1:]
    else:
        routing_path = default_routing_path()
        dsl_paths = raw_args

    handler_ids, route_sentence_parts, routing_vs = load_routing(routing_path)
    violations.extend(routing_vs)

    for path in dsl_paths:
        for entry in entries_from(path):
            entry_id = str(entry.get("id", "<missing-id>"))
            l4 = entry.get("L4") or {}
            l3 = entry.get("L3") or {}
            if not isinstance(l4, dict):
                continue
            preset = l4.get("preset")
            l3_type = l3.get("type") if isinstance(l3, dict) else ""
            if not is_backend_entry(l3 if isinstance(l3, dict) else {}, l4):
                continue
            if not isinstance(preset, dict):
                violations.append(violation("BACKEND_PRESET_MISSING", str(path), f"{entry_id} backend-like entry missing L4.preset"))
                continue
            if preset.get("name") != "web-backend":
                violations.append(violation("BACKEND_PRESET_NAME_INVALID", str(path), f"{entry_id} preset.name must be web-backend"))
            if preset.get("handler") not in handler_ids:
                violations.append(violation("BACKEND_HANDLER_INVALID", str(path), f"{entry_id} invalid handler {preset.get('handler')}"))
            sp = preset.get("sentence_part")
            if sp is not None and sp != preset.get("handler"):
                violations.append(
                    violation(
                        "BACKEND_PRESET_SENTENCE_PART_HANDLER_MISMATCH",
                        str(path),
                        f"{entry_id} preset.sentence_part must equal preset.handler for web-backend",
                    )
                )
            if sp not in route_sentence_parts:
                violations.append(violation("BACKEND_SENTENCE_PART_UNROUTED", str(path), f"{entry_id} sentence_part {sp!r} not found in handler-routing routes"))
            if not preset.get("variant"):
                violations.append(violation("BACKEND_VARIANT_MISSING", str(path), f"{entry_id} missing preset.variant"))

    return emit(not violations, "backend preset reference check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
