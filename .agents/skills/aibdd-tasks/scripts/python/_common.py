#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

FEATURE_TITLE_RE = re.compile(r"^\s*Feature:\s*(?P<title>.+?)\s*$", re.MULTILINE)
TASKS_FEATURE_CHANGE_TYPES = ("add", "update")


def emit(ok: bool, summary: str, violations: list[dict[str, Any]]) -> int:
    print(json.dumps({"ok": ok, "summary": summary, "violations": violations}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def violation(rule_id: str, file: str, msg: str, line: int | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"rule_id": rule_id, "file": file, "msg": msg}
    if line is not None:
        item["line"] = line
    return item


def workspace_root_from_args_path(args_path: Path) -> Path:
    if args_path.parent.name == ".aibdd":
        return args_path.parent.parent.resolve()
    return args_path.parent.resolve()


def repo_root_from_args_path(args_path: Path) -> Path:
    for parent in args_path.resolve().parents:
        if (parent / ".claude/skills/aibdd-core/scripts").is_dir():
            return parent
    return workspace_root_from_args_path(args_path)


def project_cwd(args_path: Path) -> Path:
    return workspace_root_from_args_path(args_path)


def ensure_shared_lib_on_path(workspace_root: Path) -> None:
    repo_root = workspace_root
    if not (repo_root / ".claude/skills/aibdd-core/scripts").is_dir():
        raise SystemExit(f"aibdd-core scripts not found under repo root: {repo_root}")
    scripts_dir = repo_root / ".claude/skills/aibdd-core/scripts"
    lib_dir = scripts_dir / "lib"
    for path in (lib_dir, scripts_dir):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def ensure_discovery_impact_matrix_on_path(workspace_root: Path) -> None:
    repo_root = workspace_root
    discovery_scripts = repo_root / ".claude/skills/aibdd-discovery/01-sourcing-and-packaging/scripts"
    if not discovery_scripts.is_dir():
        raise SystemExit(f"discovery impact-matrix scripts not found: {discovery_scripts}")
    scripts_str = str(discovery_scripts)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)


def resolve_key(key: str, *, cwd: Path, args_path: Path) -> str | None:
    ensure_shared_lib_on_path(repo_root_from_args_path(args_path))
    from shared.project_args import resolve_key as core_resolve_key

    return core_resolve_key(key, cwd=cwd)


def plan_package_override(cli_value: str | None = None) -> str | None:
    if cli_value:
        return cli_value
    env_value = os.environ.get("AIBDD_PLAN_PACKAGE", "").strip()
    return env_value or None


def resolve_plan_package(*, args_path: Path, plan_package: str | None = None) -> Path:
    cwd = project_cwd(args_path)
    override = plan_package_override(plan_package)
    if override:
        pkg = Path(override)
        if not pkg.is_absolute():
            pkg = cwd / pkg
        return pkg.resolve()

    resolved = resolve_key("CURRENT_PLAN_PACKAGE", cwd=cwd, args_path=args_path)
    if resolved:
        pkg = Path(resolved)
        if not pkg.is_absolute():
            pkg = cwd / pkg
        return pkg.resolve()

    raise SystemExit(
        "CURRENT_PLAN_PACKAGE unresolved: provide --plan-package or concrete .aibdd/arguments.yml"
    )


def resolve_truth_boundary_root(*, args_path: Path) -> Path:
    cwd = project_cwd(args_path)
    resolved = resolve_key("TRUTH_BOUNDARY_ROOT", cwd=cwd, args_path=args_path) or resolve_key(
        "SPECS_ROOT_DIR", cwd=cwd, args_path=args_path
    )
    if not resolved:
        raise SystemExit("TRUTH_BOUNDARY_ROOT unresolved")
    root = Path(resolved)
    if not root.is_absolute():
        root = cwd / root
    return root.resolve()


def resolve_boundary_map(*, args_path: Path) -> Path:
    cwd = project_cwd(args_path)
    resolved = resolve_key("BOUNDARY_MAP_FILE", cwd=cwd, args_path=args_path)
    if resolved:
        path = Path(resolved)
        if not path.is_absolute():
            path = cwd / path
        return path.resolve()
    return resolve_truth_boundary_root(args_path=args_path) / "boundary-map.yml"


def resolve_tasks_paths_bundle(*, args_path: Path, plan_package: str | None = None) -> dict[str, str]:
    cwd = project_cwd(args_path)
    plan_pkg = resolve_plan_package(args_path=args_path, plan_package=plan_package)
    truth_root = resolve_truth_boundary_root(args_path=args_path)

    resolved_plan_md = resolve_key("PLAN_MD", cwd=cwd, args_path=args_path)
    plan_md = Path(resolved_plan_md) if resolved_plan_md else plan_pkg / "plan.md"
    if not plan_md.is_absolute():
        plan_md = cwd / plan_md

    resolved_internal = resolve_key("PLAN_INTERNAL_STRUCTURE", cwd=cwd, args_path=args_path)
    internal_structure = (
        Path(resolved_internal)
        if resolved_internal
        else plan_pkg / "implementation" / "internal-structure.class.mmd"
    )
    if not internal_structure.is_absolute():
        internal_structure = cwd / internal_structure

    resolved_reports = resolve_key("PLAN_REPORTS_DIR", cwd=cwd, args_path=args_path)
    plan_reports_dir = Path(resolved_reports) if resolved_reports else plan_pkg / "reports"
    if not plan_reports_dir.is_absolute():
        plan_reports_dir = cwd / plan_reports_dir

    resolved_matrix = resolve_key("IMPACT_MATRIX_YML", cwd=cwd, args_path=args_path)
    impact_matrix = Path(resolved_matrix) if resolved_matrix else plan_reports_dir / "impact-matrix.yml"
    if not impact_matrix.is_absolute():
        impact_matrix = cwd / impact_matrix

    resolved_packages_dir = resolve_key("TRUTH_BOUNDARY_PACKAGES_DIR", cwd=cwd, args_path=args_path)
    packages_dir = (
        Path(resolved_packages_dir) if resolved_packages_dir else truth_root / "packages"
    )
    if not packages_dir.is_absolute():
        packages_dir = cwd / packages_dir

    implementation_dir = resolve_key("PLAN_IMPLEMENTATION_DIR", cwd=cwd, args_path=args_path)
    plan_implementation = (
        Path(implementation_dir) if implementation_dir else plan_pkg / "implementation"
    )
    if not plan_implementation.is_absolute():
        plan_implementation = cwd / plan_implementation

    matrix_feature_paths = query_impacted_feature_paths(
        impact_matrix,
        repo_root=repo_root_from_args_path(args_path),
    )
    return {
        "arguments_path": str(args_path.resolve()),
        "current_plan_package": str(plan_pkg),
        "plan_md": str(plan_md.resolve()),
        "research_md": str((plan_pkg / "research.md").resolve()),
        "plan_internal_structure": str(internal_structure.resolve()),
        "plan_implementation_dir": str(plan_implementation.resolve()),
        "plan_reports_dir": str(plan_reports_dir.resolve()),
        "impact_matrix_yml": str(impact_matrix.resolve()),
        "truth_boundary_root": str(truth_root),
        "truth_boundary_packages_dir": str(packages_dir.resolve()),
        "boundary_map": str(resolve_boundary_map(args_path=args_path)),
        "tasks_md": str((plan_pkg / "tasks.md").resolve()),
        "project_spec_language": resolve_key("PROJECT_SPEC_LANGUAGE", cwd=cwd, args_path=args_path) or "",
        "matrix_feature_paths": matrix_feature_paths,
    }


def query_impacted_feature_paths(matrix_path: Path, *, repo_root: Path) -> list[str]:
    if not matrix_path.is_file():
        raise SystemExit(f"impact matrix not found: {matrix_path}")

    ensure_discovery_impact_matrix_on_path(repo_root)
    from lib.impact_matrix import filter_entries, load_matrix

    data = load_matrix(matrix_path)
    entries = filter_entries(
        data,
        suffix=".feature",
        change_types=list(TASKS_FEATURE_CHANGE_TYPES),
    )
    return sorted(entry["path"] for entry in entries)


def parse_feature_paths(raw: str | None) -> list[str]:
    if not raw:
        return []
    text = raw.strip()
    if not text:
        return []
    if text.startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise SystemExit("--feature-paths JSON must be an array")
        return [str(item) for item in parsed]
    return [part.strip() for part in text.split(",") if part.strip()]


def validate_feature_paths_membership(
    ordered_paths: list[str],
    matrix_paths: list[str],
) -> None:
    if not ordered_paths:
        raise SystemExit("feature paths must be non-empty")
    if set(ordered_paths) != set(matrix_paths):
        raise SystemExit(
            "feature paths must match impact matrix membership exactly: "
            f"ordered={ordered_paths}, matrix={matrix_paths}"
        )
    if len(ordered_paths) != len(set(ordered_paths)):
        raise SystemExit(f"duplicate feature paths in order list: {ordered_paths}")


def feature_file_path(feature_rel_path: str, *, truth_boundary_root: Path) -> Path:
    return (truth_boundary_root / feature_rel_path).resolve()


def feature_title(text: str) -> str:
    match = FEATURE_TITLE_RE.search(text)
    if match:
        return match.group("title").strip()
    return ""


def basename_no_suffix(path: str) -> str:
    return Path(path).stem


def add_tasks_cli_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("arguments_yml", type=Path, help="Path to .aibdd/arguments.yml")
    parser.add_argument(
        "--plan-package",
        default=None,
        help="Concrete plan package path when CURRENT_PLAN_PACKAGE is still a slot",
    )
    parser.add_argument(
        "--feature-paths",
        default=None,
        help="Ordered feature path list as JSON array or comma-separated values",
    )


def load_tasks_context(args: argparse.Namespace) -> dict[str, Any]:
    args_path = args.arguments_yml.resolve()
    if not args_path.is_file():
        raise SystemExit(f"arguments file not found: {args_path}")
    bundle = resolve_tasks_paths_bundle(args_path=args_path, plan_package=args.plan_package)
    ordered_paths = parse_feature_paths(args.feature_paths)
    matrix_paths = bundle["matrix_feature_paths"]
    if ordered_paths:
        validate_feature_paths_membership(ordered_paths, matrix_paths)
    else:
        ordered_paths = list(matrix_paths)
    bundle["ordered_feature_paths"] = ordered_paths
    bundle["args_path"] = args_path
    return bundle
