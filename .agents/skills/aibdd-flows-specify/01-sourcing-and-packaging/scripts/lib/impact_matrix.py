"""Impact matrix core: load, validate, CRUD, and entry query."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}") from exc

SCHEMA_VERSION = 1

CHANGE_TYPES: tuple[str, ...] = (
    "read_only_compare",
    "update",
    "add",
    "conditional_update",
)

CHANGE_TYPE_SET = frozenset(CHANGE_TYPES)

GLOB_MARKERS = ("*", "?", "[", "]")


@dataclass(frozen=True)
class MatrixQuestion:
    where: str
    type: str
    text: str

    def as_dict(self) -> dict[str, str]:
        return {"where": self.where, "type": self.type, "text": self.text}


def repo_root_from_module() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    return here.parents[4]


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "impact-matrix.schema.yml"


def empty_matrix() -> dict[str, Any]:
    return {"version": SCHEMA_VERSION, "entries": []}


def _normalize_path(path: str) -> str:
    cleaned = path.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def _looks_like_glob(path: str) -> bool:
    return any(marker in path for marker in GLOB_MARKERS)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"impact matrix not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"impact matrix must be a mapping: {path}")
    return raw


def _dump_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _entry_index(entries: list[dict[str, Any]], path: str) -> int | None:
    normalized = _normalize_path(path)
    for idx, entry in enumerate(entries):
        if _normalize_path(str(entry.get("path", ""))) == normalized:
            return idx
    return None


def validate_matrix(
    data: dict[str, Any],
    *,
    matrix_path: str = "impact-matrix.yml",
) -> tuple[list[MatrixQuestion], list[str]]:
    questions: list[MatrixQuestion] = []
    warnings: list[str] = []

    version = data.get("version")
    if version != SCHEMA_VERSION:
        questions.append(
            MatrixQuestion(
                where=matrix_path,
                type="version",
                text=f"version must be {SCHEMA_VERSION}, got {version!r}",
            )
        )

    entries = data.get("entries")
    if not isinstance(entries, list):
        questions.append(
            MatrixQuestion(
                where=matrix_path,
                type="entries",
                text="entries must be a list",
            )
        )
        return questions, warnings

    seen_paths: set[str] = set()
    for idx, entry in enumerate(entries):
        entry_where = f"{matrix_path}:entries[{idx}]"
        if not isinstance(entry, dict):
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="entry",
                    text="entry must be a mapping",
                )
            )
            continue

        path = entry.get("path")
        change_type = entry.get("change_type")
        impact_summary = entry.get("impact_summary")

        if not isinstance(path, str) or not path.strip():
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="path",
                    text="path is required and must be a non-empty string",
                )
            )
            continue

        normalized_path = _normalize_path(path)
        if _looks_like_glob(normalized_path):
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="path",
                    text=(
                        f"path `{normalized_path}` contains glob markers; "
                        "impact-matrix.yml v1 requires explicit per-file paths"
                    ),
                )
            )

        if normalized_path in seen_paths:
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="path",
                    text=f"duplicate path `{normalized_path}`",
                )
            )
        seen_paths.add(normalized_path)

        if change_type not in CHANGE_TYPE_SET:
            allowed = ", ".join(CHANGE_TYPES)
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="change_type",
                    text=(
                        f"change_type {change_type!r} is invalid; "
                        f"must be one of: {allowed}"
                    ),
                )
            )

        if not isinstance(impact_summary, str) or not impact_summary.strip():
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="impact_summary",
                    text="impact_summary is required and must be a non-empty string",
                )
            )

        extra_keys = set(entry.keys()) - {"path", "change_type", "impact_summary"}
        if extra_keys:
            questions.append(
                MatrixQuestion(
                    where=entry_where,
                    type="entry",
                    text=f"unexpected fields: {sorted(extra_keys)}",
                )
            )

    return questions, warnings


def load_matrix(path: Path) -> dict[str, Any]:
    return _load_yaml(path)


def init_matrix(path: Path) -> dict[str, Any]:
    data = empty_matrix()
    _dump_yaml(path, data)
    return data


def list_entries(data: dict[str, Any]) -> list[dict[str, str]]:
    entries = data.get("entries", [])
    result: list[dict[str, str]] = []
    if not isinstance(entries, list):
        return result
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        result.append(
            {
                "path": _normalize_path(str(entry.get("path", ""))),
                "change_type": str(entry.get("change_type", "")),
                "impact_summary": str(entry.get("impact_summary", "")),
            }
        )
    return result


def upsert_entry(
    path: Path,
    *,
    entry_path: str,
    change_type: str,
    impact_summary: str,
) -> tuple[dict[str, Any], bool]:
    if change_type not in CHANGE_TYPE_SET:
        allowed = ", ".join(CHANGE_TYPES)
        raise ValueError(f"change_type must be one of: {allowed}")

    normalized_path = _normalize_path(entry_path)
    if _looks_like_glob(normalized_path):
        raise ValueError("path must be an explicit file path without glob markers")

    data = _load_yaml(path) if path.is_file() else empty_matrix()
    entries = data.setdefault("entries", [])
    if not isinstance(entries, list):
        entries = []
        data["entries"] = entries

    payload = {
        "path": normalized_path,
        "change_type": change_type,
        "impact_summary": impact_summary.strip(),
    }

    idx = _entry_index(entries, normalized_path)
    created = idx is None
    if idx is None:
        entries.append(payload)
    else:
        entries[idx] = payload

    questions, _ = validate_matrix(data, matrix_path=str(path))
    if questions:
        messages = "; ".join(q.text for q in questions)
        raise ValueError(messages)

    _dump_yaml(path, data)
    return data, created


def delete_entry(path: Path, *, entry_path: str) -> tuple[dict[str, Any], bool]:
    data = _load_yaml(path)
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")

    normalized_path = _normalize_path(entry_path)
    idx = _entry_index(entries, normalized_path)
    if idx is None:
        return data, False

    del entries[idx]
    _dump_yaml(path, data)
    return data, True


def filter_entries(
    data: dict[str, Any],
    *,
    suffix: str | None = None,
    change_types: list[str] | None = None,
    path_prefix: str | None = None,
) -> list[dict[str, str]]:
    if change_types is not None:
        invalid = [value for value in change_types if value not in CHANGE_TYPE_SET]
        if invalid:
            allowed = ", ".join(CHANGE_TYPES)
            raise ValueError(
                f"change_type filter contains invalid values: {invalid!r}; "
                f"must be one of: {allowed}"
            )

    normalized_prefix = _normalize_path(path_prefix) if path_prefix else None
    filtered: list[dict[str, str]] = []
    for entry in list_entries(data):
        if suffix is not None and not entry["path"].endswith(suffix):
            continue
        if change_types is not None and entry["change_type"] not in change_types:
            continue
        if normalized_prefix is not None and not entry["path"].startswith(normalized_prefix):
            continue
        filtered.append(entry)
    return filtered


def build_report(
    *,
    ok: bool,
    summary: str,
    entries_changed: int = 0,
    warnings: list[str] | None = None,
    questions: list[MatrixQuestion] | None = None,
    matrix_yaml: str | None = None,
    entries: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "ok": ok,
        "summary": summary,
        "entries_changed": entries_changed,
        "warnings": warnings or [],
        "questions": [q.as_dict() for q in (questions or [])],
        "entries": entries or [],
        "report": {
            "summary": summary,
        },
    }
    if matrix_yaml is not None:
        report["matrix_yaml"] = matrix_yaml
    return report


def emit_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)


def format_questions_yaml(questions: list[MatrixQuestion]) -> str:
    lines: list[str] = []
    for q in questions:
        lines.append(f"- where: {q.where}")
        lines.append(f"  type: {q.type}")
        lines.append(f"  text: {q.text}")
    return "\n".join(lines)
