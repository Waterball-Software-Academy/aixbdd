#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "prance",
#   "pyyaml",
#   "ruamel.yaml",
# ]
# ///
"""Build `entity_to_table_mapping.yml` from DBML / SQL DDL schema files.

Incremental, spec-driven naming: entity names are no longer forced to equal the
table name. Existing `entity_to_table_mapping.yml` entries are preserved as the
source of truth; only tables not yet mapped are treated as new and named by the
caller (the agent, from the plan package spec.md). See SKILL.md.

Per-folder generation: every directory under `DATA_DIR` (including `DATA_DIR`
itself) that directly contains one or more schema files gets its own
`entity_to_table_mapping.yml`, scoped to that folder's direct schema files.
This lets a `DATA_DIR` split across sub-boundary folders (e.g. `primary/`,
`secondary/`) carry one mapping per folder, while the outer `DATA_DIR` carries
its own for any schema files sitting directly in it. The root mapping is always
written (empty list when the root holds no direct schema files).

Duplicate table names are rejected within a single output folder; the same
table name may appear in different folders. Entity names, however, must be
globally unique across every folder's mapping.

Three entry points:
    plan  <DATA_DIR>   scan + group + diff against existing mappings; print a
                       JSON worklist (existing entries + new tables to name) to
                       stdout. Does not write any file.
    apply <DATA_DIR>   read a naming decision as JSON from stdin, merge it with
                       preserved existing entries, verify global uniqueness, and
                       write one mapping per folder.
    <DATA_DIR>         legacy one-shot: plan, name every new table with identity
                       (entity == table), then apply. Preserves existing
                       non-identity entries. Kept so identity-only callers and
                       the per-folder tests keep working without an agent.

Reuses `aibdd-core` spec_parsers (`dispatch_spec_parser`) so DBML / MySQL /
PostgreSQL / MSSQL parsing logic stays in one place.

Usage:
    python3 build_mapping.py <DATA_DIR>
    python3 build_mapping.py plan <DATA_DIR>
    echo '<naming-json>' | python3 build_mapping.py apply <DATA_DIR>
    DATA_DIR=specs/shared python3 build_mapping.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
# parents[0]=scripts, [1]=aibdd-table-to-entity, [2]=skills root
_AIBDD_CORE_LIB = (
    _THIS_FILE.parents[2] / "aibdd-core" / "scripts" / "lib"
)
if str(_AIBDD_CORE_LIB) not in sys.path:
    sys.path.insert(0, str(_AIBDD_CORE_LIB))

from shared.spec_parsers.dispatcher import dispatch_spec_parser  # noqa: E402
from shared.spec_parts import PartKind  # noqa: E402

SCHEMA_SUFFIXES = (".dbml", ".mysql.sql", ".pg.sql", ".mssql.sql")

# Exit codes
_EXIT_OK = 0
_EXIT_USAGE = 1
_EXIT_MISSING_DIR = 2
_EXIT_DUPLICATE_TABLE = 3
_EXIT_DUPLICATE_ENTITY = 4
_EXIT_BAD_NAMING = 5


def _scan_schema_files(data_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in data_dir.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if any(name.endswith(suffix) for suffix in SCHEMA_SUFFIXES):
            files.append(path)
    return sorted(files)


def _extract_tables(path: Path) -> list[str]:
    parser = dispatch_spec_parser(path)
    return [
        part.table_name
        for part in parser.parse(path)
        if part.kind == PartKind.table
    ]


def _group_by_dir(files: list[Path]) -> dict[Path, list[Path]]:
    groups: dict[Path, list[Path]] = {}
    for path in files:
        groups.setdefault(path.parent, []).append(path)
    return groups


def _parse_existing_mapping(path: Path) -> dict[str, str]:
    """Read an existing entity_to_table_mapping.yml into a table -> entity dict.

    The on-disk shape is a list of single-key maps `- <entity>: <table>`. We key
    by table (the stable identity of a row) so a later rerun can preserve the
    entity name a human already chose for that table.
    """
    if not path.is_file():
        return {}
    import yaml  # local import: only needed on the incremental path

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = loaded.get("entity_to_table_mapping") or []
    table_to_entity: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        for entity, table in row.items():
            table_to_entity[str(table)] = str(entity)
    return table_to_entity


def _scan_folder_tables(folder_files: list[Path]) -> tuple[list[str], int, int]:
    """Return (ordered table names, dbml_count, ddl_count) for one folder.

    Raises ValueError on a duplicate table within the folder.
    """
    table_seen: dict[str, Path] = {}
    table_order: list[str] = []
    dbml_count = 0
    ddl_count = 0
    for schema_file in folder_files:
        if schema_file.name.lower().endswith(".dbml"):
            dbml_count += 1
        else:
            ddl_count += 1
        for table_name in _extract_tables(schema_file):
            if table_name in table_seen:
                raise ValueError(
                    f"duplicate table {table_name!r}: "
                    f"{table_seen[table_name]} and {schema_file}"
                )
            table_seen[table_name] = schema_file
            table_order.append(table_name)
    return table_order, dbml_count, ddl_count


def _plan_folders(data_dir: Path) -> tuple[list[dict], int, int]:
    """Build the per-folder worklist. Raises ValueError on duplicate table.

    Each folder entry: {
        "folder": <relpath from data_dir, "." for root>,
        "existing": {table: entity, ...},   # preserved, in schema order
        "new_tables": [table, ...],          # tables with no existing entry
    }
    """
    schema_files = _scan_schema_files(data_dir)
    groups = _group_by_dir(schema_files)
    # A folder emits a mapping only when it directly holds schema files. The one
    # exception is a DATA_DIR with no schema files anywhere: emit an empty root
    # mapping to preserve the "no data yet" contract. When subfolders carry the
    # schema but the root does not, the root gets no mapping.
    if not groups:
        groups[data_dir] = []

    folders: list[dict] = []
    total_dbml = 0
    total_ddl = 0
    for out_dir in sorted(groups):
        folder_files = sorted(groups[out_dir])
        table_order, dbml_count, ddl_count = _scan_folder_tables(folder_files)
        total_dbml += dbml_count
        total_ddl += ddl_count

        output_path = out_dir / "entity_to_table_mapping.yml"
        existing_all = _parse_existing_mapping(output_path)
        # Keep only the entries whose table still exists in the current schema,
        # ordered by the current schema so the output stays stable.
        existing = {
            table: existing_all[table]
            for table in table_order
            if table in existing_all
        }
        new_tables = [t for t in table_order if t not in existing_all]

        rel = os.path.relpath(out_dir, data_dir)
        folders.append(
            {
                "folder": rel,
                "existing": existing,
                "new_tables": new_tables,
            }
        )
    return folders, total_dbml, total_ddl


def _format_yaml(rows: list[tuple[str, str]]) -> str:
    """Render rows of (entity, table) into the mapping YAML."""
    header = "# DO NOT EDIT — generated by aibdd-table-to-entity\n"
    if not rows:
        return header + "entity_to_table_mapping: []\n"
    lines = ["entity_to_table_mapping:"]
    lines.extend(f"  - {entity}: {table}" for entity, table in rows)
    return header + "\n".join(lines) + "\n"


def _resolve_folder_rows(
    data_dir: Path,
    folder: dict,
    naming: dict[str, dict[str, str]],
) -> list[tuple[str, str]]:
    """Merge preserved existing entries with the caller's naming for new tables.

    Row order follows the current schema scan order (existing + new interleaved
    by their table order), so the output is stable across reruns.
    """
    rel = folder["folder"]
    existing: dict[str, str] = folder["existing"]
    folder_naming = naming.get(rel, {})
    rows: list[tuple[str, str]] = []
    for table in existing:
        rows.append((existing[table], table))
    for table in folder["new_tables"]:
        if table not in folder_naming:
            raise KeyError(f"{rel}:{table}")
        rows.append((folder_naming[table], table))
    return rows


def _identity_naming(folders: list[dict]) -> dict[str, dict[str, str]]:
    """Name every new table with identity (entity == table)."""
    return {
        folder["folder"]: {table: table for table in folder["new_tables"]}
        for folder in folders
    }


def _write_folders(
    data_dir: Path,
    folders: list[dict],
    naming: dict[str, dict[str, str]],
) -> int:
    """Resolve rows, verify global entity uniqueness, and write per folder."""
    resolved: list[tuple[Path, list[tuple[str, str]]]] = []
    entity_owner: dict[str, str] = {}  # entity -> "folder:table" that claimed it
    for folder in folders:
        try:
            rows = _resolve_folder_rows(data_dir, folder, naming)
        except KeyError as exc:
            sys.stderr.write(f"missing naming for new table {exc}\n")
            return _EXIT_BAD_NAMING
        for entity, table in rows:
            owner = f"{folder['folder']}:{table}"
            if entity in entity_owner:
                sys.stderr.write(
                    f"duplicate entity {entity!r}: "
                    f"{entity_owner[entity]} and {owner}\n"
                )
                return _EXIT_DUPLICATE_ENTITY
            entity_owner[entity] = owner
        out_dir = data_dir if folder["folder"] == "." else data_dir / folder["folder"]
        resolved.append((out_dir / "entity_to_table_mapping.yml", rows))

    total = 0
    for output_path, rows in resolved:
        new_content = _format_yaml(rows)
        if output_path.is_file() and output_path.read_bytes() == new_content.encode():
            action = "unchanged"
        else:
            output_path.write_text(new_content)
            action = "wrote"
        total += len(rows)
        print(f"{action}: {output_path.resolve()} ({len(rows)} entries)")
    print(f"{len(resolved)} folder(s); {total} entry(ies) total")
    return _EXIT_OK


def _require_dir(data_dir: Path) -> int | None:
    if not data_dir.is_dir():
        sys.stderr.write(
            f"DATA_DIR not found: {data_dir} — run /aibdd-kickoff to create it\n"
        )
        return _EXIT_MISSING_DIR
    return None


def cmd_plan(data_dir: Path) -> int:
    miss = _require_dir(data_dir)
    if miss is not None:
        return miss
    try:
        folders, dbml_count, ddl_count = _plan_folders(data_dir)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return _EXIT_DUPLICATE_TABLE
    new_count = sum(len(f["new_tables"]) for f in folders)
    existing_count = sum(len(f["existing"]) for f in folders)
    print(
        json.dumps(
            {
                "data_dir": str(data_dir),
                "folders": folders,
                "summary": {
                    "folders": len(folders),
                    "dbml": dbml_count,
                    "ddl": ddl_count,
                    "existing_entries": existing_count,
                    "new_tables": new_count,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return _EXIT_OK


def cmd_apply(data_dir: Path, naming_json: str) -> int:
    miss = _require_dir(data_dir)
    if miss is not None:
        return miss
    try:
        naming = json.loads(naming_json) if naming_json.strip() else {}
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"invalid naming JSON on stdin: {exc}\n")
        return _EXIT_BAD_NAMING
    if not isinstance(naming, dict):
        sys.stderr.write("naming JSON must be an object of {folder: {table: entity}}\n")
        return _EXIT_BAD_NAMING
    try:
        folders, _, _ = _plan_folders(data_dir)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return _EXIT_DUPLICATE_TABLE
    return _write_folders(data_dir, folders, naming)


def cmd_legacy(data_dir: Path) -> int:
    miss = _require_dir(data_dir)
    if miss is not None:
        return miss
    try:
        folders, _, _ = _plan_folders(data_dir)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return _EXIT_DUPLICATE_TABLE
    return _write_folders(data_dir, folders, _identity_naming(folders))


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] == "plan":
        if len(args) < 2:
            sys.stderr.write("usage: build_mapping.py plan <DATA_DIR>\n")
            return _EXIT_USAGE
        return cmd_plan(Path(args[1]))
    if args and args[0] == "apply":
        if len(args) < 2:
            sys.stderr.write(
                "usage: echo '<json>' | build_mapping.py apply <DATA_DIR>\n"
            )
            return _EXIT_USAGE
        return cmd_apply(Path(args[1]), sys.stdin.read())

    if args:
        data_dir = Path(args[0])
    elif "DATA_DIR" in os.environ:
        data_dir = Path(os.environ["DATA_DIR"])
    else:
        sys.stderr.write(
            "usage: build_mapping.py [plan|apply] <DATA_DIR>  (or set DATA_DIR env)\n"
        )
        return _EXIT_USAGE
    return cmd_legacy(data_dir)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
