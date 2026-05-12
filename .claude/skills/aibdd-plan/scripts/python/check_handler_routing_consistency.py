#!/usr/bin/env python3
"""Validate aibdd-core/assets/boundaries/web-backend/handler-routing.yml structure beyond JSON Schema."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, violation

HANDLER_IDS = frozenset(
    {
        "aggregate-given",
        "http-operation",
        "success-failure",
        "readmodel-then",
        "aggregate-then",
        "time-control",
        "external-stub",
    }
)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: check_handler_routing_consistency.py <handler-routing.yml>",
            file=sys.stderr,
        )
        return 2

    path = Path(sys.argv[1]).resolve()
    data = load_yaml(path)
    violations: list[dict[str, Any]] = []

    if not isinstance(data, dict):
        violations.append(violation("ROUTING_NOT_OBJECT", str(path), "root must be a mapping"))
        return emit(False, "handler-routing consistency", violations)

    handlers = data.get("handlers")
    routes = data.get("routes")

    if not isinstance(handlers, dict):
        violations.append(violation("HANDLERS_MISSING", str(path), "handlers must be a mapping"))
    else:
        hk = set(handlers.keys())
        if hk != HANDLER_IDS:
            missing = sorted(HANDLER_IDS - hk)
            extra = sorted(hk - HANDLER_IDS)
            if missing:
                violations.append(
                    violation(
                        "HANDLERS_INCOMPLETE",
                        str(path),
                        f"handlers keys missing: {missing}",
                    )
                )
            if extra:
                violations.append(
                    violation(
                        "HANDLERS_EXTRA",
                        str(path),
                        f"handlers keys not allowed: {extra}",
                    )
                )
        for hid, block in handlers.items():
            if not isinstance(block, dict):
                violations.append(
                    violation("HANDLER_BLOCK_NOT_OBJECT", str(path), f"handlers.{hid} must be a mapping")
                )
                continue
            for req in ("required_source_kinds", "l4_requirements"):
                if req not in block:
                    violations.append(
                        violation(
                            "HANDLER_CONTRACT_INCOMPLETE",
                            str(path),
                            f"handlers.{hid} missing {req}",
                        )
                    )

    if not isinstance(routes, list):
        violations.append(violation("ROUTES_NOT_ARRAY", str(path), "routes must be a list"))
    else:
        for i, r in enumerate(routes):
            if not isinstance(r, dict):
                continue
            h = r.get("handler")
            sp = r.get("sentence_part")
            if h not in HANDLER_IDS:
                violations.append(
                    violation(
                        "ROUTE_HANDLER_UNKNOWN",
                        str(path),
                        f"routes[{i}] unknown handler {h!r}",
                    )
                )
            elif isinstance(handlers, dict) and h not in handlers:
                violations.append(
                    violation(
                        "ROUTE_HANDLER_NOT_IN_HANDLERS",
                        str(path),
                        f"routes[{i}] handler {h!r} missing from handlers map",
                    )
                )
            if sp != h:
                violations.append(
                    violation(
                        "SENTENCE_PART_HANDLER_MISMATCH",
                        str(path),
                        f"routes[{i}] sentence_part {sp!r} must equal handler {h!r}",
                    )
                )

    return emit(not violations, "handler-routing consistency", violations)


if __name__ == "__main__":
    raise SystemExit(main())
