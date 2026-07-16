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

An existing mapping may carry more than one entity row for the same table
(e.g. a view and a legacy alias). Every such row is preserved verbatim across
a rerun; only an exact duplicate row (same entity and same table) is folded,
since keeping it would make apply's global-uniqueness check flag the row as
colliding with itself.

Unsupported schema dialects: a project may carry schema files this skill
cannot parse (e.g. Cassandra CQL) whose mappings were converted by hand.
New-table discovery therefore trusts `SCHEMA_SUFFIXES` only; every other file
under `DATA_DIR` is explicitly reported as ignored instead of silently
skipped. Meanwhile every existing `entity_to_table_mapping.yml` — including
one in a folder that holds no supported schema file (a "foreign" mapping) —
still enters the global entity-name uniqueness inventory. Foreign mappings
are never rewritten.

Two entry points:
    plan  <DATA_DIR>   scan + group + diff against existing mappings; print a
                       JSON worklist (existing entries + new tables to name) to
                       stdout. Does not write any file.
    apply <DATA_DIR>   read a naming decision as JSON from stdin, merge it with
                       preserved existing entries, verify global uniqueness, and
                       write one mapping per folder.

Reuses `aibdd-core` spec_parsers (`dispatch_spec_parser`) so DBML / MySQL /
PostgreSQL / MSSQL parsing logic stays in one place.

Usage:
    python3 build_mapping.py plan <DATA_DIR>
    echo '<naming-json>' | python3 build_mapping.py apply <DATA_DIR>
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
MAPPING_FILENAME = "entity_to_table_mapping.yml"

# Exit codes
_EXIT_OK = 0
_EXIT_USAGE = 1
_EXIT_MISSING_DIR = 2
_EXIT_DUPLICATE_TABLE = 3
_EXIT_DUPLICATE_ENTITY = 4
_EXIT_BAD_NAMING = 5


def _scan_data_dir(data_dir: Path) -> tuple[list[Path], list[Path], list[Path]]:
    """Return (schema_files, ignored_files, mapping_files) under `data_dir`.

    Decision: new-table discovery trusts SCHEMA_SUFFIXES only. Any other
    non-hidden file (e.g. a Cassandra `.cql` schema this skill cannot parse)
    is collected as explicitly ignored so the plan output can surface it,
    rather than being silently dropped from the scan.
    """
    schema_files: list[Path] = []
    ignored_files: list[Path] = []
    mapping_files: list[Path] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        name = path.name.lower()
        if any(name.endswith(suffix) for suffix in SCHEMA_SUFFIXES):
            schema_files.append(path)
        elif path.name == MAPPING_FILENAME:
            mapping_files.append(path)
        else:
            ignored_files.append(path)
    return schema_files, ignored_files, mapping_files


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


