"""Step: assert aggregate-level Activity — table columns or holistic JSON docstring."""

from __future__ import annotations

import json
from dataclasses import asdict

from behave import then  # type: ignore[import-not-found]

from _shared.result_guard import require_result


_ID_KEYS = {"id", "nanoid"}
_REF_KEYS = {"actorId", "firstNodeId", "next", "loopBackTarget"}


def _strip_nulls(obj: object) -> object:
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(x) for x in obj]
    return obj


def _build_ref_symbols(activity_dict: dict) -> dict[str, str]:
    refs: dict[str, str] = {}

    initial = activity_dict.get("initialNode")
    if isinstance(initial, dict) and isinstance(initial.get("id"), str):
        refs[initial["id"]] = "initial"

    for idx, final in enumerate(activity_dict.get("finalNodes", [])):
        if isinstance(final, dict) and isinstance(final.get("id"), str):
            refs[final["id"]] = f"final:{idx}"

    for actor in activity_dict.get("actors", []):
        if isinstance(actor, dict) and isinstance(actor.get("id"), str):
            refs[actor["id"]] = f"actor:{actor.get('name')}"

    for node in activity_dict.get("nodes", []):
        if isinstance(node, dict) and isinstance(node.get("id"), str):
            refs[node["id"]] = f"node:{node.get('type')}[{node.get('displayId')}]"

    return refs


def _normalize_payload(obj: object, ref_symbols: dict[str, str], parent_key: str | None = None) -> object:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            out[key] = _normalize_payload(value, ref_symbols, key)
        return out
    if isinstance(obj, list):
        return [_normalize_payload(x, ref_symbols, parent_key) for x in obj]
    if isinstance(obj, str):
        if parent_key in _ID_KEYS:
            return "<auto>"
        if parent_key in _REF_KEYS:
            return ref_symbols.get(obj, obj)
    return obj


def _bind_alias(bindings: dict[str, str], name: str, actual_id: str, path: str) -> None:
    if name in bindings:
        assert bindings[name] == actual_id, (
            f"{path}: alias {name!r} rebound inconsistently: {bindings[name]!r} vs {actual_id!r}"
        )
    else:
        bindings[name] = actual_id


def _assert_subset_with_aliases(
    expected: object,
    actual: object,
    ref_symbols: dict[str, str],
    bindings: dict[str, str],
    pending_refs: list[tuple[object, str, str]],
    path: str = "$",
    parent_key: str | None = None,
) -> None:
    """Subset match: expected 可在正式 `id` 欄位使用 `>alias`，並以 `$alias` 引用。

    `$alias` 可晚於對應的 `>alias` 出現；延後到 walk 結束後再驗證 `pending_refs`。
    """
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected object, got {type(actual).__name__}"
        for key, expected_value in expected.items():
            assert key in actual, f"{path}.{key}: missing key"
            _assert_subset_with_aliases(
                expected_value, actual[key], ref_symbols, bindings, pending_refs, f"{path}.{key}", key
            )
        return

    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {type(actual).__name__}"
        assert len(actual) >= len(expected), (
            f"{path}: actual list shorter than expected ({len(actual)} < {len(expected)})"
        )
        for idx, expected_item in enumerate(expected):
            _assert_subset_with_aliases(
                expected_item, actual[idx], ref_symbols, bindings, pending_refs, f"{path}[{idx}]", parent_key
            )
        return

    if isinstance(expected, str) and expected.startswith(">") and len(expected) > 1:
        assert parent_key in _ID_KEYS, f"{path}: `>alias` only allowed under id-like keys ({_ID_KEYS}), got key {parent_key!r}"
        assert isinstance(actual, str), f"{path}: expected str id to bind, got {type(actual).__name__}"
        _bind_alias(bindings, expected[1:], actual, path)
        return

    if isinstance(expected, str) and expected.startswith("$") and len(expected) > 1:
        name = expected[1:]
        pending_refs.append((actual, name, path))
        return

    if isinstance(expected, str) and parent_key in _REF_KEYS and isinstance(actual, str):
        sym = ref_symbols.get(actual, actual)
        assert sym == expected, f"{path}: normalized {sym!r} != expected {expected!r}"
        return

    assert actual == expected, f"{path}: {actual!r} != {expected!r}"


def _flush_pending_refs(bindings: dict[str, str], pending_refs: list[tuple[object, str, str]]) -> None:
    for actual, name, path in pending_refs:
        assert name in bindings, f"{path}: unknown alias {name!r} (not bound by `>name` / nodeId)"
        assert actual == bindings[name], f"{path}: {actual!r} != ${name} -> {bindings[name]!r}"


def _assert_subset(expected: object, actual: object, path: str = "$") -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected object, got {type(actual).__name__}"
        for key, expected_value in expected.items():
            assert key in actual, f"{path}.{key}: missing key"
            _assert_subset(expected_value, actual[key], f"{path}.{key}")
        return

    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {type(actual).__name__}"
        assert len(actual) >= len(expected), f"{path}: actual list shorter than expected ({len(actual)} < {len(expected)})"
        for idx, expected_item in enumerate(expected):
            _assert_subset(expected_item, actual[idx], f"{path}[{idx}]")
        return

    assert actual == expected, f"{path}: {actual!r} != {expected!r}"


@then("decode 成功，activity 至少包含:")
def step_assert_activity_table(context):
    require_result(context)
    result = context.parse_result
    assert result.ok is True, f"expected ok=True, got ok={result.ok} errors={result.errors}"
    activity = result.activity
    assert activity is not None, "activity missing"

    text = (getattr(context, "text", None) or "").strip()
    if text:
        expected = json.loads(text)
        actual_raw = _strip_nulls(asdict(activity))
        ref_symbols = _build_ref_symbols(actual_raw)
        expected = _strip_nulls(expected)
        bindings: dict[str, str] = {}
        pending_refs: list[tuple[object, str, str]] = []
        try:
            _assert_subset_with_aliases(expected, actual_raw, ref_symbols, bindings, pending_refs)
            _flush_pending_refs(bindings, pending_refs)
        except AssertionError as exc:
            actual_display = _normalize_payload(actual_raw, ref_symbols)
            raise AssertionError(
                str(exc)
                + "\n--- expected ---\n"
                + json.dumps(expected, ensure_ascii=False, indent=2)
                + "\n--- actual (ids as <auto>, refs symbolic) ---\n"
                + json.dumps(actual_display, ensure_ascii=False, indent=2)
            ) from exc
        return

    assert context.table is not None, "expected docstring JSON or table after decode 成功，activity 至少包含:"
    row = context.table[0]
    if "name" in row.headings:
        assert activity.name == row["name"], f"name: {activity.name!r} != {row['name']!r}"
    if "actorsCount" in row.headings:
        assert len(activity.actors) == int(row["actorsCount"]), (
            f"actorsCount: {len(activity.actors)} != {row['actorsCount']}"
        )
    if "nodesCount" in row.headings:
        assert len(activity.nodes) == int(row["nodesCount"]), (
            f"nodesCount: {len(activity.nodes)} != {row['nodesCount']}"
        )
