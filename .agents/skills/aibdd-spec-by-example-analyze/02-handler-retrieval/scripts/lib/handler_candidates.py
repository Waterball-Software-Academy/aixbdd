"""Handler candidate retrieval: query DSL catalog and enrich # candidates: blocks."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DSL_MARKER = "# @dsl"
KINDS_PREFIX = "# handler-candidate-kinds:"
RULE_PREFIX = "# rule:"
CANDIDATES_PREFIX = "# candidates:"
SHARED_ONLY_KINDS = frozenset({"time-control", "external-stub"})
EXECUTABLE_START = re.compile(
    r"^\s*(Example:|Scenario Outline:|Scenario:|Given |When |Then |And )"
)


def repo_root_from_module() -> Path:
    module_dir = Path(__file__).resolve()
    for parent in module_dir.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    raise FileNotFoundError("cannot locate repo root from handler_candidates module")


_REPO_ROOT = repo_root_from_module()
DSL_CLI_ENTRY = _REPO_ROOT / ".claude/skills/aibdd-core/scripts/cli/dsl_cli.py"


@dataclass
class HandlerCandidateQuestion:
    path: Path
    line_no: int
    kind: str
    text: str


@dataclass
class DslBlock:
    start_line: int
    end_line: int
    kinds: list[str] | None
    rule_line: int | None
    candidates_start: int | None
    candidates_end: int | None
    step_line: int


def discover_feature_paths(feature_specs_dir: Path) -> list[Path]:
    if not feature_specs_dir.is_dir():
        return []
    return sorted(feature_specs_dir.rglob("*.feature"))


def discover_dsl_paths(contracts_dir: Path, data_dir: Path) -> list[Path]:
    paths: list[Path] = []
    if contracts_dir.is_dir():
        paths.extend(sorted(contracts_dir.glob("*.dsl.yml")))
    if data_dir.is_dir():
        paths.extend(sorted(data_dir.glob("*.dsl.yml")))
    return paths


def parse_handler_candidate_kinds(line: str) -> list[str] | None:
    stripped = line.lstrip()
    if not stripped.startswith(KINDS_PREFIX):
        return None
    raw = stripped[len(KINDS_PREFIX) :].strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split("|") if part.strip()]


def _is_dsl_comment(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("#") and (
        stripped.startswith(DSL_MARKER)
        or stripped.startswith(KINDS_PREFIX)
        or stripped.startswith(RULE_PREFIX)
        or stripped.startswith(CANDIDATES_PREFIX)
        or stripped.startswith("#   -")
    )


def parse_dsl_blocks(lines: list[str]) -> list[DslBlock]:
    blocks: list[DslBlock] = []
    idx = 0
    while idx < len(lines):
        if lines[idx].lstrip().startswith(DSL_MARKER):
            start = idx
            kinds: list[str] | None = None
            rule_line: int | None = None
            candidates_start: int | None = None
            candidates_end: int | None = None
            step_line = start
            idx += 1
            while idx < len(lines):
                line = lines[idx]
                stripped = line.lstrip()
                if stripped.startswith(KINDS_PREFIX):
                    kinds = parse_handler_candidate_kinds(line)
                elif stripped.startswith(RULE_PREFIX):
                    rule_line = idx
                elif stripped.startswith(CANDIDATES_PREFIX):
                    candidates_start = idx
                    candidates_end = idx + 1
                    idx += 1
                    while idx < len(lines) and lines[idx].lstrip().startswith("#   -"):
                        candidates_end = idx + 1
                        idx += 1
                    continue
                elif EXECUTABLE_START.match(line):
                    step_line = idx
                    break
                elif stripped.startswith(DSL_MARKER):
                    break
                idx += 1
            end = step_line
            blocks.append(
                DslBlock(
                    start_line=start,
                    end_line=end,
                    kinds=kinds,
                    rule_line=rule_line,
                    candidates_start=candidates_start,
                    candidates_end=candidates_end,
                    step_line=step_line,
                )
            )
            continue
        idx += 1
    return blocks


def _run_dsl_cli_query(
    *,
    handlers: list[str],
    dsl_paths: list[Path],
    shared_dsl_path: Path | None,
    source_scope: str,
    cwd: Path,
) -> list[dict[str, Any]]:
    cmd = [
        sys.executable,
        str(DSL_CLI_ENTRY),
        "query",
        *sum([["--handler", handler] for handler in handlers], []),
        "--source-scope",
        source_scope,
    ]
    for path in dsl_paths:
        cmd.extend(["--dsl", path.as_posix()])
    if shared_dsl_path is not None:
        cmd.extend(["--shared-dsl", shared_dsl_path.as_posix()])
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "query failed")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid query JSON: {proc.stdout!r}") from exc
    if not isinstance(payload, list):
        raise ValueError(f"query JSON must be an array, got {type(payload)!r}")
    return payload


def union_candidates_for_kinds(
    kinds: list[str],
    *,
    regular_dsl_paths: list[Path],
    shared_dsl_path: Path | None,
    cwd: Path,
) -> list[str]:
    regular_kinds = [kind for kind in kinds if kind not in SHARED_ONLY_KINDS]
    shared_kinds = [kind for kind in kinds if kind in SHARED_ONLY_KINDS]

    regular_matches: dict[str, list[str]] = {}
    if regular_kinds:
        payload = _run_dsl_cli_query(
            handlers=regular_kinds,
            dsl_paths=regular_dsl_paths,
            shared_dsl_path=None,
            source_scope="regular",
            cwd=cwd,
        )
        for item in payload:
            handler = item["handler"]
            regular_matches.setdefault(handler, []).append(item["name"])

    shared_matches: dict[str, list[str]] = {}
    if shared_kinds and shared_dsl_path is not None:
        payload = _run_dsl_cli_query(
            handlers=shared_kinds,
            dsl_paths=[],
            shared_dsl_path=shared_dsl_path,
            source_scope="shared",
            cwd=cwd,
        )
        for item in payload:
            handler = item["handler"]
            shared_matches.setdefault(handler, []).append(item["name"])

    seen: set[str] = set()
    ordered: list[str] = []
    for kind in kinds:
        pool = shared_matches if kind in SHARED_ONLY_KINDS else regular_matches
        for name in pool.get(kind, []):
            if name in seen:
                continue
            seen.add(name)
            ordered.append(name)
    return ordered


def render_candidates_block(indent: str, candidate_names: list[str]) -> list[str]:
    lines = [f"{indent}{CANDIDATES_PREFIX}"]
    for name in candidate_names:
        lines.append(f"{indent}#   - {name}")
    return lines


def _block_indent(lines: list[str], block: DslBlock) -> str:
    marker = lines[block.start_line]
    return marker[: len(marker) - len(marker.lstrip())]


def apply_block_candidates(
    lines: list[str],
    block: DslBlock,
    candidate_names: list[str],
) -> bool:
    indent = _block_indent(lines, block)
    new_block = render_candidates_block(indent, candidate_names)
    if block.candidates_start is not None and block.candidates_end is not None:
        old = lines[block.candidates_start : block.candidates_end]
        if old == new_block:
            return False
        lines[block.candidates_start : block.candidates_end] = new_block
        return True

    insert_at = block.rule_line + 1 if block.rule_line is not None else block.start_line + 1
    lines[insert_at:insert_at] = new_block
    return True


def apply_in_place_update(
    path: Path,
    *,
    regular_dsl_paths: list[Path],
    shared_dsl_path: Path | None,
    questions: list[HandlerCandidateQuestion],
    cwd: Path | None = None,
) -> tuple[bool, int]:
    work_cwd = cwd or path.parent
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    blocks = parse_dsl_blocks(lines)
    changed = False
    updated_blocks = 0

    for block in sorted(blocks, key=lambda item: item.start_line, reverse=True):
        line_no = block.start_line + 1
        if block.kinds is None:
            questions.append(
                HandlerCandidateQuestion(
                    path=path,
                    line_no=line_no,
                    kind="missing-handler-candidate-kinds",
                    text=(
                        f"# @dsl block at {path.name}:{line_no} has no "
                        f"# handler-candidate-kinds:"
                    ),
                )
            )
            continue
        if not block.kinds:
            questions.append(
                HandlerCandidateQuestion(
                    path=path,
                    line_no=line_no,
                    kind="missing-handler-candidate-kinds",
                    text=(
                        f"# @dsl block at {path.name}:{line_no} has empty "
                        f"# handler-candidate-kinds:"
                    ),
                )
            )
            continue

        candidate_names = union_candidates_for_kinds(
            block.kinds,
            regular_dsl_paths=regular_dsl_paths,
            shared_dsl_path=shared_dsl_path,
            cwd=work_cwd,
        )
        if not candidate_names:
            questions.append(
                HandlerCandidateQuestion(
                    path=path,
                    line_no=line_no,
                    kind="no-candidates-found",
                    text=(
                        f"kinds {block.kinds!r} matched no dsl entry in "
                        f"{path.name}:{line_no}"
                    ),
                )
            )

        if apply_block_candidates(lines, block, candidate_names):
            changed = True
            updated_blocks += 1

    if changed:
        trailing_newline = original.endswith("\n")
        rendered = "\n".join(lines)
        if trailing_newline or not rendered.endswith("\n"):
            rendered += "\n"
        path.write_text(rendered, encoding="utf-8")
    return changed, updated_blocks


def question_to_json_dict(question: HandlerCandidateQuestion) -> dict[str, str]:
    return {
        "where": f"{question.path.name}:{question.line_no}",
        "type": question.kind,
        "text": question.text,
    }


def build_apply_report(
    *,
    changed_count: int,
    feature_count: int,
    changed_features: list[str],
    updated_block_count: int,
    questions: list[HandlerCandidateQuestion],
) -> dict[str, Any]:
    return {
        "changed_count": changed_count,
        "feature_count": feature_count,
        "changed_features": changed_features,
        "updated_block_count": updated_block_count,
        "questions": [question_to_json_dict(q) for q in questions],
        "report": {
            "summary": (
                f"changed={changed_count} features={feature_count} "
                f"blocks={updated_block_count} questions={len(questions)}"
            ),
        },
    }


def emit_apply_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
