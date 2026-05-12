"""Scanner — walk spec packages, count boundary dsl.md entry reuse across packages.

MVP scaffold. Canonicalize / near-duplicate merging lives in
``docs/sub-proposals/01-dsl-promotion-detail.md``.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class Candidate:
    """A boundary dsl.md entry that appears in multiple spec packages."""

    entry_id: str
    occurrences: int
    packages: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    threshold: int
    total_entries_seen: int
    candidates: list[Candidate]


def _iter_dsl_local_files(specs_root: Path) -> Iterable[Path]:
    yield from specs_root.glob("*/dsl.md")


def _extract_entry_ids(md_path: Path) -> list[str]:
    """Extract ``id:`` values from the YAML entries of a boundary dsl.md file.

    MVP: matches lines of the form ``- id: <snake-case-id>``. A proper parser
    (YAML + canonicalize) is deferred; see ``docs/sub-proposals/01-dsl-promotion-detail.md``.
    """
    ids: list[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            ids.append(stripped.split("- id:", 1)[1].strip().strip('"'))
    return ids


def scan_specs(specs_root: Path, *, threshold: int = 20) -> ScanResult:
    """Scan ``specs/*/dsl.md`` and return candidates that meet threshold."""
    counts: dict[str, list[str]] = defaultdict(list)
    total = 0
    for md in _iter_dsl_local_files(specs_root):
        package_name = md.parent.name
        for entry_id in _extract_entry_ids(md):
            counts[entry_id].append(package_name)
            total += 1

    candidates = [
        Candidate(entry_id=eid, occurrences=len(pkgs), packages=sorted(set(pkgs)))
        for eid, pkgs in counts.items()
        if len(pkgs) >= threshold
    ]
    candidates.sort(key=lambda c: (-c.occurrences, c.entry_id))
    return ScanResult(threshold=threshold, total_entries_seen=total, candidates=candidates)


def format_report(result: ScanResult) -> str:
    lines = [
        f"# Scan report",
        f"Threshold: {result.threshold}",
        f"Total boundary dsl.md entries seen: {result.total_entries_seen}",
        f"Candidates ≥ threshold: {len(result.candidates)}",
        "",
    ]
    if not result.candidates:
        lines.append("No candidates above threshold.")
    else:
        lines.append("| entry_id | occurrences | packages |")
        lines.append("|---|---|---|")
        for c in result.candidates:
            lines.append(f"| `{c.entry_id}` | {c.occurrences} | {', '.join(c.packages)} |")
    return "\n".join(lines)
