#!/usr/bin/env python3
"""
check_example_coverage.py — BDD Analysis Quality Gate 5a

Validates package-level example coverage after /aibdd-spec-by-example-analyze.
Preferred usage reads /aibdd-plan output paths from arguments.yml:

  python check_example_coverage.py --args .aibdd/arguments.yml

Legacy explicit path mode remains available:

  python check_example_coverage.py <SPECS_ROOT_DIR> \\
      --features-dir backend/packages/01-order-checkout/features \\
      --coverage-dir backend/packages/01-order-checkout/coverage
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RULE_RE = re.compile(r"^\s*Rule\s*:\s*(.+?)\s*$", re.IGNORECASE)
FEATURE_RE = re.compile(r"^\s*Feature\s*:", re.IGNORECASE)
SCENARIO_RE = re.compile(
    r"^\s*(Scenario Outline|Scenario|Example)\s*:",
    re.IGNORECASE,
)
EXAMPLES_RE = re.compile(r"^\s*Examples\s*:", re.IGNORECASE)
TAG_LINE_RE = re.compile(r"^\s*@\S+")
IGNORE_TAG_RE = re.compile(r"@ignore\b")
TABLE_ROW_RE = re.compile(r"^\s*\|")

REQUIRED_EXAMPLE_FIELDS = ("rule_id", "dimension", "example_id", "coverage_type")


def _violation(rule_id: str, file: str, line: int, msg: str) -> dict:
    return {"rule_id": rule_id, "file": file, "line": line, "msg": msg}


def _slug_rule(title: str) -> str:
    body = re.sub(r"^\s*Rule\s*:\s*", "", title).strip()
    body = re.sub(r"\s+", "-", body)
    body = re.sub(r"[^\w\-\u4e00-\u9fff（）()：:]+", "", body)
    return body[:120] or "rule"


def _workspace_root() -> Path:
    skill_dir = Path(__file__).resolve().parent.parent
    return skill_dir.parents[2]


def _resolve_plan_paths(args_path: Path) -> dict:
    resolver = (
        _workspace_root()
        / ".claude"
        / "skills"
        / "aibdd-plan"
        / "scripts"
        / "python"
        / "resolve_plan_paths.py"
    )
    proc = subprocess.run(
        [sys.executable, str(resolver), str(args_path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "ok": False,
                    "summary": {"violations": 1},
                    "violations": [
                        _violation(
                            "PLAN_RESOLVER_FAILED",
                            str(args_path),
                            0,
                            proc.stderr.strip() or proc.stdout.strip(),
                        )
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return json.loads(proc.stdout)


def _paths_from_args(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.args_path:
        paths = _resolve_plan_paths(Path(args.args_path).resolve())
        features = Path(paths["features_dir"])
        coverage = Path(paths["truth_function_package"]) / "coverage"
        root = Path(paths["specs_root"])
        return root, features, coverage

    if not args.specs_root:
        raise SystemExit("specs_root is required unless --args is provided")
    root = Path(args.specs_root).resolve()
    features = (root / args.features_dir).resolve()
    coverage = (root / args.coverage_dir).resolve()
    return root, features, coverage


def parse_feature(path: Path) -> tuple[list[dict], bool, list[dict]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [], False, [_violation(
            "FILE_READ_ERROR", str(path), 0, f"cannot read: {e}",
        )]

    rule_blocks: list[dict] = []
    current_rule: dict | None = None
    pre_feature_tags: list[str] = []
    seen_feature = False
    has_ignore = False
    outline_target_idx: int | None = None
    in_examples_section = False

    for i, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue

        if not seen_feature and TAG_LINE_RE.match(stripped):
            pre_feature_tags.append(stripped.strip())
            continue

        if FEATURE_RE.search(stripped):
            seen_feature = True
            has_ignore = any(IGNORE_TAG_RE.search(tag) for tag in pre_feature_tags)
            pre_feature_tags = []
            continue

        m_rule = RULE_RE.search(stripped)
        if m_rule:
            current_rule = {
                "rule_line": i,
                "rule_title": stripped.strip(),
                "rule_id": _slug_rule(stripped),
                "scenarios": [],
            }
            rule_blocks.append(current_rule)
            outline_target_idx = None
            in_examples_section = False
            continue

        m = SCENARIO_RE.search(stripped)
        if m:
            kind_raw = m.group(1).lower()
            kind = "Outline" if "outline" in kind_raw else ("Example" if kind_raw == "example" else "Scenario")
            entry = {"line": i, "title": stripped.strip(), "kind": kind, "examples_rows": 0}
            if current_rule is not None:
                current_rule["scenarios"].append(entry)
                outline_target_idx = len(current_rule["scenarios"]) - 1 if kind == "Outline" else None
            else:
                outline_target_idx = None
            in_examples_section = False
            continue

        if EXAMPLES_RE.search(stripped):
            in_examples_section = True
            continue

        if in_examples_section and TABLE_ROW_RE.match(stripped):
            if current_rule is not None and outline_target_idx is not None:
                current_rule["scenarios"][outline_target_idx]["examples_rows"] += 1
            continue

        if in_examples_section and stripped.strip() and not TABLE_ROW_RE.match(stripped):
            in_examples_section = False

    return rule_blocks, has_ignore, []


def check_feature_file(path: Path) -> tuple[list[dict], set[str]]:
    violations: list[dict] = []
    rule_ids: set[str] = set()
    rule_blocks, has_ignore, read_errors = parse_feature(path)
    if read_errors:
        return read_errors, rule_ids

    if has_ignore:
        violations.append(_violation(
            "BDD_FEATURE_HAS_IGNORE", str(path), 0,
            "@ignore tag must be removed at BDD Analysis stage",
        ))

    for rule in rule_blocks:
        rule_ids.add(rule["rule_id"])
        if not rule["scenarios"]:
            violations.append(_violation(
                "BDD_RULE_NO_EXAMPLE", str(path), rule["rule_line"],
                f"Rule '{rule['rule_title']}' has no Scenario / Scenario Outline / Example",
            ))
            continue
        for scen in rule["scenarios"]:
            if scen["kind"] == "Outline" and scen["examples_rows"] < 2:
                violations.append(_violation(
                    "BDD_OUTLINE_EMPTY_EXAMPLES", str(path), scen["line"],
                    f"Scenario Outline '{scen['title']}' needs header + at least one data row",
                ))
    return violations, rule_ids


def load_coverage_entries(cov_dir: Path) -> tuple[list[dict], list[dict]]:
    if not cov_dir.exists():
        return [], []
    try:
        import yaml
    except ImportError:
        return [], [_violation("YAML_IMPORT_ERROR", str(cov_dir), 0, "PyYAML not installed")]

    entries: list[dict] = []
    violations: list[dict] = []
    for f in sorted(cov_dir.glob("*.coverage.yml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as e:
            violations.append(_violation("FILE_READ_ERROR", str(f), 0, f"cannot read: {e}"))
            continue
        except yaml.YAMLError as e:
            mark = getattr(e, "problem_mark", None)
            line = (mark.line + 1) if mark is not None else 0
            violations.append(_violation("YAML_PARSE_ERROR", str(f), line, f"invalid yaml: {e}"))
            continue
        if not isinstance(data, dict) or not isinstance(data.get("coverage"), list):
            violations.append(_violation("COVERAGE_INVALID_TOP_LEVEL", str(f), 0, "coverage file must contain list key 'coverage'"))
            continue
        for idx, entry in enumerate(data["coverage"]):
            if not isinstance(entry, dict):
                violations.append(_violation("COVERAGE_ENTRY_NOT_MAPPING", str(f), 0, f"entry #{idx} is not a mapping"))
                continue
            entries.append({"_source": str(f), "_index": idx, **entry})
    return entries, violations


def main() -> int:
    p = argparse.ArgumentParser(description="Validate BDD-stage package example coverage")
    p.add_argument("specs_root", nargs="?", help="${SPECS_ROOT_DIR}; optional when --args is provided")
    p.add_argument("--args", dest="args_path", default=None, help="arguments.yml; resolves /aibdd-plan output paths")
    p.add_argument("--features-dir", default="features")
    p.add_argument("--coverage-dir", default="coverage")
    args = p.parse_args()

    _, features, cov_dir = _paths_from_args(args)
    violations: list[dict] = []
    summary = {
        "features_dir": str(features),
        "coverage_dir": str(cov_dir),
        "features_scanned": 0,
        "rules": 0,
        "scenarios": 0,
        "coverage_files": 0,
        "example_entries": 0,
        "violations": 0,
    }

    if not features.exists():
        violations.append(_violation("FEATURES_DIR_MISSING", str(features), 0, f"features dir not found: {features}"))
    if violations:
        summary["violations"] = len(violations)
        print(json.dumps({"ok": False, "summary": summary, "violations": violations}, ensure_ascii=False, indent=2))
        return 1

    feature_rule_ids: set[str] = set()
    for f in sorted(features.rglob("*.feature")):
        summary["features_scanned"] += 1
        rule_blocks, _, _ = parse_feature(f)
        summary["rules"] += len(rule_blocks)
        summary["scenarios"] += sum(len(rule["scenarios"]) for rule in rule_blocks)
        file_vs, ids = check_feature_file(f)
        violations.extend(file_vs)
        feature_rule_ids.update(ids)

    entries, load_vs = load_coverage_entries(cov_dir)
    violations.extend(load_vs)
    summary["coverage_files"] = len(sorted(cov_dir.glob("*.coverage.yml"))) if cov_dir.exists() else 0

    example_layer_ids: set[str] = set()
    seen_example_keys: dict[str, str] = {}
    for entry in entries:
        src = entry.get("_source", "<unknown>")
        idx = entry.get("_index", 0)
        if entry.get("coverage_type") != "example":
            continue
        summary["example_entries"] += 1
        for fld in REQUIRED_EXAMPLE_FIELDS:
            if fld not in entry or entry.get(fld) in (None, ""):
                violations.append(_violation("COVERAGE_EXAMPLE_MISSING_FIELD", src, 0, f"entry #{idx} missing '{fld}'"))
        if not (entry.get("spec_file") or entry.get("feature_path")):
            violations.append(_violation("COVERAGE_EXAMPLE_MISSING_FIELD", src, 0, f"entry #{idx} missing 'spec_file' or 'feature_path'"))
        rid = entry.get("rule_id")
        eid = entry.get("example_id")
        if isinstance(rid, str) and rid:
            example_layer_ids.add(rid)
        if isinstance(rid, str) and rid and isinstance(eid, str) and eid:
            key = f"{rid}::{eid}"
            if key in seen_example_keys:
                violations.append(_violation("COVERAGE_DUPLICATE_EXAMPLE_ID", src, 0, f"duplicate example_id '{eid}' for rule_id '{rid}'"))
            else:
                seen_example_keys[key] = src

    for rid in sorted(example_layer_ids - feature_rule_ids):
        violations.append(_violation(
            "COVERAGE_EXAMPLE_ORPHAN_RULE_ID",
            str(cov_dir),
            0,
            f"rule_id '{rid}' does not match any atomic Rule anchor in feature files",
        ))

    summary["violations"] = len(violations)
    result = {"ok": len(violations) == 0, "summary": summary, "violations": violations}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
