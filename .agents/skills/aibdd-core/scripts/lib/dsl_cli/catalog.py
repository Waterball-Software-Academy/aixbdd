"""Generic DSL corpus query — filter by handler and/or step text with stable ordering.

Read-only layer on top of `dsl_reader.load_dsl_files`. Phase-specific policies
such as handler-candidate-kinds routing stay in caller scripts (e.g. SBE analyze).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from dsl_cli.dsl_reader import load_dsl_files
from dsl_cli.models import CatalogMatch, DSLEntry

SourceScope = Literal["regular", "shared", "all"]

_FORMAT_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")


def _entry_to_match(
    entry: DSLEntry,
    source_file: str,
    source_scope: Literal["regular", "shared"],
) -> CatalogMatch:
    return CatalogMatch(
        name=entry.name,
        handler=entry.handler,
        target_part_path=entry.target_part_path,
        source_file=source_file,
        source_scope=source_scope,
        format=entry.format,
        param_bindings={
            key: {"target": binding.target}
            for key, binding in entry.param_bindings.items()
        },
        datatable_bindings={
            key: {
                "target": binding.target,
                "required": binding.required,
                **(
                    {"default_value": binding.default_value}
                    if binding.default_value is not None
                    else {}
                ),
            }
            for key, binding in entry.datatable_bindings.items()
        },
    )


def _ordered_corpus_paths(
    dsl_paths: list[Path],
    shared_dsl_path: Path | None,
    source_scope: SourceScope,
) -> list[tuple[Path, Literal["regular", "shared"]]]:
    ordered: list[tuple[Path, Literal["regular", "shared"]]] = []
    if source_scope in ("regular", "all"):
        ordered.extend((path, "regular") for path in dsl_paths)
    if source_scope in ("shared", "all") and shared_dsl_path is not None:
        ordered.append((shared_dsl_path, "shared"))
    return ordered


def step_text_matches_format(step_text: str, format_str: str) -> bool:
    """Placeholder-aware exact match: ``{key}`` slots accept any concrete value."""

    if step_text == format_str:
        return True

    pattern_parts: list[str] = []
    pos = 0
    for match in _FORMAT_PLACEHOLDER_RE.finditer(format_str):
        pattern_parts.append(re.escape(format_str[pos : match.start()]))
        pattern_parts.append("(.+?)")
        pos = match.end()
    pattern_parts.append(re.escape(format_str[pos:]))
    pattern = "^" + "".join(pattern_parts) + "$"
    return re.fullmatch(pattern, step_text) is not None


def query_catalog(
    dsl_paths: list[Path],
    *,
    handlers: list[str] | None = None,
    step_text: str | None = None,
    shared_dsl_path: Path | None = None,
    source_scope: SourceScope = "regular",
) -> list[CatalogMatch]:
    """Return catalog entries matching optional handler and/or step-text filters.

    File order follows *dsl_paths* argument order, then optional shared file when
    *source_scope* is ``all``. Within each file, order follows ``dsl_steps`` list
    order. Duplicate ``name`` values across the corpus keep only the first hit.

    When both *handlers* and *step_text* are set, filters combine with AND.
    """
    if not handlers and not step_text:
        return []

    handler_set = set(handlers) if handlers else None
    ordered_paths = _ordered_corpus_paths(dsl_paths, shared_dsl_path, source_scope)
    if not ordered_paths:
        return []

    unique_paths = [path for path, _ in ordered_paths]
    entries_by_file = load_dsl_files(unique_paths)

    seen_names: set[str] = set()
    matches: list[CatalogMatch] = []
    for path, scope in ordered_paths:
        source_file = path.as_posix()
        for entry in entries_by_file.get(path, []):
            if handler_set is not None and entry.handler not in handler_set:
                continue
            if step_text is not None and not step_text_matches_format(
                step_text, entry.format
            ):
                continue
            if entry.name in seen_names:
                continue
            seen_names.add(entry.name)
            matches.append(_entry_to_match(entry, source_file, scope))
    return matches


def query_by_handlers(
    dsl_paths: list[Path],
    handlers: list[str],
    shared_dsl_path: Path | None = None,
    source_scope: SourceScope = "regular",
) -> list[CatalogMatch]:
    """Return entries whose handler is in *handlers*, preserving scan order."""
    return query_catalog(
        dsl_paths,
        handlers=handlers,
        shared_dsl_path=shared_dsl_path,
        source_scope=source_scope,
    )
