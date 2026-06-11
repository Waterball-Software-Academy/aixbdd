"""dsl_to_isa orchestrator — translation driver.

Responsibilities:
  - Collect dsl files from BOUNDARY_SHARED_DSL or TRUTH_BOUNDARY_PACKAGES_DIR.
  - Let the web_service translator prepare its context (prerequisite checks +
    loading: contracts/isa.yml + data/entity_to_table_mapping.yml).
  - Per file/step: enforce the translator's HANDLER_TABLE, delegate validation
    and translation, write skeleton params/isa_steps back to dsl.yml.
  - Idempotency: count files whose on-disk bytes match new serialization.

The translator is a single in-skill module (`web_service`). There is no
per-boundary plugin loader: a future boundary that needs different ISA
translation edits this skill, not a drop-in adapter.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dsl_to_isa import web_service as translator

# Re-exported so existing importers (test harness) keep working; the DSL flow-map
# brace fix is skill-resident in this package.
from dsl_to_isa.dsl_yaml import (  # noqa: F401
    fix_flow_map_values,
    load_dsl_yaml,
    serialize_to_bytes,
)


def _collect_dsl_files(
    contracts_path: Path,
    data_path: Path,
    boundary_shared_dsl: str | None,
    truth_packages_dir: str | None,
) -> list[Path]:
    """Collect dsl files in a stable, de-duplicated order."""
    dsl_files: list[Path] = []
    if boundary_shared_dsl:
        p = Path(boundary_shared_dsl)
        if p.is_file():
            dsl_files.append(p)
    if truth_packages_dir:
        pkgs_root = Path(truth_packages_dir)
        if pkgs_root.is_dir():
            dsl_files.extend(sorted(pkgs_root.glob("*/dsl.yml")))
    if contracts_path.is_dir():
        dsl_files.extend(sorted(contracts_path.glob("*.dsl.yml")))
    if data_path.is_dir():
        dsl_files.extend(sorted(data_path.glob("*.dsl.yml")))

    seen: set[Path] = set()
    unique: list[Path] = []
    for p in dsl_files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(p)
    return unique


def run_translate(
    contracts_dir: str,
    data_dir: str,
    boundary_shared_dsl: str | None,
    truth_packages_dir: str | None,
) -> int:
    """Main entry point called by the CLI.

    Returns exit code (0 = success, 1 = error).
    Side effects: writes to dsl.yml files, prints to stdout/stderr.
    """
    contracts_path = Path(contracts_dir)
    data_path = Path(data_dir)

    # -----------------------------------------------------------------------
    # 1. Collect dsl files — early exit if none (don't require any
    #    prerequisites when there's nothing to do).
    # -----------------------------------------------------------------------
    dsl_files = _collect_dsl_files(
        contracts_path, data_path, boundary_shared_dsl, truth_packages_dir
    )
    if not dsl_files:
        print("無 dsl.yml 待翻譯")
        return 0

    # -----------------------------------------------------------------------
    # 2. Let the translator prepare its own context. All prerequisite checks
    #    (isa.yml, entity maps, …) and their user-facing pointers live in the
    #    translator module.
    # -----------------------------------------------------------------------
    context, err = translator.prepare_context(contracts_dir, data_dir)
    if err:
        print(err, file=sys.stderr)
        return 1

    handler_table: dict = translator.HANDLER_TABLE

    # -----------------------------------------------------------------------
    # 3. Per-file translation
    # -----------------------------------------------------------------------
    first_write_count = 0
    idempotent_skip_count = 0

    for dsl_path in dsl_files:
        data = load_dsl_yaml(dsl_path)
        if not data:
            continue

        dsl_steps = data.get("dsl_steps", [])

        # Validate all steps before writing anything.
        for step in dsl_steps:
            handler = step.get("handler", "")
            step_name = step.get("name", "<unnamed>")

            # Handler-table membership is the one generic gate the orchestrator
            # keeps: the translator exposes a HANDLER_TABLE and the mechanism is
            # boundary-agnostic even though its contents are web-service-specific.
            if handler not in handler_table:
                print(
                    f"handler not in translator built-in handler table — "
                    f"step `{step_name}` uses handler `{handler}`",
                    file=sys.stderr,
                )
                return 1

            err = translator.validate_step(dict(step), context)
            if err:
                print(err, file=sys.stderr)
                return 1

        # Capture bytes before modification for idempotency check.
        original_bytes = dsl_path.read_bytes()

        for step in dsl_steps:
            params, isa_steps = translator.translate_step(dict(step), context)
            step["params"] = params
            step["isa_steps"] = isa_steps

        new_bytes = serialize_to_bytes(data)

        if new_bytes == original_bytes:
            idempotent_skip_count += 1
        else:
            dsl_path.write_bytes(new_bytes)
            first_write_count += 1

    # -----------------------------------------------------------------------
    # 4. Summary
    # -----------------------------------------------------------------------
    print(
        f"summary: first_write_count={first_write_count} "
        f"idempotent_skip_count={idempotent_skip_count}"
    )
    return 0