def _parse_existing_mapping(path: Path) -> list[tuple[str, str]]:
    """Read an existing entity_to_table_mapping.yml into (entity, table) rows.

    Decision: return every row verbatim, in file order, duplicates included.
    A hand-maintained or previously-generated mapping may legitimately carry
    more than one entity name for the same physical table (e.g. a view and a
    legacy alias sharing one table); collapsing rows into a table-keyed dict
    would silently drop whichever entity name lost the last-write-wins race.
    Callers that need "does this table already have an entry" test table
    membership across these rows instead of keying a dict by table.
    """
    if not path.is_file():
        return []
    import yaml  # local import: only needed on the incremental path

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = loaded.get("entity_to_table_mapping") or []
    result: list[tuple[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for entity, table in row.items():
            result.append((str(entity), str(table)))
    return result


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


def _plan_folders(data_dir: Path) -> tuple[list[dict], list[dict], list[str], int, int]:
    """Build the per-folder worklist. Raises ValueError on duplicate table.

    Returns (folders, foreign_mappings, ignored_files, dbml_count, ddl_count).

    Each folder entry: {
        "folder": <relpath from data_dir, "." for root>,
        "existing": [{"entity": ..., "table": ...}, ...],  # preserved rows,
                     # ordered by schema table order then original file
                     # order; a table with more than one existing entity
                     # name keeps every row (see _parse_existing_mapping)
        "new_tables": [table, ...],          # tables with no existing entry
    }

    Each foreign mapping entry: {
        "folder": <relpath from data_dir>,
        "entities": [{"entity": ..., "table": ...}, ...],  # every row
                     # verbatim, per _parse_existing_mapping — kept as a row
                     # list rather than an entity-keyed dict so an entity
                     # name the foreign file itself duplicates (a pre-existing
                     # defect in that hand-maintained file) is not silently
                     # collapsed away before it reaches the uniqueness check.
    }
    A mapping is foreign when its folder holds no supported schema file — e.g.
    it was hand-converted from a schema dialect this skill cannot parse.
    Foreign mappings are never rewritten, but their entity names must count
    toward the global uniqueness inventory (see `_write_folders`).
    """
    schema_files, ignored_paths, mapping_files = _scan_data_dir(data_dir)
    groups = _group_by_dir(schema_files)
    # A folder emits a mapping only when it directly holds schema files. The one
    # exception is a DATA_DIR with no schema files anywhere: emit an empty root
    # mapping to preserve the "no data yet" contract — unless a root mapping
    # already exists (then it is foreign truth we must not clobber). When
    # subfolders carry the schema but the root does not, the root gets no
    # mapping.
    if not groups and not (data_dir / MAPPING_FILENAME).is_file():
        groups[data_dir] = []

    foreign: list[dict] = []
    for mapping_path in mapping_files:
        if mapping_path.parent in groups:
            continue
        existing_rows = _parse_existing_mapping(mapping_path)
        seen_rows: set[tuple[str, str]] = set()
        entities = []
        for entity, table in existing_rows:
            # Fold only an exact duplicate row, same as the managed-folder
            # path below — a genuine same-entity-different-table collision
            # inside the foreign file must survive into the inventory.
            if (entity, table) in seen_rows:
                continue
            seen_rows.add((entity, table))
            entities.append({"entity": entity, "table": table})
        foreign.append(
            {
                "folder": os.path.relpath(mapping_path.parent, data_dir),
                "entities": entities,
            }
        )

    ignored_files = [
        os.path.relpath(path, data_dir) for path in ignored_paths
    ]

    folders: list[dict] = []
    total_dbml = 0
    total_ddl = 0
    for out_dir in sorted(groups):
        folder_files = sorted(groups[out_dir])
        table_order, dbml_count, ddl_count = _scan_folder_tables(folder_files)
        total_dbml += dbml_count
        total_ddl += ddl_count

        output_path = out_dir / "entity_to_table_mapping.yml"
        existing_rows = _parse_existing_mapping(output_path)
        # Decision: group by table without collapsing it — a table may carry
        # more than one existing entity row (see _parse_existing_mapping) and
        # every one of them must survive the rerun. An exact duplicate row
        # (same entity *and* same table) is the one case we do fold, since
        # keeping it verbatim would make apply's uniqueness check flag the
        # row as colliding with itself.
        rows_by_table: dict[str, list[str]] = {}
        for entity, table in existing_rows:
            entities_for_table = rows_by_table.setdefault(table, [])
            if entity not in entities_for_table:
                entities_for_table.append(entity)
        # Keep only the rows whose table still exists in the current schema,
        # ordered by the current schema so the output stays stable.
        existing = [
            {"entity": entity, "table": table}
            for table in table_order
            for entity in rows_by_table.get(table, [])
        ]
        new_tables = [t for t in table_order if t not in rows_by_table]

        rel = os.path.relpath(out_dir, data_dir)
        folders.append(
            {
                "folder": rel,
                "existing": existing,
                "new_tables": new_tables,
            }
        )
    return folders, foreign, ignored_files, total_dbml, total_ddl


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
    existing: list[dict[str, str]] = folder["existing"]
    folder_naming = naming.get(rel, {})
    rows: list[tuple[str, str]] = [
        (row["entity"], row["table"]) for row in existing
    ]
    for table in folder["new_tables"]:
        if table not in folder_naming:
            raise KeyError(f"{rel}:{table}")
        rows.append((folder_naming[table], table))
    return rows


def _write_folders(
    data_dir: Path,
    folders: list[dict],
    foreign: list[dict],
    naming: dict[str, dict[str, str]],
) -> int:
    """Resolve rows, verify global entity uniqueness, and write per folder."""
    resolved: list[tuple[Path, list[tuple[str, str]]]] = []
    entity_owner: dict[str, str] = {}  # entity -> "folder:table" that claimed it
    # Decision: foreign mappings (hand-maintained for unsupported schema
    # dialects) seed the inventory first, so a new naming can never collide
    # with an entity name a foreign mapping already claimed. Foreign folders
    # themselves are never written.
    for foreign_mapping in foreign:
        for row in foreign_mapping["entities"]:
            entity, table = row["entity"], row["table"]
            owner = f"{foreign_mapping['folder']}:{table} (foreign mapping)"
            if entity in entity_owner:
                sys.stderr.write(
                    f"duplicate entity {entity!r}: "
                    f"{entity_owner[entity]} and {owner}\n"
                )
                return _EXIT_DUPLICATE_ENTITY
            entity_owner[entity] = owner
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
        folders, foreign, ignored_files, dbml_count, ddl_count = _plan_folders(
            data_dir
        )
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return _EXIT_DUPLICATE_TABLE
    new_count = sum(len(f["new_tables"]) for f in folders)
    existing_count = sum(len(f["existing"]) for f in folders)
    foreign_entity_count = sum(len(f["entities"]) for f in foreign)
    print(
        json.dumps(
            {
                "data_dir": str(data_dir),
                "folders": folders,
                "foreign_mappings": foreign,
                "ignored_files": ignored_files,
                "summary": {
                    "folders": len(folders),
                    "dbml": dbml_count,
                    "ddl": ddl_count,
                    "existing_entries": existing_count,
                    "new_tables": new_count,
                    "foreign_entities": foreign_entity_count,
                    "ignored_files": len(ignored_files),
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
        folders, foreign, _, _, _ = _plan_folders(data_dir)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return _EXIT_DUPLICATE_TABLE
    return _write_folders(data_dir, folders, foreign, naming)


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

    sys.stderr.write("usage: build_mapping.py plan|apply <DATA_DIR>\n")
    return _EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
