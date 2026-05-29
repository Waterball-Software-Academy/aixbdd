#!/usr/bin/env python3
"""Static consistency analyzer for generic skill families."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "site-packages",
    "dist-info",
    ".tox",
    ".eggs",
}

TEXT_EXTS = {".md", ".txt", ".yml", ".yaml", ".json", ".py", ".sh", ".js", ".ts"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REF_PATH_RE = re.compile(r"^\s*-\s+path:\s*(.+?)\s*$|^\s*path:\s*(.+?)\s*$")
SLASH_SKILL_RE = re.compile(r"(?<![\w/$}])/`?(?P<name>[a-z][a-z0-9]*(?:-[a-z0-9]+)+)`?")
ESCALATION_LINE_RE = re.compile(r"\b(STOP|DELEGATE|TRIGGER|dispatch|escalat|handoff)\b|回 `/", re.I)

# Per-skill convention basenames mandated by programlike-skill-creator. Multiple
# skills legitimately ship same-named files (each scoped to its own skill's
# role/forbidden-mutations). Demote duplicate_ssot to INFO for these.
PER_SKILL_CONVENTION_BASENAMES = {
    "role-and-contract.md",
    "forbidden-mutations.md",
    "path-contract.md",
    "quality-gate-contract.md",
}


@dataclass(frozen=True)
class Skill:
    name: str
    path: str
    skill_md: str


@dataclass(frozen=True)
class Finding:
    severity: str
    problem: str
    file: str
    target: str
    message: str
    evidence: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="Skill directory or parent containing skill directories")
    parser.add_argument("--json-out", help="Write JSON report to this path")
    parser.add_argument("--md-out", help="Write Markdown report to this path")
    parser.add_argument("--include-tests", action="store_true", help="Scan .tests directories")
    return parser.parse_args()


def should_skip(path: Path, include_tests: bool) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_DIRS:
        return True
    if not include_tests and ".tests" in parts:
        return True
    return False


def discover_skills(roots: Iterable[Path], include_tests: bool) -> list[Skill]:
    skills: list[Skill] = []
    seen: set[Path] = set()
    for root in roots:
        root = root.resolve()
        candidates = [root / "SKILL.md"] if (root / "SKILL.md").exists() else root.rglob("SKILL.md")
        for skill_md in candidates:
            if should_skip(skill_md, include_tests):
                continue
            skill_dir = skill_md.parent.resolve()
            if skill_dir in seen:
                continue
            seen.add(skill_dir)
            name = parse_frontmatter_name(skill_md) or skill_dir.name
            skills.append(Skill(name=name, path=str(skill_dir), skill_md=str(skill_md.resolve())))
    return sorted(skills, key=lambda s: s.path)


def parse_frontmatter_name(skill_md: Path) -> str | None:
    text = read_text(skill_md)
    match = re.search(r"^name:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else None


def iter_files(skill: Skill, include_tests: bool) -> Iterable[Path]:
    skill_dir = Path(skill.path)
    for path in skill_dir.rglob("*"):
        if path.is_dir() or should_skip(path, include_tests):
            continue
        if path.suffix.lower() in TEXT_EXTS:
            yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def normalize_link(raw: str) -> str:
    target = raw.strip().split()[0].strip("<>")
    return target.split("#", 1)[0]


def is_external(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or target.startswith(("http://", "https://", "mailto:"))
        or "::" in target
    )


def resolve_target(source_file: Path, skill_dir: Path, target: str, from_skill_refs: bool) -> Path:
    target_path = Path(target)
    if target_path.is_absolute():
        return target_path
    base = skill_dir if from_skill_refs else source_file.parent
    return (base / target_path).resolve()


def extract_skill_reference_paths(skill_md: Path) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for line in read_text(skill_md).splitlines():
        match = REF_PATH_RE.match(line)
        if not match:
            continue
        raw = (match.group(1) or match.group(2) or "").strip().strip("\"'")
        if raw and not raw.startswith("<"):
            refs.append((raw, line.strip()))
    return refs


def extract_markdown_links(path: Path) -> list[tuple[str, str]]:
    text = read_text(path)
    links: list[tuple[str, str]] = []
    for line in text.splitlines():
        for raw in LINK_RE.findall(line):
            target = normalize_link(raw)
            if target:
                links.append((target, line.strip()))
    return links


def add_finding(findings: list[Finding], seen: set[tuple[str, str, str]], finding: Finding) -> None:
    key = (finding.problem, finding.file, finding.target)
    if key in seen:
        return
    seen.add(key)
    findings.append(finding)


def analyze(skills: list[Skill], include_tests: bool) -> dict:
    findings: list[Finding] = []
    seen_findings: set[tuple[str, str, str]] = set()
    referenced_targets: set[Path] = set()
    skill_names = {skill.name for skill in skills}
    reference_basenames: dict[str, list[Path]] = {}

    for skill in skills:
        skill_dir = Path(skill.path)
        skill_md = Path(skill.skill_md)

        for raw, evidence in extract_skill_reference_paths(skill_md):
            if is_external(raw):
                continue
            target = resolve_target(skill_md, skill_dir, raw, from_skill_refs=True)
            referenced_targets.add(target)
            if not target.exists():
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "FAIL",
                        "missing_reference_target",
                        str(skill_md),
                        raw,
                        "SKILL.md reference path does not exist.",
                        evidence,
                    ),
                )

        for path in iter_files(skill, include_tests):
            if path.parts[-2:-1] == ("references",):
                reference_basenames.setdefault(path.name, []).append(path)

            text = read_text(path)
            for line in text.splitlines():
                if not ESCALATION_LINE_RE.search(line):
                    continue
                for match in SLASH_SKILL_RE.finditer(line):
                    target_name = match.group("name")
                    if target_name not in skill_names:
                        add_finding(
                            findings,
                            seen_findings,
                            Finding(
                                "FAIL",
                                "dead_escalation_target",
                                str(path),
                                f"/{target_name}",
                                "Escalation or delegation target is not a discovered skill in this skill-set.",
                                line.strip(),
                            ),
                        )

            # Markdown link extraction only makes sense in markdown-like files.
            # Skip code files where `[x](y)` syntax is not a link (e.g. dict
            # subscripts in Python source that may slip past IGNORE_DIRS).
            if path.suffix.lower() in {".md", ".txt"}:
                for raw, evidence in extract_markdown_links(path):
                    if is_external(raw):
                        continue
                    target = resolve_target(path, skill_dir, raw, from_skill_refs=False)
                    referenced_targets.add(target)
                    if not target.exists():
                        add_finding(
                            findings,
                            seen_findings,
                            Finding(
                                "FAIL",
                                "broken_relative_path",
                                str(path),
                                raw,
                                "Markdown link target does not exist from declaring file.",
                                evidence,
                            ),
                        )

            if "fallback" in text.lower() and re.search(r"fallback\s+to|fall\s+back\s+to", text, re.I):
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "WARN",
                        "fallback_violates_fail_stop_policy",
                        str(path),
                        "",
                        "File mentions fallback; review whether this violates fail-stop policy.",
                        "fallback",
                    ),
                )

            if path.name != "analyze_skill_family.py" and re.search(r"\b(specs/arguments\.yml|aibdd-plan/assets/boundaries)\b", text):
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "WARN",
                        "obsolete_reference_still_linked",
                        str(path),
                        "",
                        "File mentions a known legacy or superseded path.",
                        "legacy path",
                    ),
                )

            if path.name != "SKILL.md" and "_" in path.stem and path.suffix.lower() not in {".py", ".sh"}:
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "WARN",
                        "inconsistent_naming_convention",
                        str(path),
                        path.name,
                        "Filename contains underscore; verify this is intentional for this artifact type.",
                        path.name,
                    ),
                )

        for ref_path in (skill_dir / "references").rglob("*.md") if (skill_dir / "references").exists() else []:
            if ref_path.resolve() not in referenced_targets and ref_path.name != "README.md":
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "WARN",
                        "unused_reference_file",
                        str(ref_path),
                        "",
                        "Reference file is not linked by SKILL.md or local markdown links.",
                        ref_path.name,
                    ),
                )

        for asset_path in (skill_dir / "assets").rglob("*") if (skill_dir / "assets").exists() else []:
            if asset_path.is_file() and asset_path.resolve() not in referenced_targets:
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        "INFO",
                        "unreachable_asset_file",
                        str(asset_path),
                        "",
                        "Asset file is not linked by markdown references; verify a script/template resolver reaches it.",
                        asset_path.name,
                    ),
                )

    for basename, paths in reference_basenames.items():
        unique_paths = sorted({p.resolve() for p in paths})
        if len(unique_paths) > 1:
            is_convention = basename in PER_SKILL_CONVENTION_BASENAMES
            severity = "INFO" if is_convention else "WARN"
            message = (
                "Per-skill convention basename appears in multiple skills; expected by programlike-skill-creator (each scoped to its own skill)."
                if is_convention
                else "Multiple reference files share the same basename across the analyzed skill-set."
            )
            for path in unique_paths:
                add_finding(
                    findings,
                    seen_findings,
                    Finding(
                        severity,
                        "duplicate_ssot",
                        str(path),
                        basename,
                        message,
                        ", ".join(str(p) for p in unique_paths[:5]),
                    ),
                )

    counts = {"fail": 0, "warn": 0, "info": 0}
    for finding in findings:
        counts[finding.severity.lower()] += 1

    status = "fail" if counts["fail"] else "warn" if counts["warn"] else "ok"
    return {
        "status": status,
        "skill_roots": sorted({str(Path(skill.path).parent) for skill in skills}),
        "skills": [asdict(skill) for skill in skills],
        "findings": [asdict(finding) for finding in sorted(findings, key=lambda f: (f.severity, f.problem, f.file))],
        "summary": counts,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Skill Family Consistency Report",
        "",
        "## Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Skills: {len(report['skills'])}",
        f"- FAIL: {report['summary']['fail']}",
        f"- WARN: {report['summary']['warn']}",
        f"- INFO: {report['summary']['info']}",
        "",
        "## Findings",
        "",
    ]
    if not report["findings"]:
        lines.append("No findings.")
    else:
        for finding in report["findings"]:
            lines.extend(
                [
                    f"- **{finding['severity']}** `{finding['problem']}` in `{finding['file']}`",
                    f"  - Target: `{finding['target']}`" if finding["target"] else "  - Target: n/a",
                    f"  - {finding['message']}",
                    f"  - Evidence: `{finding['evidence']}`",
                ]
            )
    lines.extend(["", "## Skill Inventory", ""])
    for skill in report["skills"]:
        lines.append(f"- `{skill['name']}` — `{skill['path']}`")
    lines.extend(
        [
            "",
            "## Analyzer Coverage",
            "",
            "- Scans SKILL.md reference YAML paths.",
            "- Scans markdown links in text artifacts.",
            "- Checks slash-command targets against discovered skill names.",
            "- Flags unused references and apparently unreachable assets.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    roots = [Path(root) for root in args.roots]
    missing_roots = [str(root) for root in roots if not root.exists()]
    if missing_roots:
        print(f"Missing root path(s): {', '.join(missing_roots)}", file=sys.stderr)
        return 2

    skills = discover_skills(roots, include_tests=args.include_tests)
    report = analyze(skills, include_tests=args.include_tests)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    if args.md_out:
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md_out).write_text(render_markdown(report), encoding="utf-8")

    print(payload)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
