#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from _common import emit, load_yaml, read_args, resolve_arg_path, violation


REQUIRED_SHARED_IDS = {
    "shared.success-failure.operation-success",
    "shared.success-failure.operation-failure",
    "shared.success-failure.operation-failure-reason",
    "shared.time-control.now",
}


def entries_from(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return [x for x in data["entries"] if isinstance(x, dict)]
    return []


def preset_variant(entry: dict[str, Any]) -> str:
    l4 = entry.get("L4") if isinstance(entry.get("L4"), dict) else {}
    preset = l4.get("preset") if isinstance(l4.get("preset"), dict) else {}
    return str(preset.get("variant", "") or "")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_shared_dsl_template.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    skill_dir = Path(__file__).resolve().parent.parent.parent
    template_path = skill_dir.parent / "aibdd-core" / "assets" / "boundaries" / "web-backend" / "shared-dsl-template.yml"
    shared_path = resolve_arg_path(args_path, args, "BOUNDARY_SHARED_DSL")
    variant = str(args.get("STARTER_VARIANT") or "python-e2e")

    violations = []
    template_entries = entries_from(template_path)
    shared_entries = entries_from(shared_path) if shared_path else []

    template_ids = {str(e.get("id")) for e in template_entries}
    shared_by_id = {str(e.get("id")): e for e in shared_entries}

    for rid in sorted(REQUIRED_SHARED_IDS):
        if rid not in template_ids:
            violations.append(violation("SHARED_TEMPLATE_REQUIRED_ENTRY_MISSING", str(template_path), f"template missing {rid}"))
        if rid not in shared_by_id:
            violations.append(violation("SHARED_DSL_REQUIRED_ENTRY_MISSING", str(shared_path), f"shared DSL missing {rid}"))

    for entry in template_entries:
        pv = preset_variant(entry)
        if pv and pv != "<backend-variant-id>":
            violations.append(
                violation("SHARED_TEMPLATE_VARIANT_NOT_PLACEHOLDER", str(template_path), f"{entry.get('id')} variant must be <backend-variant-id>")
            )

    for rid, entry in shared_by_id.items():
        if rid in REQUIRED_SHARED_IDS:
            pv = preset_variant(entry)
            if pv == "<backend-variant-id>":
                violations.append(violation("SHARED_DSL_VARIANT_UNRESOLVED", str(shared_path), f"{rid} still has template placeholder variant"))
            elif pv != variant:
                violations.append(violation("SHARED_DSL_VARIANT_MISMATCH", str(shared_path), f"{rid} variant {pv!r} != {variant!r}"))

    return emit(not violations, "shared DSL template check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
