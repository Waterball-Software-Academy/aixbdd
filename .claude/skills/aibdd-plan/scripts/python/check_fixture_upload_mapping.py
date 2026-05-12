#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import collect_yaml_files, emit, load_text, load_yaml, violation


UPLOAD_TOKENS = ("multipart", "file", "upload", "blob", "檔案", "上傳")


def entries_from(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return [x for x in data["entries"] if isinstance(x, dict)]
    return []


def contract_mentions_upload(contracts_dir: Path) -> bool:
    for path in collect_yaml_files(contracts_dir):
        text = load_text(path).lower()
        if any(token in text for token in UPLOAD_TOKENS):
            return True
    return False


def entry_has_upload_support(entry: dict[str, Any]) -> bool:
    l3 = entry.get("L3") or {}
    l4 = entry.get("L4") or {}
    if not isinstance(l4, dict):
        return False
    if isinstance(l3, dict) and l3.get("type") == "fixture-upload":
        return True
    fixture = l4.get("fixture")
    has_fixture = isinstance(fixture, dict) and fixture.get("catalog_ref") and fixture.get("missing_file_behavior")
    has_surface = l4.get("surface_kind") == "fixture-upload"
    has_response = isinstance(l4.get("assertion_bindings"), dict) and bool(l4.get("assertion_bindings"))
    return bool(has_fixture and has_surface and has_response)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: check_fixture_upload_mapping.py <contracts-dir> <local-dsl.yml> <shared-dsl.yml>", file=sys.stderr)
        return 2

    contracts_dir = Path(sys.argv[1]).resolve()
    dsl_paths = [Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()]
    violations = []

    if contract_mentions_upload(contracts_dir):
        entries = [entry for p in dsl_paths for entry in entries_from(p)]
        if not any(entry_has_upload_support(entry) for entry in entries):
            violations.append(violation("FIXTURE_UPLOAD_DSL_MISSING", ",".join(str(p) for p in dsl_paths), "upload contract exists but no DSL fixture-upload mapping found"))

    return emit(not violations, "fixture upload mapping check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
