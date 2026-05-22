"""Supplement DSL entries with DB-required-no-default fields SEMANTIC missed.

Runs between SEMANTIC step 4 (business focus fill) and HARNESS step 5 (eval).

Flow:
  1. parse all specs → parts_by_path keyed on target_part_path
  2. for each dsl entry:
       - handler not in {state-builder, operation-invoke} → silent skip
       - target_part_path not in parts_by_path → SkippedEntry
       - else compute missing required fields, append to datatable_bindings
  3. return SupplementReport

Append uses ruamel round-trip mode so candidate-comment blocks and existing
entry ordering survive. Only the targeted `datatable_bindings` mapping is
mutated; everything else is preserved verbatim.

Required-no-default rule per part kind:
  - DbmlTablePart: not_pk && !nullable && !has_default
  - ApiOperationPart: required && source == "body"

Field is supplemented only if absent from both param_bindings and
datatable_bindings on the entry — making the operation idempotent.
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from dsl_cli.dsl_reader import load_dsl_files
from dsl_cli.models import (
    ApiOperationPart,
    DbmlTablePart,
    DSLEntry,
    Part,
    SkippedEntry,
    SupplementedField,
    SupplementReport,
)
from dsl_cli.spec_parsers.dispatcher import dispatch_spec_parser

_SUPPLEMENTED_HANDLERS = {"state-builder", "operation-invoke"}
_PLACEHOLDER = "<FILL IN>"
_REASON_NO_PART = "target_part_path 對應不到 spec part"


def run_supplement(
    spec_paths: list[Path], dsl_paths: list[Path]
) -> SupplementReport:
    parts_by_path: dict[str, Part] = {}
    processed_specs: list[Path] = []
    for spec_path in spec_paths:
        if not spec_path.is_file():
            continue
        parser = dispatch_spec_parser(spec_path)
        for part in parser.parse(spec_path):
            parts_by_path[part.target_part_path] = part
        processed_specs.append(spec_path)

    entries_by_file = load_dsl_files(dsl_paths)
    supplemented: list[SupplementedField] = []
    skipped: list[SkippedEntry] = []
    processed_dsl_files: list[Path] = []

    for dsl_path, entries in entries_by_file.items():
        edits: dict[str, list[tuple[str, str]]] = {}
        for entry in entries:
            if entry.handler not in _SUPPLEMENTED_HANDLERS:
                continue
            part = parts_by_path.get(entry.target_part_path)
            if part is None:
                skipped.append(
                    SkippedEntry(
                        entry_name=entry.name,
                        dsl_file=dsl_path,
                        reason=_REASON_NO_PART,
                    )
                )
                continue
            missing = _compute_missing(entry, part)
            if missing:
                edits[entry.name] = missing
                for key, target in missing:
                    supplemented.append(
                        SupplementedField(
                            entry_name=entry.name,
                            dsl_file=dsl_path,
                            field_key=key,
                            target=target,
                        )
                    )
        if edits:
            _apply_edits(dsl_path, edits)
        if dsl_path.is_file():
            processed_dsl_files.append(dsl_path)

    return SupplementReport(
        supplemented_fields=supplemented,
        skipped_entries=skipped,
        processed_specs=processed_specs,
        processed_dsl_files=processed_dsl_files,
    )


def _compute_missing(entry: DSLEntry, part: Part) -> list[tuple[str, str]]:
    """Return list of (key, target) for fields to supplement on this entry.

    A spec field is considered already bound iff its `target_part_path` appears
    as the `target` of any existing param_binding or datatable_binding —
    matching by target (not by key) lets SEMANTIC use localized keys
    (e.g. `玩家暱稱` for a column named `nickname`) without breaking the
    idempotency check.
    """
    bound_targets = {b.target for b in entry.param_bindings.values()} | {
        b.target for b in entry.datatable_bindings.values()
    }
    out: list[tuple[str, str]] = []
    if isinstance(part, DbmlTablePart):
        for col in part.columns:
            if col.is_pk or col.nullable or col.has_default:
                continue
            if col.target_part_path in bound_targets:
                continue
            out.append((col.name, col.target_part_path))
    elif isinstance(part, ApiOperationPart):
        for ri in part.request_inputs:
            if not ri.required or ri.source != "body":
                continue
            if ri.target_part_path in bound_targets:
                continue
            out.append((ri.name, ri.target_part_path))
    return out


def _new_yaml() -> YAML:
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def _apply_edits(path: Path, edits: dict[str, list[tuple[str, str]]]) -> None:
    yaml = _new_yaml()
    with path.open() as fh:
        doc = yaml.load(fh)
    for raw_entry in doc.get("dsl_steps") or []:
        missing = edits.get(raw_entry.get("name"))
        if not missing:
            continue
        dt = raw_entry.get("datatable_bindings")
        if not isinstance(dt, CommentedMap):
            dt = CommentedMap()
            raw_entry["datatable_bindings"] = dt
        if len(dt) == 0:
            # Empty `{}` flow-style → switch to block style before append.
            dt.fa.set_block_style()
        for key, target in missing:
            if key in dt:
                continue
            inner = CommentedMap()
            inner["target"] = target
            inner["required"] = False
            inner["default_value"] = _PLACEHOLDER
            dt[key] = inner
    with path.open("w") as fh:
        yaml.dump(doc, fh)
