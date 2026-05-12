#!/usr/bin/env python3
"""
eval_reasoning_graph.py — validate RP YAML meta and render a derivation graph.

Usage:
    eval_reasoning_graph.py <skill_directory>

Exit codes:
    0 — graph checks pass
    1 — reasoning graph violations found
    2 — usage / IO error

The script scans `<skill>/reasoning/**/*.md`, parses required YAML frontmatter,
builds a bipartite RP/Axis graph, writes `.quality/reasoning-derivation-graph.mmd`,
and writes `.quality/reasoning-graph-report.json`.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_RP_TYPES = {"reasoning_phase", "polymorphism"}
ALLOWED_AXIS_KINDS = {"material_bundle", "required_axis", "derived_axis", "config", "reference", "decision", "cic"}
ALLOWED_SOURCES = {"caller", "skill_global", "upstream_rp", "reference", "filesystem"}


@dataclass
class Finding:
    severity: str
    path: str
    message: str


@dataclass
class RpFile:
    path: Path
    relpath: str
    meta: dict[str, Any]
    body: str


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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def item_name(item: Any) -> str | None:
    if isinstance(item, dict) and isinstance(item.get("name"), str):
        return item["name"]
    return None


def sanitize_node_id(raw: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")
    if not slug:
        slug = "node"
    if slug[0].isdigit():
        slug = "n_" + slug
    return slug


def mermaid_label(raw: str) -> str:
    return raw.replace('"', "'").replace("\n", " ")


def validate_meta(rp: RpFile, findings: list[Finding]) -> None:
    meta = rp.meta
    required = ["rp_type", "id", "context", "slot", "name", "consumes", "produces", "downstream"]
    for key in required:
        if key not in meta:
            findings.append(Finding("HARD", rp.relpath, f"missing meta field `{key}`"))

    rp_type = meta.get("rp_type")
    if rp_type not in ALLOWED_RP_TYPES:
        findings.append(Finding("HARD", rp.relpath, f"invalid rp_type `{rp_type}`"))

    rp_id = meta.get("id")
    if not isinstance(rp_id, str) or not rp_id.strip():
        findings.append(Finding("HARD", rp.relpath, "`id` must be non-empty string"))

    for list_key in ("consumes", "produces"):
        if not isinstance(meta.get(list_key), list):
            findings.append(Finding("HARD", rp.relpath, f"`{list_key}` must be a list"))
    if not isinstance(meta.get("downstream"), list):
        findings.append(Finding("HARD", rp.relpath, "`downstream` must be a list"))

    for item in as_list(meta.get("consumes")):
        name = item_name(item)
        if not name:
            findings.append(Finding("HARD", rp.relpath, "consume item missing `name`"))
            continue
        kind = item.get("kind")
        source = item.get("source")
        if kind not in ALLOWED_AXIS_KINDS:
            findings.append(Finding("HARD", rp.relpath, f"consume `{name}` invalid kind `{kind}`"))
        if source not in ALLOWED_SOURCES:
            findings.append(Finding("HARD", rp.relpath, f"consume `{name}` invalid source `{source}`"))

    for item in as_list(meta.get("produces")):
        name = item_name(item)
        if not name:
            findings.append(Finding("HARD", rp.relpath, "produce item missing `name`"))
            continue
        kind = item.get("kind")
        if kind not in ALLOWED_AXIS_KINDS:
            findings.append(Finding("HARD", rp.relpath, f"produce `{name}` invalid kind `{kind}`"))

    if rp_type == "polymorphism":
        if not isinstance(meta.get("selector"), dict):
            findings.append(Finding("HARD", rp.relpath, "polymorphism missing `selector` object"))
        if not isinstance(meta.get("variants"), list) or not meta.get("variants"):
            findings.append(Finding("HARD", rp.relpath, "polymorphism requires non-empty `variants`"))


def parse_required_axis(body: str) -> tuple[list[dict[str, Any]] | None, str | None]:
    section = re.search(
        r"^###\s+1\.1\s+Required Axis\s*$([\s\S]*?)(?=^###\s+1\.2\s+|^##\s+2\.\s+|\Z)",
        body,
        re.MULTILINE,
    )
    if not section:
        return None, "missing `### 1.1 Required Axis` section"

    yaml_block = re.search(r"```yaml\n(.*?)\n```", section.group(1), re.DOTALL)
    if not yaml_block:
        return None, "`### 1.1 Required Axis` must contain a yaml fenced block"

    try:
        data = yaml.safe_load(yaml_block.group(1))
    except yaml.YAMLError as exc:
        return None, f"invalid Required Axis YAML: {exc}"

    if not isinstance(data, dict) or not isinstance(data.get("required_axis"), list):
        return None, "Required Axis YAML must have top-level `required_axis` list"
    return data["required_axis"], None


def validate_required_axis(rp: RpFile, findings: list[Finding]) -> None:
    if rp.meta.get("rp_type") != "reasoning_phase":
        return

    axes, error = parse_required_axis(rp.body)
    if error:
        findings.append(Finding("HARD", rp.relpath, error))
        return

    assert axes is not None
    axis_names: set[str] = set()
    for axis in axes:
        if not isinstance(axis, dict):
            findings.append(Finding("HARD", rp.relpath, "Required Axis item must be object"))
            continue
        name = axis.get("name")
        if not isinstance(name, str) or not name:
            findings.append(Finding("HARD", rp.relpath, "Required Axis item missing `name`"))
            continue
        axis_names.add(name)

        source = axis.get("source")
        if not isinstance(source, dict) or source.get("kind") not in ALLOWED_SOURCES:
            findings.append(Finding("HARD", rp.relpath, f"Required Axis `{name}` has invalid `source.kind`"))
        if not isinstance(axis.get("granularity"), str) or not axis["granularity"].strip():
            findings.append(Finding("HARD", rp.relpath, f"Required Axis `{name}` missing `granularity`"))
        if not isinstance(axis.get("required_fields"), list):
            findings.append(Finding("HARD", rp.relpath, f"Required Axis `{name}` missing `required_fields` list"))
        check = axis.get("completeness_check")
        if not isinstance(check, dict) or not check.get("rule") or not check.get("on_missing"):
            findings.append(Finding("HARD", rp.relpath, f"Required Axis `{name}` missing completeness_check rule/on_missing"))

    consumed_required = {
        item["name"]
        for item in as_list(rp.meta.get("consumes"))
        if isinstance(item, dict)
        and item.get("kind") == "required_axis"
        and isinstance(item.get("name"), str)
    }

    for name in sorted(consumed_required - axis_names):
        findings.append(Finding("HARD", rp.relpath, f"meta consumes required_axis `{name}` but Required Axis YAML does not define it"))
    for name in sorted(axis_names - consumed_required):
        findings.append(Finding("SOFT", rp.relpath, f"Required Axis `{name}` is defined but not listed in meta consumes"))


def load_rp_files(skill_dir: Path, findings: list[Finding]) -> list[RpFile]:
    reasoning_dir = skill_dir / "reasoning"
    if not reasoning_dir.exists():
        return []
    if not reasoning_dir.is_dir():
        findings.append(Finding("HARD", "reasoning", "`reasoning` exists but is not a directory"))
        return []

    rp_files: list[RpFile] = []
    for path in sorted(reasoning_dir.rglob("*.md")):
        relpath = str(path.relative_to(skill_dir))
        text = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        if meta is None:
            findings.append(Finding("HARD", relpath, "missing or invalid YAML frontmatter"))
            continue
        rp = RpFile(path=path, relpath=relpath, meta=meta, body=body)
        validate_meta(rp, findings)
        validate_required_axis(rp, findings)
        rp_files.append(rp)
    return rp_files


def validate_graph(skill_dir: Path, rp_files: list[RpFile], findings: list[Finding]) -> dict[str, Any]:
    by_id: dict[str, RpFile] = {}
    produced_by: dict[str, list[str]] = {}
    consumed_by: dict[str, list[str]] = {}

    for rp in rp_files:
        rp_id = rp.meta.get("id")
        if not isinstance(rp_id, str):
            continue
        if rp_id in by_id:
            findings.append(Finding("HARD", rp.relpath, f"duplicate rp id `{rp_id}`"))
        by_id[rp_id] = rp
        for item in as_list(rp.meta.get("produces")):
            name = item_name(item)
            if name:
                produced_by.setdefault(name, []).append(rp_id)
        for item in as_list(rp.meta.get("consumes")):
            name = item_name(item)
            if name:
                consumed_by.setdefault(name, []).append(rp_id)

    skill_text = ""
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        skill_text = skill_md.read_text(encoding="utf-8")

    for rp in rp_files:
        rp_id = rp.meta.get("id")
        if not isinstance(rp_id, str):
            continue

        for item in as_list(rp.meta.get("consumes")):
            name = item_name(item)
            if not name:
                continue
            required = item.get("required", True) is not False
            source = item.get("source")
            if required and source == "upstream_rp" and name not in produced_by:
                findings.append(Finding("HARD", rp.relpath, f"required upstream consume `{name}` has no producer"))

        for downstream in as_list(rp.meta.get("downstream")):
            if isinstance(downstream, str) and downstream not in by_id:
                findings.append(Finding("HARD", rp.relpath, f"downstream rp `{downstream}` not found"))

        for variant in as_list(rp.meta.get("variants")):
            if not isinstance(variant, dict):
                findings.append(Finding("HARD", rp.relpath, "variant entry must be object"))
                continue
            variant_path = variant.get("path")
            if not isinstance(variant_path, str):
                findings.append(Finding("HARD", rp.relpath, "variant missing `path`"))
                continue
            target = rp.path.parent / variant_path
            if not target.is_file():
                findings.append(Finding("HARD", rp.relpath, f"variant path not found: {variant_path}"))

    for axis, producers in produced_by.items():
        is_consumed = axis in consumed_by
        mentioned_in_skill = axis in skill_text
        has_terminal = any(
            item_name(item) == axis and item.get("terminal") is True
            for rp_id in producers
            for item in as_list(by_id[rp_id].meta.get("produces"))
        )
        if not (is_consumed or mentioned_in_skill or has_terminal):
            findings.append(Finding("SOFT", ", ".join(producers), f"produced axis `{axis}` is not consumed downstream"))

    return {
        "rp_count": len(rp_files),
        "rp_ids": sorted(by_id.keys()),
        "axis_count": len(set(produced_by) | set(consumed_by)),
        "produced_axes": sorted(produced_by),
        "consumed_axes": sorted(consumed_by),
    }


def render_mermaid(rp_files: list[RpFile]) -> str:
    lines = ["flowchart LR"]
    declared: set[str] = set()

    def add_axis(axis: str) -> str:
        node_id = "A_" + sanitize_node_id(axis)
        if node_id not in declared:
            lines.append(f'  {node_id}(["{mermaid_label(axis)}"])')
            declared.add(node_id)
        return node_id

    def add_rp(rp_id: str, name: str, rp_type: str) -> str:
        node_id = "RP_" + sanitize_node_id(rp_id)
        if node_id not in declared:
            label = mermaid_label(name or rp_id)
            if rp_type == "polymorphism":
                lines.append(f'  {node_id}{{{{"{label}"}}}}')
            else:
                lines.append(f'  {node_id}["{label}"]')
            declared.add(node_id)
        return node_id

    for rp in rp_files:
        rp_id = str(rp.meta.get("id", rp.relpath))
        rp_node = add_rp(rp_id, str(rp.meta.get("name", rp_id)), str(rp.meta.get("rp_type", "")))

        for item in as_list(rp.meta.get("consumes")):
            name = item_name(item)
            if name:
                lines.append(f"  {add_axis(name)} --> {rp_node}")
        for item in as_list(rp.meta.get("produces")):
            name = item_name(item)
            if name:
                lines.append(f"  {rp_node} --> {add_axis(name)}")
        for downstream in as_list(rp.meta.get("downstream")):
            if isinstance(downstream, str):
                lines.append(f"  {rp_node} -. downstream .-> RP_{sanitize_node_id(downstream)}")
        for variant in as_list(rp.meta.get("variants")):
            if isinstance(variant, dict) and isinstance(variant.get("id"), str):
                variant_id = str(variant["id"])
                variant_node = add_rp(f"{rp_id}.{variant_id}", variant_id, "reasoning_phase")
                label = mermaid_label(str(variant.get("when", "variant")))
                lines.append(f'  {rp_node} -. "{label}" .-> {variant_node}')

    return "\n".join(lines) + "\n"


def try_render_svg(mmd_path: Path, svg_path: Path) -> str | None:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None
    result = subprocess.run(
        [mmdc, "-i", str(mmd_path), "-o", str(svg_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return "svg-rendered"
    return f"svg-render-failed: {result.stderr.strip() or result.stdout.strip()}"


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

    findings: list[Finding] = []
    rp_files = load_rp_files(skill_dir, findings)
    graph_summary = validate_graph(skill_dir, rp_files, findings) if rp_files else {
        "rp_count": 0,
        "rp_ids": [],
        "axis_count": 0,
        "produced_axes": [],
        "consumed_axes": [],
    }

    mmd_path = quality_dir / "reasoning-derivation-graph.mmd"
    svg_path = quality_dir / "reasoning-derivation-graph.svg"
    mmd_path.write_text(render_mermaid(rp_files), encoding="utf-8")
    svg_status = try_render_svg(mmd_path, svg_path)

    report = {
        "ok": not any(f.severity == "HARD" for f in findings),
        "skill_dir": str(skill_dir),
        "graph": graph_summary,
        "outputs": {
            "mermaid": str(mmd_path),
            "svg": str(svg_path) if svg_path.exists() else None,
            "svg_status": svg_status or "mmd-only",
        },
        "findings": [f.__dict__ for f in findings],
    }
    report_path = quality_dir / "reasoning-graph-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    hard = [f for f in findings if f.severity == "HARD"]
    soft = [f for f in findings if f.severity == "SOFT"]
    print(f"reasoning graph: {graph_summary['rp_count']} RP files, {graph_summary['axis_count']} axes")
    print(f"wrote: {mmd_path}")
    print(f"wrote: {report_path}")
    if svg_status:
        print(f"svg: {svg_status}")
    if hard or soft:
        for finding in findings:
            print(f"{finding.severity}: {finding.path}: {finding.message}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
