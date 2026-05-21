"""Read `*.dsl.yml` files into `DSLEntry` dataclasses.

The reader uses a shared round-trip ruamel.yaml instance (same one writer uses)
so that comment-bearing files survive a read/write cycle without diff noise.
Read-only callers can still consume the returned `DSLEntry` list directly —
the round-trip representation is only relevant when writer.append_templates()
re-emits the file.
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

from dsl_cli.models import DatatableBinding, DSLEntry, ParamBinding

_yaml = YAML(typ="rt")
_yaml.preserve_quotes = True


def load_dsl_files(paths: list[Path]) -> dict[Path, list[DSLEntry]]:
    """Load each path's YAML doc into DSLEntry dataclasses.

    Top-level shape is `dsl_steps: <list>`. Paths that don't exist, contain an
    empty document, or set `dsl_steps: []` yield an empty entry list — that
    matches the harness's append-only flow where the dsl.yml may not yet exist
    before the first generate pass.
    """

    result: dict[Path, list[DSLEntry]] = {}
    for path in paths:
        result[path] = _load_one(path)
    return result


def _load_one(path: Path) -> list[DSLEntry]:
    if not path.is_file():
        return []
    with path.open() as fh:
        doc = _yaml.load(fh)
    if doc is None:
        return []
    return [_hydrate_entry(raw) for raw in (doc.get("dsl_steps") or [])]


def _hydrate_entry(raw: dict) -> DSLEntry:
    return DSLEntry(
        handler=str(raw["handler"]),
        name=str(raw["name"]),
        target_part_path=str(raw["target_part_path"]),
        format=str(raw["format"]),
        param_bindings={
            key: ParamBinding(target=str(value["target"]))
            for key, value in (raw.get("param_bindings") or {}).items()
        },
        datatable_bindings={
            key: DatatableBinding(
                target=str(value["target"]),
                required=bool(value.get("required", False)),
                default_value=(
                    str(value["default_value"]) if "default_value" in value else None
                ),
            )
            for key, value in (raw.get("datatable_bindings") or {}).items()
        },
    )


def index_resolved_parts(entries_by_file: dict[Path, list[DSLEntry]]) -> set[str]:
    return {
        entry.target_part_path
        for entries in entries_by_file.values()
        for entry in entries
    }
