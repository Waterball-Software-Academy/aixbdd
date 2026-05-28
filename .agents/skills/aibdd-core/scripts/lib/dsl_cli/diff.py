"""Compute the set of unresolved parts given known resolved target paths.

`compute_unresolved(parts, resolved_targets)` is the core diff step run before
the preset plugin's generate_templates. The resolution rule is:

    A part is RESOLVED iff there exists at least one entry whose
    `target_part_path` equals OR is a descendant of `part.target_part_path`.

The "descendant" check is segment-aware, not raw string-prefix, so paths like
`/post` cannot falsely resolve `/posts/...`:

    1. Split on the first `#` into (spec_file, anchor). Spec files must match
       exactly; differing spec files never resolve each other.
    2. For JSON Pointer anchors (those starting with `/`), split on `/` and
       check list-prefix on the segment lists.
    3. For DBML relationship anchors (`ref:<from>.<col><op><to>.<col>`), only
       exact equality resolves the part; there is no descendant notion.
    4. For DBML-style dot-separated anchors (`<table>` or `<table>.<column>`),
       a child anchor must start with `<part_anchor> + '.'` to count.
    5. The empty-anchor case (rare) treats any non-empty anchor on the same
       spec_file as a descendant.
"""

from __future__ import annotations

from collections.abc import Iterable

from dsl_cli.models import Part


def compute_unresolved(
    parts: Iterable[Part], resolved_targets: Iterable[str]
) -> list[Part]:
    resolved = list(resolved_targets)
    return [p for p in parts if not _is_resolved_by_any(p.target_part_path, resolved)]


def _is_resolved_by_any(part_path: str, resolved: list[str]) -> bool:
    return any(_is_descendant_or_equal(entry, part_path) for entry in resolved)


def _is_descendant_or_equal(entry_path: str, part_path: str) -> bool:
    """True if `entry_path` equals or is a descendant of `part_path`."""

    entry_spec, _, entry_anchor = entry_path.partition("#")
    part_spec, _, part_anchor = part_path.partition("#")
    if entry_spec != part_spec:
        return False
    if entry_anchor == part_anchor:
        return True
    if part_anchor.startswith("/"):
        # JSON Pointer — segment-list prefix check on `/`-split.
        part_segments = part_anchor.split("/")
        entry_segments = entry_anchor.split("/")
        return (
            len(entry_segments) > len(part_segments)
            and entry_segments[: len(part_segments)] == part_segments
        )
    if part_anchor.startswith("ref:"):
        return False
    # DBML-style dotted anchor.
    if part_anchor == "":
        return entry_anchor != ""
    return entry_anchor.startswith(part_anchor + ".")
