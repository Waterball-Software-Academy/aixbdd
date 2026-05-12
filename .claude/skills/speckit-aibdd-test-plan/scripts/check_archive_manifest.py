"""Check archive-manifest.yml completeness for a spec package (PF-15c).

Called by:
    .claude/skills/aibdd-core/scripts/bash/check-archive-manifest.sh         (wrapper)
    preset/commands/speckit.implement.md (Archive Gate)      (consumer)

Contract:
    CLI: check_archive_manifest.py <feature-dir>
    exit 0 → manifest covers every unarchived feature/DSL file in the spec package
    exit 1 → mismatch; stderr lists unarchived files + suggested TZ## task IDs
    exit 2 → manifest missing or malformed

What "unarchived" means:
    A source file is still present in the spec package AND is not listed in
    manifest.moves[].from. Once manifest says it's moved, we trust the manifest
    (the actual `git mv` removed the file — it's the manifest that keeps the
    pointer).
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: pyyaml required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


def main(feature_dir_arg: str) -> int:
    feature_dir = Path(feature_dir_arg).resolve()
    if not feature_dir.is_dir():
        print(f"ERROR: {feature_dir} is not a directory", file=sys.stderr)
        return 2

    manifest_path = feature_dir / "archive-manifest.yml"
    if not manifest_path.exists():
        print(
            f"FAIL: archive-manifest.yml not found at {manifest_path}.\n"
            f"      Phase Z has not been generated or executed. Run /speckit.tasks "
            f"to emit Phase Z tasks, then execute them.",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"FAIL: archive-manifest.yml is malformed YAML: {exc}", file=sys.stderr)
        return 2

    moves = manifest.get("moves") or []
    moved_sources: set[Path] = set()
    for m in moves:
        if not isinstance(m, dict) or "from" not in m:
            continue
        # Normalise to absolute path under feature_dir
        src = Path(m["from"])
        if not src.is_absolute():
            # manifest may store repo-relative path; try to resolve under feature_dir's parent chain
            abs_src = (feature_dir.parent.parent / src).resolve() if str(src).startswith("specs/") else (feature_dir / src).resolve()
        else:
            abs_src = src.resolve()
        moved_sources.add(abs_src)

    # Discover every artefact that should be archived
    candidates: list[Path] = []
    candidates.extend(sorted((feature_dir / "features").rglob("*.feature"))) if (feature_dir / "features").exists() else None
    candidates.extend(sorted((feature_dir / "test-plan").glob("*.feature"))) if (feature_dir / "test-plan").exists() else None
    dsl_local = feature_dir / "dsl.md"
    if dsl_local.exists():
        candidates.append(dsl_local)

    unarchived: list[Path] = [c for c in candidates if c.resolve() not in moved_sources]

    total = len(candidates)
    archived = total - len(unarchived)

    if unarchived:
        print(
            f"FAIL: {len(unarchived)}/{total} artefacts remain unarchived in {feature_dir.name}",
            file=sys.stderr,
        )
        print("Unarchived files (each must have its own TZ## `git mv` task):", file=sys.stderr)
        for u in unarchived[:25]:
            rel = u.relative_to(feature_dir)
            print(f"  - {rel}", file=sys.stderr)
        if len(unarchived) > 25:
            print(f"  ... and {len(unarchived) - 25} more", file=sys.stderr)
        print(
            f"\nTo fix: either (a) execute Phase Z tasks — one `git mv` per file + append "
            f"the entry to archive-manifest.yml.moves[]; OR (b) explicitly mark the task "
            f"as `[SKIP :: reason=<justification>]` in tasks.md and log in "
            f"phase-7-progress.md.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: all {archived}/{total} artefacts archived; manifest.moves[] has {len(moves)} entries.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_archive_manifest.py <feature-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
