#!/usr/bin/env python3
"""
eval_reasoning_quality.py — evaluate internal quality of Reasoning Phase files.

Usage:
    eval_reasoning_quality.py <skill_directory>

Exit codes:
    0 — reasoning eval checks pass
    1 — reasoning eval violations found
    2 — usage / IO error

The script scans `<skill>/reasoning/**/*.md`, checks `rp_type: reasoning_phase`
files for required RP sections, computes D/S/I density, verifies derived axes are
carried into Material Reducer SOP, and writes `.quality/reasoning-eval-report.json`.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


D_VERBS = {
    "READ", "LOAD", "WRITE", "CREATE", "DELETE", "COMPUTE", "DERIVE", "PARSE", "RENDER",
    "ASSERT", "MATCH", "TRIGGER", "DELEGATE", "MARK", "BRANCH", "GOTO", "IF",
    "ELSE", "END", "LOOP", "RETURN", "STOP", "EMIT", "WAIT", "EXTRACT", "VALIDATE",
}
S_VERBS = {
    "THINK", "CLASSIFY", "JUDGE", "DECIDE", "DRAFT", "EDIT",
    "PARAPHRASE", "CRITIQUE", "SUMMARIZE", "EXPLAIN",
}
I_VERBS = {"ASK"}

REQUIRED_SECTIONS = [
    "## 1. Material Sourcing",
    "## 3. Reasoning SOP",
    "## 4. Material Reducer SOP",
]
MODELING_HEADING = "## 2. Modeling Element Definition"
LEGACY_CLASSIFICATION_HEADING = "## 2. Classification Definition"
FORBIDDEN_MODELING_KEYS = {"source_of_truth", "classify_rule"}


@dataclass
class Finding:
    severity: str
    path: str
    message: str


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    if not text.startswith("---\n"):
        return None, text
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, text[m.end():]
    return data if isinstance(data, dict) else None, text[m.end():]


def section_text(body: str, heading: str) -> str:
    pattern = re.compile(r"^" + re.escape(heading) + r"\s*$", re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return ""
    start = m.end()
    next_h2 = re.search(r"^##\s+", body[start:], re.MULTILINE)
    end = start + next_h2.start() if next_h2 else len(body)
    return body[start:end]


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def extract_step_verb(line: str) -> str | None:
    m = re.match(r"^\s*\d+(?:\.\d+)*\.?\s+(.+?)$", line)
    if not m:
        return None
    body = m.group(1).strip()
    body = re.sub(r"^\[[^\]]+\]\s*", "", body)
    body = re.sub(r"^`\$\$?[a-z_][a-z0-9_]*`\s*=\s*", "", body)
    body = re.sub(r"^\$\$?[a-z_][a-z0-9_]*\s*=\s*", "", body)
    token = body.split(maxsplit=1)[0] if body else ""
    return token.strip("`*").rstrip(":.,()").upper() or None


def count_verbs(body: str) -> dict[str, int]:
    counts = {"D": 0, "S": 0, "I": 0, "unknown": 0}
    searchable = "\n".join(
        section_text(body, heading)
        for heading in ("## 1. Material Sourcing", "## 3. Reasoning SOP", "## 4. Material Reducer SOP")
    )
    for line in strip_code_blocks(searchable).splitlines():
        verb = extract_step_verb(line)
        if not verb:
            continue
        if verb in D_VERBS:
            counts["D"] += 1
        elif verb in S_VERBS:
            counts["S"] += 1
        elif verb in I_VERBS:
            counts["I"] += 1
        else:
            counts["unknown"] += 1
    return counts


def fenced_yaml_payload(text: str) -> dict[str, Any] | None:
    for m in re.finditer(r"```(?:yaml|yml)\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE):
        try:
            data = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            return data
    return None


def find_forbidden_keys(value: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if key in FORBIDDEN_MODELING_KEYS:
                hits.append(key_path)
            hits.extend(find_forbidden_keys(child, key_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return hits


def extract_model_elements(modeling: str) -> tuple[list[str], list[Finding], dict[str, Any] | None]:
    findings: list[Finding] = []
    data = fenced_yaml_payload(modeling)
    if data is None:
        return [], findings, None
    for key_path in find_forbidden_keys(data):
        findings.append(Finding("HARD", "", f"Modeling Element Definition contains forbidden schema key `{key_path}`"))
    root = data.get("modeling_element_definition")
    if not isinstance(root, dict):
        findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `modeling_element_definition` root"))
        return [], findings, data
    if not root.get("output_model"):
        findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `modeling_element_definition.output_model`"))
    element_rules = root.get("element_rules")
    if not isinstance(element_rules, dict):
        findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `modeling_element_definition.element_rules`"))
    else:
        element_vs_field = element_rules.get("element_vs_field")
        if not isinstance(element_vs_field, dict):
            findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `element_rules.element_vs_field`"))
        else:
            if not element_vs_field.get("element"):
                findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `element_rules.element_vs_field.element`"))
            if not element_vs_field.get("field"):
                findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `element_rules.element_vs_field.field`"))
    elements = root.get("elements")
    if not isinstance(elements, dict):
        findings.append(Finding("HARD", "", "Modeling Element Definition YAML must contain `modeling_element_definition.elements` map"))
        return [], findings, data
    missing_fields = [
        name for name, spec in elements.items()
        if not isinstance(spec, dict) or "fields" not in spec
    ]
    for name in missing_fields:
        findings.append(Finding("HARD", "", f"model element `{name}` has no `fields` block"))
    missing_roles = [
        name for name, spec in elements.items()
        if not isinstance(spec, dict) or "role" not in spec
    ]
    for name in missing_roles:
        findings.append(Finding("HARD", "", f"model element `{name}` has no `role` field"))
    return sorted(str(name) for name in elements.keys()), findings, data


def extract_derived_axes(classification: str) -> list[str]:
    axes: list[str] = []
    # Preferred style: `1. `BDDExample``.
    for m in re.finditer(r"^\s*\d+(?:\.\d+)*\.?\s+`([^`]+)`", classification, re.MULTILINE):
        axes.append(m.group(1).strip())
    # Common markdown bullet style: `- `DerivedAxis`: definition`.
    for m in re.finditer(r"^\s*-\s+`([^`]+)`\s*:", classification, re.MULTILINE):
        axes.append(m.group(1).strip())
    # Fallback YAML-ish style: `- name: BDDExample`.
    if not axes:
        for m in re.finditer(r"^\s*-\s+name:\s*([A-Za-z][A-Za-z0-9_-]*)\s*$", classification, re.MULTILINE):
            axes.append(m.group(1).strip())
    return sorted(dict.fromkeys(axes))


def modeling_semantic_warnings(modeling: str, axes: list[str], relpath: str) -> list[Finding]:
    findings: list[Finding] = []
    suspicious_suffixes = ("Verdict", "Check", "Pass", "Score", "Temp", "DraftCandidate")
    field_like_suffixes = ("Ref", "Label", "Guard", "Condition", "Name")
    for axis in axes:
        if axis.endswith(suspicious_suffixes):
            findings.append(
                Finding(
                    "SOFT",
                    relpath,
                    f"model element `{axis}` looks like an intermediate reasoning variable; keep only output model elements",
                )
            )
        if axis.endswith(field_like_suffixes):
            findings.append(
                Finding(
                    "SOFT",
                    relpath,
                    f"model element `{axis}` looks like a field; consider nesting it under its parent element's `fields` block",
                )
            )

    lowered = modeling.lower()
    format_terms = ("mermaid", "flowchart", "projection", "render format")
    if any(term in lowered for term in format_terms):
        findings.append(
            Finding(
                "SOFT",
                relpath,
                "Modeling Element Definition mentions render/format/projection concerns; ensure they belong to output, otherwise move to reducer",
            )
        )
    return findings


def ask_bindings(body: str) -> list[str]:
    bindings: list[str] = []
    for line in strip_code_blocks(body).splitlines():
        if not re.search(r"=\s*ASK\b", line):
            continue
        m = re.search(r"`?(\$\$?[a-z_][a-z0-9_]*)`?\s*=\s*ASK\b", line)
        if m:
            bindings.append(m.group(1))
        else:
            bindings.append("<unbound-ASK>")
    return bindings


def has_chain_of_thought_output(body: str) -> bool:
    for line in strip_code_blocks(body).splitlines():
        lowered = line.lower()
        if "chain-of-thought" not in lowered:
            continue
        if re.search(r"\b(emit|write|output|include|report|render)\b", lowered):
            return True
    return False


def evaluate_rp(path: Path, relpath: str, meta: dict[str, Any], body: str) -> dict[str, Any]:
    findings: list[Finding] = []
    for heading in REQUIRED_SECTIONS:
        if not re.search(r"^" + re.escape(heading) + r"\s*$", body, re.MULTILINE):
            findings.append(Finding("HARD", relpath, f"missing required section `{heading}`"))
    has_modeling = re.search(r"^" + re.escape(MODELING_HEADING) + r"\s*$", body, re.MULTILINE)
    has_legacy_classification = re.search(r"^" + re.escape(LEGACY_CLASSIFICATION_HEADING) + r"\s*$", body, re.MULTILINE)
    if not has_modeling and not has_legacy_classification:
        findings.append(Finding("HARD", relpath, f"missing required section `{MODELING_HEADING}`"))
    if has_legacy_classification and not has_modeling:
        findings.append(Finding("SOFT", relpath, "legacy `Classification Definition` section should be renamed to `Modeling Element Definition`"))

    counts = count_verbs(body)
    total = counts["D"] + counts["S"] + counts["I"] + counts["unknown"]
    s_density = (counts["S"] / total) if total else 0.0

    modeling = section_text(body, MODELING_HEADING)
    legacy_classification = section_text(body, LEGACY_CLASSIFICATION_HEADING)
    modeling_source = modeling or legacy_classification
    reasoning = section_text(body, "## 3. Reasoning SOP")
    reducer = section_text(body, "## 4. Material Reducer SOP")
    completion = section_text(body, "## 5. Completion Contract")
    if completion:
        findings.append(Finding("HARD", relpath, "`Completion Contract` is obsolete; fold its schema into Material Reducer SOP"))
    if modeling:
        axes, schema_findings, _schema = extract_model_elements(modeling)
        for finding in schema_findings:
            finding.path = relpath
            findings.append(finding)
    else:
        axes = extract_derived_axes(legacy_classification)

    if not axes:
        findings.append(Finding("SOFT", relpath, "no model elements found in Modeling Element Definition"))
    findings.extend(modeling_semantic_warnings(modeling_source, axes, relpath))

    missing_from_reducer = []
    for axis in axes:
        if axis not in reducer:
            missing_from_reducer.append(axis)
            findings.append(Finding("HARD", relpath, f"model element `{axis}` missing from reducer output"))
        if axis not in reasoning and axis not in reducer:
            findings.append(Finding("SOFT", relpath, f"model element `{axis}` not mentioned in Reasoning SOP"))

    asks = ask_bindings(body)
    for binding in asks:
        if binding == "<unbound-ASK>":
            findings.append(Finding("HARD", relpath, "ASK step must bind its reply to `$var`"))
            continue
        if binding not in reducer:
            findings.append(Finding("HARD", relpath, f"ASK binding `{binding}` not traceable in reducer output"))

    if has_chain_of_thought_output(body):
        findings.append(Finding("HARD", relpath, "RP appears to output chain-of-thought"))

    return {
        "id": meta.get("id", relpath),
        "path": relpath,
        "reasoning_density": {
            "D": counts["D"],
            "S": counts["S"],
            "I": counts["I"],
            "unknown": counts["unknown"],
            "S_density": round(s_density, 4),
        },
        "model_elements": axes,
        "derived_axes": axes,
        "reducer_completeness": "pass" if not missing_from_reducer else "fail",
        "findings": [f.__dict__ for f in findings],
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 0
    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    skill_dir = Path(args[0]).resolve()
    if not skill_dir.is_dir():
        print(f"error: skill directory not found: {skill_dir}", file=sys.stderr)
        return 2

    quality_dir = skill_dir / ".quality"
    quality_dir.mkdir(exist_ok=True)

    rp_reports: list[dict[str, Any]] = []
    global_findings: list[Finding] = []
    reasoning_dir = skill_dir / "reasoning"

    if reasoning_dir.is_dir():
        for path in sorted(reasoning_dir.rglob("*.md")):
            relpath = str(path.relative_to(skill_dir))
            text = path.read_text(encoding="utf-8")
            meta, body = split_frontmatter(text)
            if meta is None:
                global_findings.append(Finding("HARD", relpath, "missing or invalid YAML frontmatter"))
                continue
            if meta.get("rp_type") != "reasoning_phase":
                continue
            rp_reports.append(evaluate_rp(path, relpath, meta, body))

    all_findings = global_findings + [
        Finding(item["severity"], item["path"], item["message"])
        for report in rp_reports
        for item in report["findings"]
    ]
    ok = not any(f.severity == "HARD" for f in all_findings)

    report = {
        "ok": ok,
        "skill_dir": str(skill_dir),
        "rp_count": len(rp_reports),
        "rp_reports": rp_reports,
        "findings": [f.__dict__ for f in all_findings],
    }
    report_path = quality_dir / "reasoning-eval-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"reasoning eval: {len(rp_reports)} RP files")
    print(f"wrote: {report_path}")
    for finding in all_findings:
        print(f"{finding.severity}: {finding.path}: {finding.message}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
