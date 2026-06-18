"""Impact matrix v2: model, mutation, query, validation, and JSON report.

An impact connects raw requirement quotes to the spec files they drive.
Schema:

    version: 2
    impacts:
      - id: <uuid>                      # global identity, auto-generated on create
        owner: <one of OWNERS>          # the plan phase that maintains these specs
        quotes: [<str>, ...]            # raw requirement sentences
        rationale: <str>                # why the quotes drive these specs
        status: pending | resolved      # resolved iff every spec is consistent
        specs:
          - path: <relative file path>  # unique within the impact (may repeat across impacts)
            status: inconsistent | consistent

Mutating operations validate the whole resulting matrix and raise MatrixError
(carrying violations) instead of writing an invalid file. There is no standalone
validate verb; the invariants live here and are enforced on every write.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}") from exc

SCHEMA_VERSION = 2

OWNERS: tuple[str, ...] = (
    "aibdd-flows-specify",
    "aibdd-rules-specify",
    "aibdd-spec-by-example",
    "aibdd-plan",
    "aibdd-api-plan",
    "aibdd-data-plan",
)
OWNER_SET = frozenset(OWNERS)

IMPACT_STATUSES: tuple[str, ...] = ("pending", "resolved")
SPEC_STATUSES: tuple[str, ...] = ("inconsistent", "consistent")


@dataclass(frozen=True)
class MatrixViolation:
    location: str
    type: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "location": self.location,
            "type": self.type,
            "message": self.message,
        }


class MatrixError(Exception):
    """Raised by mutating ops when the resulting matrix would be invalid."""

    def __init__(self, violations: list[MatrixViolation]):
        self.violations = violations
        super().__init__("; ".join(v.message for v in violations))


# --- deterministic id seam (tests inject IMPACT_MATRIX_TEST_IDS) ------------

_test_id_index = 0


def reset_test_ids() -> None:
    global _test_id_index
    _test_id_index = 0


def _generate_id() -> str:
    global _test_id_index
    seq = os.environ.get("IMPACT_MATRIX_TEST_IDS")
    if seq:
        ids = [s.strip() for s in seq.split(",") if s.strip()]
        if _test_id_index < len(ids):
            value = ids[_test_id_index]
            _test_id_index += 1
            return value
    return str(uuid.uuid4())


# --- plumbing ---------------------------------------------------------------


def repo_root_from_module() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    return here.parents[5]


def empty_matrix() -> dict[str, Any]:
    return {"version": SCHEMA_VERSION, "impacts": []}


def _normalize_path(path: str) -> str:
    cleaned = path.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


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


def load_matrix(path: Path) -> dict[str, Any]:
    return _load_yaml(path)


def list_impacts(data: dict[str, Any]) -> list[dict[str, Any]]:
    impacts = data.get("impacts", [])
    return impacts if isinstance(impacts, list) else []


# --- internal helpers -------------------------------------------------------


def _find_impact(impacts: list[dict[str, Any]], impact_id: str) -> tuple[int, dict] | None:
    for idx, imp in enumerate(impacts):
        if imp.get("id") == impact_id:
            return idx, imp
    return None


def _not_found(location: str, message: str) -> MatrixError:
    return MatrixError([MatrixViolation(location, "NOT_FOUND", message)])


def _commit(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    violations = validate_matrix(data)
    if violations:
        raise MatrixError(violations)
    _dump_yaml(path, data)
    return data


# --- public operations ------------------------------------------------------


def init_matrix(path: Path) -> dict[str, Any]:
    if path.exists():
        raise MatrixError(
            [
                MatrixViolation(
                    "args.matrix",
                    "ALREADY_EXISTS",
                    "impact matrix already exists; init refuses to overwrite",
                )
            ]
        )
    data = empty_matrix()
    _dump_yaml(path, data)
    return data


def write_impact(
    path: Path,
    *,
    owner: str,
    quotes: list[str],
    rationale: str,
    spec_paths: list[str],
    impact_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = _load_yaml(path) if path.is_file() else empty_matrix()
    impacts = data.setdefault("impacts", [])
    impact = {
        "id": impact_id or _generate_id(),
        "owner": owner,
        "quotes": list(quotes),
        "rationale": rationale,
        "status": "pending",
        "specs": [{"path": p, "status": "inconsistent"} for p in spec_paths],
    }
    found = _find_impact(impacts, impact["id"]) if impact_id else None
    if found is not None:
        impacts[found[0]] = impact
    else:
        impacts.append(impact)
    _commit(path, data)
    return data, impact


def add_spec(
    path: Path,
    *,
    impact_id: str,
    spec_path: str,
    status: str,
) -> dict[str, Any]:
    data = _load_yaml(path)
    found = _find_impact(data.get("impacts", []), impact_id)
    if found is None:
        raise _not_found("args.id", f"impact `{impact_id}` not found")
    _, impact = found
    impact.setdefault("specs", []).append({"path": spec_path, "status": status})
    if status == "inconsistent":
        impact["status"] = "pending"
    return _commit(path, data)


def transit_status(
    path: Path,
    *,
    impact_id: str,
    status: str,
    spec_path: str | None = None,
) -> dict[str, Any]:
    if spec_path is not None:
        if status not in SPEC_STATUSES:
            allowed = ", ".join(SPEC_STATUSES)
            raise MatrixError([MatrixViolation(
                "args.status", "INVALID_VALUE",
                f"status '{status}' is invalid for a spec; must be one of: {allowed}",
            )])
    elif status not in IMPACT_STATUSES:
        allowed = ", ".join(IMPACT_STATUSES)
        raise MatrixError([MatrixViolation(
            "args.status", "INVALID_VALUE",
            f"status '{status}' is invalid for an impact; must be one of: {allowed}",
        )])

    data = _load_yaml(path)
    found = _find_impact(data.get("impacts", []), impact_id)
    if found is None:
        raise _not_found("args.id", f"impact `{impact_id}` not found")
    _, impact = found

    if spec_path is None:
        impact["status"] = status
    else:
        spec = next((s for s in impact.get("specs", []) if s.get("path") == spec_path), None)
        if spec is None:
            raise _not_found(
                "args.spec",
                f"spec `{spec_path}` not found in impact `{impact_id}`",
            )
        spec["status"] = status
        # introducing inconsistency auto-degrades the impact; consistency never auto-resolves.
        if status == "inconsistent":
            impact["status"] = "pending"
    return _commit(path, data)


def remove_impact(
    path: Path,
    *,
    impact_id: str,
    spec_path: str | None = None,
) -> dict[str, Any]:
    data = _load_yaml(path)
    impacts = data.get("impacts", [])
    found = _find_impact(impacts, impact_id)
    if found is None:
        return _commit(path, data)
    idx, impact = found
    if spec_path is None:
        del impacts[idx]
    else:
        impact["specs"] = [s for s in impact.get("specs", []) if s.get("path") != spec_path]
    return _commit(path, data)


def read_impacts(
    data: dict[str, Any],
    *,
    impact_id: str | None = None,
    owners: list[str] | None = None,
    impact_status: str | None = None,
    spec_status: str | None = None,
    spec_path: str | None = None,
) -> list[dict[str, Any]]:
    pattern = re.compile(spec_path) if spec_path is not None else None
    spec_filtering = spec_status is not None or pattern is not None
    result: list[dict[str, Any]] = []
    for impact in list_impacts(data):
        if impact_id is not None and impact.get("id") != impact_id:
            continue
        if owners is not None and impact.get("owner") not in owners:
            continue
        if impact_status is not None and impact.get("status") != impact_status:
            continue
        if not spec_filtering:
            result.append(impact)
            continue
        specs = [
            s
            for s in impact.get("specs", [])
            if (spec_status is None or s.get("status") == spec_status)
            and (pattern is None or pattern.search(str(s.get("path", ""))))
        ]
        if not specs:
            continue
        result.append({**impact, "specs": specs})
    return result


def validate_matrix(
    data: dict[str, Any],
    *,
    matrix_path: str = "impact-matrix.yml",
) -> list[MatrixViolation]:
    violations: list[MatrixViolation] = []

    if data.get("version") != SCHEMA_VERSION:
        violations.append(MatrixViolation(
            "version", "INVALID_VALUE", f"version must be {SCHEMA_VERSION}",
        ))

    impacts = data.get("impacts", [])
    seen_ids: set[str] = set()
    for i, impact in enumerate(impacts):
        loc = f"impacts[{i}]"
        iid = impact.get("id")
        if not isinstance(iid, str) or not iid.strip():
            violations.append(MatrixViolation(f"{loc}.id", "MISSING", "id is required"))
        elif iid in seen_ids:
            violations.append(MatrixViolation(
                f"{loc}.id", "DUPLICATE", f"duplicate impact id `{iid}`",
            ))
        else:
            seen_ids.add(iid)

        if impact.get("owner") not in OWNER_SET:
            allowed = ", ".join(OWNERS)
            violations.append(MatrixViolation(
                f"{loc}.owner", "INVALID_VALUE",
                f"owner '{impact.get('owner')}' is invalid; must be one of: {allowed}",
            ))

        quotes = impact.get("quotes")
        if (
            not isinstance(quotes, list)
            or not quotes
            or not all(isinstance(q, str) and q.strip() for q in quotes)
        ):
            violations.append(MatrixViolation(
                f"{loc}.quotes", "MISSING",
                "quotes must be a non-empty list of non-empty strings",
            ))

        rationale = impact.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            violations.append(MatrixViolation(
                f"{loc}.rationale", "MISSING", "rationale must be a non-empty string",
            ))

        status = impact.get("status")
        if status not in IMPACT_STATUSES:
            allowed = ", ".join(IMPACT_STATUSES)
            violations.append(MatrixViolation(
                f"{loc}.status", "INVALID_VALUE",
                f"status '{status}' is invalid for an impact; must be one of: {allowed}",
            ))

        seen_paths: set[str] = set()
        specs = impact.get("specs", [])
        for j, spec in enumerate(specs):
            sloc = f"{loc}.specs[{j}]"
            spath = spec.get("path")
            if not isinstance(spath, str) or not spath.strip():
                violations.append(MatrixViolation(f"{sloc}.path", "MISSING", "spec path is required"))
            elif spath in seen_paths:
                violations.append(MatrixViolation(
                    f"{sloc}.path", "DUPLICATE",
                    f"duplicate spec path `{spath}` within impact",
                ))
            else:
                seen_paths.add(spath)
            if spec.get("status") not in SPEC_STATUSES:
                allowed = ", ".join(SPEC_STATUSES)
                violations.append(MatrixViolation(
                    f"{sloc}.status", "INVALID_VALUE",
                    f"status '{spec.get('status')}' is invalid for a spec; must be one of: {allowed}",
                ))

        if status == "resolved":
            for spec in specs:
                if spec.get("status") == "inconsistent":
                    violations.append(MatrixViolation(
                        f"{loc}.status", "INCONSISTENT",
                        f"impact `{iid}` is resolved but spec `{spec.get('path')}` is inconsistent",
                    ))
                    break

    return violations


# --- report -----------------------------------------------------------------


def build_report(
    *,
    ok: bool,
    violations: list[MatrixViolation] | None = None,
    impacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "violations": [v.as_dict() for v in (violations or [])],
        "impacts": impacts or [],
    }


def emit_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
