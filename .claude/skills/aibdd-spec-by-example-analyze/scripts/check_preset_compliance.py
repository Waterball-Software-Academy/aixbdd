#!/usr/bin/env python3
"""
check_preset_compliance.py — BDD Analysis Quality Gate 5a

Validates Gherkin steps against canonical L1 patterns from `/aibdd-plan`
DSL registries (package + shared). Only supported invocation:

  python check_preset_compliance.py --args .aibdd/arguments.yml
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

STEP_RE = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s+(.+?)\s*$", re.IGNORECASE)
TABLE_ROW_RE = re.compile(r"^\s*\|")
DOCSTRING_RE = re.compile(r'^\s*"""')
FEATURE_RE = re.compile(r"^\s*Feature\s*:", re.IGNORECASE)
BACKGROUND_RE = re.compile(r"^\s*Background\s*:", re.IGNORECASE)
RULE_RE = re.compile(r"^\s*Rule\s*:", re.IGNORECASE)
SCENARIO_RE = re.compile(r"^\s*(Scenario Outline|Scenario|Example|Examples)\s*:", re.IGNORECASE)

_SLOT = "\u27e8\u27e9"
_SLOT_RE = re.compile(
    r'"[^"]*"'
    r"|'[^']*'"
    r"|\u300c[^\u300d]*\u300d"
    r"|<[^<>]+>"
    r"|\{[^{}]+\}"
    r"|\$[A-Za-z0-9_\u4e00-\u9fff]+(?:\.[A-Za-z0-9_\u4e00-\u9fff]+)*"
    r"|\d+(?:\.\d+)?"
)


def _violation(rule_id: str, file: str, line: int, msg: str) -> dict:
    return {"rule_id": rule_id, "file": file, "line": line, "msg": msg}


def canonicalize(body: str) -> str:
    return re.sub(r"\s+", " ", _SLOT_RE.sub(_SLOT, body)).strip()


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
        err = {
            "ok": False,
            "summary": {"violations": 1},
            "violations": [
                _violation("PLAN_RESOLVER_FAILED", str(args_path), 0, proc.stderr.strip() or proc.stdout.strip())
            ],
        }
        print(json.dumps(err, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    return json.loads(proc.stdout)


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"PyYAML required: {exc}") from exc
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _collect_dsl_l1_patterns(paths: dict) -> tuple[set[str], list[dict]]:
    """Return canonicalized L1 step patterns from plan-owned package/shared DSL."""
    patterns: set[str] = set()
    violations: list[dict] = []
    dsl_files = [Path(paths["boundary_package_dsl"])]
    shared = Path(paths.get("boundary_shared_dsl") or "")
    if shared.exists():
        dsl_files.append(shared)
    for dsl in dsl_files:
        raw = _load_yaml(dsl) or {}
        entries = raw.get("entries") if isinstance(raw, dict) else None
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            l4 = entry.get("L4") or {}
            preset = ((l4.get("preset") or {}).get("name") if isinstance(l4.get("preset"), dict) else None)
            if not preset:
                violations.append(_violation("DSL_PRESET_MISSING", str(dsl), 0, f"entry {entry.get('id')} missing L4.preset.name"))
                continue
            l1 = entry.get("L1")
            if not isinstance(l1, dict):
                violations.append(_violation("DSL_L1_MISSING", str(dsl), 0, f"entry {entry.get('id')} missing L1 mapping"))
                continue
            for key in ("given", "when"):
                body = l1.get(key)
                if body is None:
                    continue
                if isinstance(body, list):
                    for item in body:
                        if item:
                            patterns.add(canonicalize(str(item)))
                else:
                    patterns.add(canonicalize(str(body)))
            then = l1.get("then")
            if isinstance(then, list):
                for body in then:
                    if body:
                        patterns.add(canonicalize(str(body)))
            elif then:
                patterns.add(canonicalize(str(then)))
    return patterns, violations


def extract_feature_steps(path: Path) -> tuple[list[tuple[int, str]], list[dict]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [], [_violation("FILE_READ_ERROR", str(path), 0, f"cannot read: {e}")]

    steps: list[tuple[int, str]] = []
    in_docstring = False
    for i, raw in enumerate(text.splitlines(), start=1):
        if in_docstring:
            if DOCSTRING_RE.match(raw):
                in_docstring = False
            continue
        if DOCSTRING_RE.match(raw):
            in_docstring = True
            continue
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip() or TABLE_ROW_RE.match(line):
            continue
        if FEATURE_RE.search(line) or BACKGROUND_RE.search(line) or RULE_RE.search(line) or SCENARIO_RE.search(line):
            continue
        m = STEP_RE.match(line)
        if m:
            steps.append((i, m.group(2).strip()))
    return steps, []


def main() -> int:
    p = argparse.ArgumentParser(description="Validate feature steps against plan DSL L1 patterns")
    p.add_argument("--args", dest="args_path", required=True, help="arguments.yml; resolves /aibdd-plan output paths")
    args = p.parse_args()

    violations: list[dict] = []
    args_path = Path(args.args_path).resolve()
    paths = _resolve_plan_paths(args_path)
    features = Path(paths["features_dir"])
    dsl_allowed_patterns, dsl_vs = _collect_dsl_l1_patterns(paths)
    violations.extend(dsl_vs)

    summary = {
        "features_dir": str(features),
        "dsl_l1_patterns": len(dsl_allowed_patterns or set()),
        "features_scanned": 0,
        "steps_total": 0,
        "steps_matched": 0,
        "violations": 0,
    }

    if not features.exists():
        violations.append(_violation("FEATURES_DIR_MISSING", str(features), 0, f"features dir not found: {features}"))

    if not dsl_allowed_patterns:
        violations.append(_violation("DSL_L1_PATTERNS_EMPTY", str(args_path), 0, "plan DSL yielded 0 L1 step patterns"))

    if violations:
        summary["violations"] = len(violations)
        print(json.dumps({"ok": False, "summary": summary, "violations": violations}, ensure_ascii=False, indent=2))
        return 1

    allowed = dsl_allowed_patterns
    for f in sorted(features.rglob("*.feature")):
        summary["features_scanned"] += 1
        steps, step_vs = extract_feature_steps(f)
        violations.extend(step_vs)
        for line, body in steps:
            summary["steps_total"] += 1
            if canonicalize(body) in allowed:
                summary["steps_matched"] += 1
            else:
                violations.append(
                    _violation("STEP_NOT_IN_PLAN_DSL", str(f), line, f"step does not match any plan DSL L1 pattern: {body!r}")
                )

    summary["violations"] = len(violations)
    result = {"ok": len(violations) == 0, "summary": summary, "violations": violations}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
