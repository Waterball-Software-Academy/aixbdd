#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path


CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_.-]*)\b")
EDGE_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*([.<>|*o\-]+)\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*(?::.*)?$"
)


def normalize_dependency(left: str, op: str, right: str) -> tuple[str, str]:
    compact = op.replace(".", "-")
    if "<" in compact and ">" not in compact:
        return right, left
    if compact.startswith("<|") or compact.startswith("<"):
        return right, left
    return left, right


def topological_waves(nodes: set[str], dependency_pairs: list[tuple[str, str]]) -> list[list[str]]:
    build_graph: dict[str, set[str]] = {node: set() for node in nodes}
    indegree: dict[str, int] = {node: 0 for node in nodes}

    for consumer, provider in dependency_pairs:
        if consumer == provider:
            continue
        if consumer not in build_graph[provider]:
            build_graph[provider].add(consumer)
            indegree[consumer] += 1

    queue = sorted([node for node, deg in indegree.items() if deg == 0])
    waves: list[list[str]] = []
    remaining = dict(indegree)
    ready = deque(queue)
    visited = 0

    while ready:
        current_wave = sorted(list(ready))
        waves.append(current_wave)
        next_ready: list[str] = []
        ready.clear()
        for node in current_wave:
            visited += 1
            for nxt in sorted(build_graph[node]):
                remaining[nxt] -= 1
                if remaining[nxt] == 0:
                    next_ready.append(nxt)
        for item in sorted(set(next_ready)):
            ready.append(item)

    if visited != len(nodes):
        raise ValueError("cycle_detected")
    return waves


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: parse_internal_structure_topo.py <internal-structure.class.mmd>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        print(json.dumps({"ok": False, "reason": f"file not found: {path}"}, ensure_ascii=False, indent=2))
        return 1

    text = path.read_text(encoding="utf-8")
    nodes: set[str] = set()
    dependency_pairs: list[tuple[str, str]] = []

    for raw in text.splitlines():
        class_match = CLASS_RE.match(raw)
        if class_match:
            nodes.add(class_match.group(1))
            continue
        edge_match = EDGE_RE.match(raw)
        if edge_match:
            left, op, right = edge_match.groups()
            nodes.add(left)
            nodes.add(right)
            dependency_pairs.append(normalize_dependency(left, op, right))

    if not nodes:
        print(json.dumps({"ok": False, "reason": "no_classes_detected"}, ensure_ascii=False, indent=2))
        return 1

    try:
        waves = topological_waves(nodes, dependency_pairs)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    payload = {
        "ok": True,
        "parser_status": "parsed",
        "class_graph": {
            "classes": sorted(nodes),
            "dependency_pairs": [
                {"consumer": consumer, "provider": provider}
                for consumer, provider in sorted(dependency_pairs)
            ],
        },
        "plan_level_waves": [
            {"wave_index": idx, "classes": wave}
            for idx, wave in enumerate(waves, start=1)
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
