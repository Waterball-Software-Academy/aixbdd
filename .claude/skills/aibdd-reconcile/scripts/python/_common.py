#!/usr/bin/env python3
"""Shared helpers for /aibdd-reconcile scripts."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE_ORDER = [
    "aibdd-discovery",
    "aibdd-plan",
    "aibdd-spec-by-example-analyze",
]
PHASE_INDEX = {name: index for index, name in enumerate(PHASE_ORDER)}
VAR_RE = re.compile(r"\$\{([^}]+)\}")
PACKAGE_NAME_RE = re.compile(r"^\d+-")


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"PyYAML is required to parse {path}: {exc}")
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return None
    return yaml.safe_load(text)


def read_args(args_path: Path) -> dict[str, str]:
    raw = _load_yaml(args_path)
    if not isinstance(raw, dict):
        raise SystemExit(f"arguments file must be a YAML mapping: {args_path}")
    return {str(k): "" if v is None else str(v) for k, v in raw.items()}


def expand_vars(value: str, mapping: dict[str, str], limit: int = 10) -> str:
    result = value
    for _ in range(limit):
        replaced = VAR_RE.sub(lambda m: mapping.get(m.group(1), m.group(0)), result)
        if replaced == result:
            return result
        result = replaced
    return result


def workspace_root(args_path: Path) -> Path:
    return args_path.parent.parent if args_path.parent.name == ".aibdd" else args_path.parent


def load_boundary_id(args_path: Path, args: dict[str, str]) -> str | None:
    boundary_rel = expand_vars(args.get("BOUNDARY_YML", ""), args)
    if not boundary_rel:
        return None
    boundary_path = Path(boundary_rel)
    if not boundary_path.is_absolute():
        boundary_path = workspace_root(args_path) / boundary_path
    boundary_path = boundary_path.resolve()
    if not boundary_path.is_file():
        return None
    raw = _load_yaml(boundary_path) or {}
    boundaries = raw.get("boundaries") if isinstance(raw, dict) else None
    if not isinstance(boundaries, list) or not boundaries:
        return None
    bid = str(boundaries[0].get("id") or "").strip()
    return bid or None


def specs_root(args_path: Path, args: dict[str, str]) -> Path:
    root = expand_vars(args.get("SPECS_ROOT_DIR", "specs"), args)
    boundary_id = load_boundary_id(args_path, args)
    if boundary_id:
        root = root.replace("<boundary>", boundary_id)
    root_path = Path(root)
    if not root_path.is_absolute():
        root_path = workspace_root(args_path) / root_path
    return root_path.resolve()


def assert_inside(base: Path, target: Path) -> None:
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise SystemExit(f"path escapes sandbox: {target}") from exc


def normalize_plan_package(args_path: Path, raw_path: str) -> Path:
    if not raw_path:
        raise SystemExit("plan package path is required")
    args = read_args(args_path)
    specs = specs_root(args_path, args)
    package = Path(raw_path)
    if not package.is_absolute():
        package = workspace_root(args_path) / package
    package = package.resolve()
    assert_inside(specs, package)
    if not package.is_dir():
        raise SystemExit(f"plan package must be an existing directory: {package}")
    if not PACKAGE_NAME_RE.match(package.name):
        raise SystemExit(f"plan package basename must start with numeric prefix: {package.name}")
    return package


def derive_paths(target_plan_package: Path) -> dict[str, Path]:
    archive_dir = target_plan_package / "archive"
    return {
        "archive_dir": archive_dir,
        "active_session_path": archive_dir / ".reconcile-active.json",
        "record_path": target_plan_package / "RECONCILE_RECORD.md",
    }


def utc_session_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def derive_cascade_chain(earliest: str) -> list[str]:
    if earliest not in PHASE_INDEX:
        raise SystemExit(f"unsupported earliest planner: {earliest}")
    return PHASE_ORDER[PHASE_INDEX[earliest] :]


def phase_is_more_upstream(lhs: str, rhs: str) -> bool:
    return PHASE_INDEX[lhs] < PHASE_INDEX[rhs]


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def list_entries_to_archive(target_plan_package: Path) -> list[Path]:
    entries = []
    for child in sorted(target_plan_package.iterdir(), key=lambda p: p.name):
        if child.name == "archive":
            continue
        entries.append(child)
    return entries


def execute_archive(target_plan_package: Path, session_id: str) -> tuple[Path, list[str]]:
    paths = derive_paths(target_plan_package)
    archive_path = paths["archive_dir"] / session_id
    archive_path.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []
    for entry in list_entries_to_archive(target_plan_package):
        destination = archive_path / entry.name
        if destination.exists():
            raise SystemExit(f"archive destination already exists: {destination}")
        shutil.move(str(entry), str(destination))
        moved.append(str(entry))
    return archive_path, moved


def final_session_path(active_session_path: Path, session_id: str) -> Path:
    return active_session_path.parent / session_id / "RECONCILE_SESSION.json"


def render_record(session: dict[str, Any]) -> str:
    target = session.get("target_plan_package", "")
    archive_path = session.get("archive_path", "")
    chain = session.get("cascade_chain") or []
    chain_text = " -> ".join(chain) if chain else "(none)"
    session_lines = [
        f"- `session_id`: `{session.get('session_id', '')}`",
        f"- `status`: `{session.get('status', '')}`",
        f"- `archive_path`: `{archive_path}`",
        f"- `earliest_planner`: `{session.get('earliest_planner', '')}`",
        f"- `replay_from`: `{session.get('replay_from', '')}`",
        f"- `current_pointer`: `{session.get('current_pointer', '')}`",
    ]
    trigger_lines = [
        f"- `{item.get('at', '')}` [{item.get('kind', '')}] {item.get('text', '')}"
        for item in session.get("triggers") or []
    ]
    if not trigger_lines:
        trigger_lines = ["- (none)"]
    event_lines = []
    for item in session.get("events") or []:
        summary_bits = [item.get("type", "event")]
        if item.get("earliest_planner"):
            summary_bits.append(f"earliest={item['earliest_planner']}")
        if item.get("replay_from"):
            summary_bits.append(f"replay_from={item['replay_from']}")
        if item.get("current_pointer"):
            summary_bits.append(f"current_pointer={item['current_pointer']}")
        event_lines.append(f"- `{item.get('at', '')}` " + ", ".join(summary_bits))
    if not event_lines:
        event_lines = ["- (none)"]
    mode = session.get("mode", "start_new")
    cascade_note = (
        "merged into in-flight session; no new archive created"
        if mode == "merge_existing"
        else "started a new archive snapshot before cascading planners"
    )
    return "\n".join(
        [
            "# Reconcile Session",
            "",
            "> Generated by `/aibdd-reconcile`. This file is the human-readable projection of one reconcile session.",
            "",
            "## Target",
            "",
            f"`{target}`",
            "",
            "## Session",
            "",
            *session_lines,
            "",
            "## Trigger History",
            "",
            *trigger_lines,
            "",
            "## Cascade",
            "",
            f"- chain: `{chain_text}`",
            f"- note: {cascade_note}",
            "",
            "## Event Log",
            "",
            *event_lines,
            "",
        ]
    )


def relative_to_workspace(args_path: Path, path: Path) -> str:
    root = workspace_root(args_path)
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path.resolve())
