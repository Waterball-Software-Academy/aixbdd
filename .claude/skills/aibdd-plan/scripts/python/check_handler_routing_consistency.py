#!/usr/bin/env python3
"""Validate handler-routing.yml internal consistency for any boundary preset.

This check is preset-agnostic: it does NOT presume a fixed handler set.
The preset's own SSOT (handlers map) defines the universe; routes are
validated against it. Adding a new preset (e.g., mobile-app, desktop-app)
requires no change to this script.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, violation


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

    declared_handler_ids: set[str] = set()
    if not isinstance(handlers, dict):
        violations.append(violation("HANDLERS_MISSING", str(path), "handlers must be a mapping"))
    else:
        declared_handler_ids = set(handlers.keys())
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

    referenced_handler_ids: set[str] = set()
    if not isinstance(routes, list):
        violations.append(violation("ROUTES_NOT_ARRAY", str(path), "routes must be a list"))
    else:
        for i, r in enumerate(routes):
            if not isinstance(r, dict):
                continue
            h = r.get("handler")
            sp = r.get("sentence_part")
            if isinstance(h, str):
                referenced_handler_ids.add(h)
            if isinstance(h, str) and declared_handler_ids and h not in declared_handler_ids:
                violations.append(
                    violation(
                        "ROUTE_HANDLER_UNKNOWN",
                        str(path),
                        f"routes[{i}] handler {h!r} not declared in handlers map",
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

    if declared_handler_ids:
        unreferenced = declared_handler_ids - referenced_handler_ids
        for hid in sorted(unreferenced):
            violations.append(
                violation(
                    "HANDLER_NOT_ROUTED",
                    str(path),
                    f"handlers.{hid} declared but not referenced by any route",
                )
            )

    return emit(not violations, "handler-routing consistency", violations)


if __name__ == "__main__":
    raise SystemExit(main())
