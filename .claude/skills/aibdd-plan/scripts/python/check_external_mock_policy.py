#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, violation


def entries_from(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return [x for x in data["entries"] if isinstance(x, dict)]
    return []


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: check_external_mock_policy.py <boundary-map.yml> <test-strategy.yml> <local-dsl.yml> <shared-dsl.yml>", file=sys.stderr)
        return 2

    boundary_map = Path(sys.argv[1]).resolve()
    strategy_path = Path(sys.argv[2]).resolve()
    dsl_paths = [Path(sys.argv[3]).resolve(), Path(sys.argv[4]).resolve()]
    violations = []

    bm = load_yaml(boundary_map) or {}
    strategy = load_yaml(strategy_path) or {}
    edges = bm.get("dependency_edges", []) if isinstance(bm, dict) else []
    strategy_edges = strategy.get("dependency_edges", []) if isinstance(strategy, dict) else []
    strategy_ids = {str(e.get("edge_id")) for e in strategy_edges if isinstance(e, dict)}

    external_edges = []
    for edge in edges if isinstance(edges, list) else []:
        if not isinstance(edge, dict):
            continue
        if edge.get("provider_kind") == "third_party" or edge.get("mockable") is True:
            external_edges.append(edge)
            if str(edge.get("edge_id")) not in strategy_ids:
                violations.append(violation("MOCK_POLICY_EDGE_MISSING", str(strategy_path), f"missing strategy for edge {edge.get('edge_id')}"))

    dsl_entries = [entry for p in dsl_paths for entry in entries_from(p)]
    external_stub_refs = set()
    internal_mock_refs = []
    for entry in dsl_entries:
        l4 = entry.get("L4") or {}
        l3 = entry.get("L3") or {}
        if not isinstance(l4, dict):
            continue
        surface_kind = l4.get("surface_kind")
        if surface_kind == "external-stub":
            refs = l4.get("source_refs") or {}
            if isinstance(refs, dict):
                strategy_ref = refs.get("test_strategy")
                boundary_ref = refs.get("boundary")
                if strategy_ref:
                    external_stub_refs.add(str(strategy_ref).split("#")[-1])
                if boundary_ref:
                    external_stub_refs.add(str(boundary_ref).split("#")[-1])
        if l3.get("type") == "mock" and surface_kind != "external-stub":
            internal_mock_refs.append(str(entry.get("id", "<missing-id>")))

    for edge in external_edges:
        edge_id = str(edge.get("edge_id"))
        if edge_id and edge_id not in external_stub_refs:
            violations.append(violation("EXTERNAL_STUB_DSL_MISSING", ",".join(str(p) for p in dsl_paths), f"no DSL external-stub references edge {edge_id}"))

    for entry_id in internal_mock_refs:
        violations.append(violation("NO_SAME_BOUNDARY_INTERNAL_MOCK", ",".join(str(p) for p in dsl_paths), f"{entry_id} is mock but not external-stub"))

    return emit(not violations, "external mock policy check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
