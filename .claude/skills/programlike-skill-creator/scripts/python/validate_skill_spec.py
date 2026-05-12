#!/usr/bin/env python3
"""
validate_skill_spec.py — 規章 §15 C1–C16 compliance validator.

Usage:
    validate_skill_spec.py <skill_directory>

Exit codes:
    0 — all checks PASS (or only SOFT WARN)
    1 — at least one HARD FAIL
    2 — usage / IO error

Detects 規章 violations in SKILL.md per `references/compliance-checklist.md`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

import yaml


VERB_WHITELIST = {
    # 規章 §5 core verbs
    "READ", "LOAD", "WRITE", "COMPUTE", "THINK", "DELEGATE", "VALIDATE", "EMIT",
    "ASSERT", "REPORT", "STOP", "TRIGGER", "IF", "ELSE", "END", "LOOP",
    "RETURN", "GOTO", "BRANCH", "MARK", "WAIT",
    # tolerated utility verbs (synonyms / specialisations of core)
    "CAPTURE", "CLASSIFY", "CREATE", "ENFORCE", "EXPAND", "LIST", "PREFIX",
    "STUB", "ASK", "JOIN", "INLINE", "BIND", "CROSS-VALIDATE",
    "CONTINUE", "REMEDIATE", "OFFER", "SKIP",
    "COMPOSE", "PARSE", "RENDER", "REPLACE", "SORT", "TRANSLATE",
    "EXTRACT", "ENUMERATE", "DESIGN", "EXECUTE", "PRESERVE",
    "RENAME", "GUARD", "FORMULATE", "PROBE",
    "REMOVE", "DELETE", "SERIALIZE", "RECEIVE", "RESOLVE", "SWEEP",
    "APPLY", "GENERATE", "MERGE", "DISPATCH", "SCAN", "FILTER",
    "COUNT", "SELECT", "REJECT", "ACCEPT", "AUDIT",
    "ASSIGN", "EXAMINE", "QUANTIFY", "VERIFY", "AGGREGATE",
    "INSERT", "APPEND", "PREPEND", "DETECT", "DERIVE", "DRAFT", "JUDGE", "MATCH",
}
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
HARD_FAIL_CHECKS = {"C1", "C2", "C3", "C4", "C5", "C8", "C13", "C14", "C15", "C16", "C25"}


class Finding(NamedTuple):
    code: str
    severity: str  # "HARD" or "SOFT"
    message: str
    line: int = 0


def split_frontmatter(content: str) -> tuple[dict | None, str, int]:
    """Return (frontmatter_dict, body_text, body_start_line). body_start_line is 1-based."""
    if not content.startswith("---"):
        return None, content, 1
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        return None, content, 1
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, content, 1
    body_start = content[: m.end()].count("\n") + 1
    return fm if isinstance(fm, dict) else None, content[m.end():], body_start


def check_frontmatter(fm: dict | None, findings: list[Finding]) -> None:
    if fm is None:
        findings.append(Finding("C1", "HARD", "Missing or invalid YAML frontmatter"))
        return
    extra = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if extra:
        findings.append(Finding("C1", "HARD", f"Unexpected frontmatter keys: {sorted(extra)}"))
    if "name" not in fm or "description" not in fm:
        findings.append(Finding("C1", "HARD", "Missing required name/description"))
        return
    desc = fm.get("description", "")
    if not isinstance(desc, str):
        findings.append(Finding("C2", "HARD", f"description not string: {type(desc).__name__}"))
        return
    if len(desc) > 1024:
        findings.append(Finding("C2", "HARD", f"description {len(desc)} chars > 1024"))
    if "<" in desc or ">" in desc:
        findings.append(Finding("C8", "HARD", "description contains angle brackets"))


def is_reference_hub(fm: dict | None) -> bool:
    """Detect reference-hub skill via metadata.skill-type per spec.md §14.1.1."""
    if not fm:
        return False
    meta = fm.get("metadata", {})
    if not isinstance(meta, dict):
        return False
    return meta.get("skill-type") == "reference-hub"


def check_top_sections(body: str, body_start: int, findings: list[Finding], fm: dict | None = None) -> None:
    h2_pattern = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
    matches = list(h2_pattern.finditer(body))
    if not matches:
        findings.append(Finding("C3", "HARD", "No top-level H2 sections found"))
        return
    first = matches[0].group(1).strip()
    if not re.match(r"^§1\s+REFERENCES$", first):
        findings.append(Finding("C3", "HARD", f"First H2 must be `§1 REFERENCES`, got `{first}`"))
    # C4 reference-hub 豁免（per spec.md §14.1.1）
    if is_reference_hub(fm):
        return
    if len(matches) >= 2:
        second = matches[1].group(1).strip()
        if not re.match(r"^§2\s+SOP$", second):
            findings.append(Finding("C4", "HARD", f"Second H2 must be `§2 SOP`, got `{second}`"))
    else:
        findings.append(Finding("C4", "HARD", "Missing `§2 SOP` section"))

    allowed_h2 = (
        r"^§1\s+REFERENCES$",
        r"^§2\s+SOP$",
        r"^§3\s+CROSS-REFERENCES$",
    )
    for m in matches:
        title = m.group(1).strip()
        if not any(re.match(pat, title) for pat in allowed_h2):
            findings.append(Finding("C15", "HARD", f"Unexpected top-level H2 section `{title}`; keep execution flow inside `§2 SOP`"))


def _section_bounds(body: str, section_re: str) -> tuple[int, int] | None:
    """Return (start_offset_of_content, end_offset) for the section matching section_re, or None."""
    m = re.search(section_re, body, re.MULTILINE)
    if not m:
        return None
    content_start = m.end()
    next_h2 = re.search(r"^##\s+", body[content_start:], re.MULTILINE)
    return (content_start, content_start + next_h2.start() if next_h2 else len(body))


def check_phase_headers(body: str, findings: list[Finding]) -> list[tuple[int, int, str]]:
    """Return list of phases inside §2 SOP only."""
    phases = []
    sop_bounds = _section_bounds(body, r"^##\s+§2\s+SOP\s*$")
    if sop_bounds is None:
        return phases
    sop_body = body[sop_bounds[0]:sop_bounds[1]]
    h3_re = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    valid_re = re.compile(r"^Phase\s+(\d+)\s+[—–-]\s+\S+")
    for m in h3_re.finditer(sop_body):
        header = m.group(1).strip()
        if header.startswith("Phase"):
            if not valid_re.match(header):
                findings.append(Finding("C5", "HARD", f"Malformed phase header in §2 SOP: `### {header}` (expected `### Phase N — <name>`)"))
            else:
                phases.append((m.start(), header.count("\n"), header))
    return phases


def check_step_verbs(body: str, findings: list[Finding]) -> None:
    """Extract first verb of each step. Skip `[TAG]` prefixes (e.g., `[USER INTERACTION]`)."""
    step_re = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+(.+?)$", re.MULTILINE)
    tag_re = re.compile(r"^\[[^\]]+\]\s*")
    bad_verbs: set[str] = set()
    for m in step_re.finditer(body):
        body_text = m.group(1).strip()
        # strip leading `[USER INTERACTION]` / `[STATEFUL]` / etc tag(s)
        while True:
            new_text, n = tag_re.subn("", body_text)
            if n == 0:
                break
            body_text = new_text
        # extract first word
        tokens = body_text.split()
        if not tokens:
            continue
        body_text = re.sub(r"^`\$\$?[a-z_][a-z0-9_]*`\s*=\s*", "", body_text)
        body_text = re.sub(r"^\$\$?[a-z_][a-z0-9_]*\s*=\s*", "", body_text)
        tokens = body_text.split()
        if not tokens:
            continue
        first_word = tokens[0].strip("`*").rstrip(":.,()")
        if not first_word or first_word.startswith("#"):
            continue
        if first_word.upper() not in VERB_WHITELIST:
            bad_verbs.add(first_word)
    if bad_verbs:
        findings.append(Finding("C6", "SOFT", f"Steps starting with non-whitelist verbs: {sorted(bad_verbs)}"))


def check_goto_targets(body: str, findings: list[Finding]) -> None:
    """Match GOTO only inside step body — ignore prose / code blocks. Step lines start with `<digits>(.<digits>)* ` after optional indent."""
    # strip code blocks first to avoid false positives in templates / examples
    code_block_re = re.compile(r"^(```|~~~).*?^\1\s*$", re.DOTALL | re.MULTILINE)
    sanitized = code_block_re.sub("", body)
    # Step body GOTO: indented number prefix anywhere on the line, then GOTO
    step_goto_re = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+.*?\bGOTO\s+(\S+)", re.MULTILINE)
    valid_target = re.compile(r"^#\d+(\.\d+)*$")
    for m in step_goto_re.finditer(sanitized):
        target = m.group(1).strip("`,.;:")
        if not valid_target.match(target):
            findings.append(Finding("C14", "HARD", f"GOTO target `{target}` is not `#phase.step` literal"))


def check_loop_budget(body: str, findings: list[Finding]) -> None:
    """LOOP must declare bounds. Tolerate `LOOP per <noun>` (bounded foreach over finite collection)."""
    loop_re = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+LOOP\b(.*)$", re.MULTILINE)
    for m in loop_re.finditer(body):
        rest = m.group(1)
        has_budget = bool(re.search(r"\bmax\s+\d+", rest))
        has_until = "until" in rest.lower() or "while" in rest.lower()
        is_foreach = re.search(r"\bper\s+\S+", rest, re.IGNORECASE) is not None
        if not (has_budget or has_until or is_foreach):
            findings.append(Finding("C11", "SOFT", f"LOOP missing budget/exit-condition: `{m.group(0).strip()}`"))


def check_forbidden_failure_section(body: str, findings: list[Finding]) -> None:
    if re.search(r"^##\s+§\d+\s+FAILURE\s*&\s*FALLBACK", body, re.MULTILINE):
        findings.append(Finding("C15", "HARD", "Failure/fallback handling must be modeled inside `§2 SOP`, not as a separate H2 section"))


def check_references_yaml(skill_dir: Path, body: str, findings: list[Finding]) -> None:
    """C16: §1 REFERENCES must contain exactly one fenced YAML block.

    Schema:
      references:
        - path: <non-empty string>
          purpose: <non-empty string>

    No `id`, `kind`, or `phase_scope`: `path` syntax is enough to infer hub refs.
    """
    bounds = _section_bounds(body, r"^##\s+§1\s+REFERENCES\s*$")
    if bounds is None:
        return
    section = body[bounds[0]:bounds[1]]
    yaml_blocks = re.findall(
        r"^```ya?ml\s*\n(.*?)^```\s*$",
        section,
        flags=re.MULTILINE | re.DOTALL,
    )
    if len(yaml_blocks) != 1:
        findings.append(
            Finding(
                "C16",
                "HARD",
                f"§1 REFERENCES must contain exactly one fenced yaml block, got {len(yaml_blocks)}",
            )
        )
        return

    try:
        data = yaml.safe_load(yaml_blocks[0])
    except yaml.YAMLError as exc:
        findings.append(Finding("C16", "HARD", f"§1 REFERENCES YAML parse failed: {exc}"))
        return

    if not isinstance(data, dict) or set(data.keys()) != {"references"}:
        findings.append(Finding("C16", "HARD", "§1 REFERENCES YAML root must be exactly `references`"))
        return
    refs = data["references"]
    if not isinstance(refs, list):
        findings.append(Finding("C16", "HARD", "`references` must be a list"))
        return

    for i, ref in enumerate(refs, start=1):
        if not isinstance(ref, dict):
            findings.append(Finding("C16", "HARD", f"references[{i}] must be a mapping"))
            continue
        keys = set(ref.keys())
        if keys != {"path", "purpose"}:
            findings.append(
                Finding(
                    "C16",
                    "HARD",
                    f"references[{i}] keys must be exactly path/purpose, got {sorted(keys)}",
                )
            )
            continue
        path = ref.get("path")
        purpose = ref.get("purpose")
        if not isinstance(path, str) or not path.strip():
            findings.append(Finding("C16", "HARD", f"references[{i}].path must be non-empty string"))
            continue
        if not isinstance(purpose, str) or not purpose.strip():
            findings.append(Finding("C16", "HARD", f"references[{i}].purpose must be non-empty string"))
        if "::" in path or path.startswith("${") or Path(path).is_absolute():
            continue
        if not (skill_dir / path).exists():
            findings.append(Finding("C16", "HARD", f"references[{i}].path does not exist: {path}"))


def check_body_size(body: str, findings: list[Finding]) -> None:
    line_count = body.count("\n")
    if line_count > 300:
        findings.append(Finding("C9", "SOFT", f"SKILL.md body {line_count} lines > 300"))


def check_step_local_flow_in_refs(skill_dir: Path, findings: list[Finding]) -> None:
    """C13: references / assets / scripts should not contain ACTIVE step flow patterns.

    Tolerate Phase / Step word inside fenced code blocks (showing examples / templates),
    inside markdown tables (regulatory enumeration), and in known SSOT files.
    """
    code_block_re = re.compile(r"^(```|~~~).*?^\1\s*$", re.DOTALL | re.MULTILINE)
    table_row_re = re.compile(r"^\|.*\|\s*$", re.MULTILINE)
    flow_pattern = re.compile(r"^\s*Phase\s+\d+\s+[—–-]\s+|^\s*\d+\.\s+(READ|WRITE|LOAD|COMPUTE|DELEGATE|ASSERT|VALIDATE|EMIT|REPORT|STOP|TRIGGER|IF)\b", re.MULTILINE)
    SSOT_FILES = {"spec.md", "compliance-checklist.md", "verb-whitelist.md", "intake-questions.md"}
    for sub in ("references", "assets"):
        d = skill_dir / sub
        if not d.is_dir():
            continue
        for f in d.rglob("*.md"):
            if f.name in SSOT_FILES:
                continue
            text = f.read_text(encoding="utf-8")
            sanitized = code_block_re.sub("", text)
            sanitized = table_row_re.sub("", sanitized)
            if flow_pattern.search(sanitized):
                findings.append(Finding("C13", "HARD", f"{f.relative_to(skill_dir)} contains active flow pattern outside code blocks"))


def check_self_contained_artifact_closure(skill_dir: Path, body: str, findings: list[Finding]) -> None:
    """C25: runtime gate/rubric/contract must not depend on transient external docs.

    Stable shared hubs such as `aibdd-core::...` and runtime variables like
    `${PLAN_SPEC}` are allowed. The forbidden class is ad-hoc external research,
    eval, and plan documents becoming a skill's own contract/rubric SSOT.
    """
    code_block_re = re.compile(r"^(```|~~~).*?^\1\s*$", re.DOTALL | re.MULTILINE)
    gate_word = re.compile(r"\b(?:rubric|gate|contract|oracle|verdict|quality)\b", re.IGNORECASE)
    forbidden_path_patterns = [
        re.compile(r"(?:^|[`=\s(])(?:\S*/)?research/[^`\s)]*\.(?:md|yml|yaml|json)\b", re.IGNORECASE),
        re.compile(r"(?:^|[`=\s(])\.cursor/plans/[^`\s)]*\.(?:md|yml|yaml|json)\b", re.IGNORECASE),
        re.compile(r"(?:^|[`=\s(])[^*`\s)][^`\s)]*outcome-eval\.md\b", re.IGNORECASE),
        re.compile(r"(?:^|[`=\s(])/Users/[^`\s)]*/(?:research|\.cursor/plans)/[^`\s)]*\.(?:md|yml|yaml|json)\b", re.IGNORECASE),
        re.compile(r"(?:rubric|gate|contract|oracle|verdict|quality)\s*=\s*[^`\s)]*(?:^|/)(?:eval|proposal)\.md\b", re.IGNORECASE),
    ]

    SSOT_FILES = {"spec.md", "compliance-checklist.md", "references-vs-assets.md", "verb-whitelist.md", "intake-questions.md"}
    files = [skill_dir / "SKILL.md"]
    for sub in ("references", "reasoning", "assets"):
        d = skill_dir / sub
        if d.is_dir():
            files.extend(p for p in d.rglob("*") if p.is_file() and p.suffix in {".md", ".yml", ".yaml", ".json", ".txt"})

    for path in files:
        if path.name in SSOT_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        sanitized = code_block_re.sub("", text)
        for line in sanitized.splitlines():
            if not gate_word.search(line):
                continue
            for pattern in forbidden_path_patterns:
                m = pattern.search(line)
                if m:
                    snippet = m.group(0).strip()
                    rel = path.relative_to(skill_dir) if path != skill_dir / "SKILL.md" else Path("SKILL.md")
                    findings.append(Finding("C25", "HARD", f"{rel} has non-self-contained runtime gate/rubric/contract link: {snippet[:160]}"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_skill_spec.py <skill_directory>", file=sys.stderr)
        return 2
    skill_dir = Path(sys.argv[1]).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"error: SKILL.md not found at {skill_md}", file=sys.stderr)
        return 2
    content = skill_md.read_text(encoding="utf-8")
    findings: list[Finding] = []

    fm, body, body_start = split_frontmatter(content)
    check_frontmatter(fm, findings)
    check_top_sections(body, body_start, findings, fm=fm)
    phases = check_phase_headers(body, findings)
    check_step_verbs(body, findings)
    check_goto_targets(body, findings)
    check_loop_budget(body, findings)
    check_forbidden_failure_section(body, findings)
    check_references_yaml(skill_dir, body, findings)
    check_body_size(body, findings)
    check_step_local_flow_in_refs(skill_dir, findings)
    check_self_contained_artifact_closure(skill_dir, body, findings)

    hard = [f for f in findings if f.severity == "HARD"]
    soft = [f for f in findings if f.severity == "SOFT"]

    if not findings:
        print(f"PASS — {skill_md} 規章-compliant (no findings)")
        return 0

    print(f"REPORT for {skill_md}")
    print(f"  HARD FAIL: {len(hard)}")
    print(f"  SOFT WARN: {len(soft)}")
    print()
    for f in hard + soft:
        print(f"  [{f.severity}] {f.code}: {f.message}")

    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
