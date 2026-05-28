"""Form-lock core: load boundary profile YAML and apply Example skeletons to .feature files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RULE_PATTERN = re.compile(r"^(\s*)Rule:\s*")
EXECUTABLE_START = re.compile(
    r"^\s*(Example:|Scenario Outline:|Scenario:|Given |When |Then |And )"
)
PROFILE_FILENAME = "form-lock.profile.yml"
SBE_FORM_LOCK_DIR = "sbe-form-lock"
DSL_ARRANGEMENT_RULES_DIR = "dsl-arrangement-rules"


def repo_root_from_module() -> Path:
    module_dir = Path(__file__).resolve()
    for parent in module_dir.parents:
        if (parent / ".claude" / "skills" / "aibdd-core").is_dir():
            return parent
    raise FileNotFoundError("cannot locate repo root from form_lock module")


_REPO_ROOT = repo_root_from_module()
CORE_BOUNDARIES_ROOT = _REPO_ROOT / ".claude/skills/aibdd-core/assets/boundaries"
DEFAULT_BOUNDARY_YML = _REPO_ROOT / "specs/architecture/boundary.yml"


@dataclass
class FormLockConfig:
    boundary_type: str
    sbe_form_lock_dir: Path
    rule_prefix_to_template: list[tuple[str, str]]


@dataclass
class UnknownPrefixQuestion:
    path: Path
    line_no: int
    prefix: str | None


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise ValueError(f"PyYAML is required to parse {path}") from exc
    if not path.is_file():
        raise FileNotFoundError(str(path))
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected YAML mapping in {path}")
    return data


def _sort_prefix_mappings(
    entries: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        prefix = entry.get("rule_prefix")
        template = entry.get("template")
        if not isinstance(prefix, str) or not isinstance(template, str):
            continue
        pairs.append((prefix, template))
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def load_profile_from_path(profile_path: Path) -> FormLockConfig:
    data = _load_yaml(profile_path)
    boundary_type = data.get("boundary_type")
    if not isinstance(boundary_type, str) or not boundary_type.strip():
        raise ValueError(f"boundary_type missing in {profile_path}")
    raw_entries = data.get("rule_prefix_to_template")
    if not isinstance(raw_entries, list):
        raise ValueError(f"rule_prefix_to_template missing in {profile_path}")
    return FormLockConfig(
        boundary_type=boundary_type,
        sbe_form_lock_dir=profile_path.parent,
        rule_prefix_to_template=_sort_prefix_mappings(raw_entries),
    )


def resolve_profile_for_boundary_type(
    boundary_type: str,
    boundaries_root: Path = CORE_BOUNDARIES_ROOT,
) -> FormLockConfig:
    profile_path = (
        boundaries_root / boundary_type / SBE_FORM_LOCK_DIR / PROFILE_FILENAME
    )
    return load_profile_from_path(profile_path)


def load_active_boundary_type(boundary_yml: Path = DEFAULT_BOUNDARY_YML) -> str:
    data = _load_yaml(boundary_yml)
    boundary_type = data.get("type")
    if not isinstance(boundary_type, str) or not boundary_type.strip():
        raise ValueError(f"type missing in {boundary_yml}")
    return boundary_type


def load_active_profile(
    boundary_yml: Path = DEFAULT_BOUNDARY_YML,
    boundaries_root: Path = CORE_BOUNDARIES_ROOT,
) -> FormLockConfig:
    boundary_type = load_active_boundary_type(boundary_yml)
    return resolve_profile_for_boundary_type(boundary_type, boundaries_root)


def config_to_json_dict(config: FormLockConfig) -> dict[str, Any]:
    return {
        "boundary_type": config.boundary_type,
        "rule_prefix_to_template": [
            {"rule_prefix": prefix, "template": template}
            for prefix, template in config.rule_prefix_to_template
        ],
    }


def emit_config_json(config: FormLockConfig) -> str:
    return json.dumps(config_to_json_dict(config), ensure_ascii=False)


def _extract_rule_prefix(rule_line: str) -> str | None:
    match = RULE_PATTERN.match(rule_line)
    if not match:
        return None
    remainder = rule_line[match.end() :].strip()
    if " - " not in remainder:
        return None
    return remainder.split(" - ", 1)[0].strip()


def map_rule_to_template(
    rule_line: str, config: FormLockConfig
) -> tuple[str | None, str | None]:
    prefix = _extract_rule_prefix(rule_line)
    if prefix is None:
        return None, None
    for rule_prefix, template in config.rule_prefix_to_template:
        if prefix.startswith(rule_prefix):
            return prefix, template
    return prefix, None


def extract_template_block(tmpl_path: Path) -> list[str]:
    if not tmpl_path.is_file():
        raise FileNotFoundError(str(tmpl_path))
    lines = tmpl_path.read_text(encoding="utf-8").splitlines()
    start = 0
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("Example:") or stripped.startswith("Scenario Outline:"):
            start = idx
            break
    else:
        raise ValueError(f"no Example/Scenario Outline block in {tmpl_path}")
    return lines[start:]


def is_executable_line(line: str) -> bool:
    return bool(EXECUTABLE_START.match(line))


def is_rule_comment(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("#") and not stripped.startswith("# @dsl")


def should_replace_line(line: str) -> bool:
    return is_rule_comment(line)


def _rule_indent_len(rule_line: str) -> int:
    match = RULE_PATTERN.match(rule_line)
    if not match:
        return 0
    return len(match.group(1))


def is_skippable_before_insert(line: str, rule_indent: str) -> bool:
    if not line.strip():
        return True
    if RULE_PATTERN.match(line):
        return False
    cur_indent = len(line) - len(line.lstrip())
    rule_indent_len = len(rule_indent)
    if cur_indent <= rule_indent_len:
        return False
    if is_executable_line(line):
        return False
    if should_replace_line(line):
        return False
    return True


def _scan_rule_body(
    lines: list[str], rule_idx: int
) -> tuple[int, int | None, int | None]:
    rule_indent = RULE_PATTERN.match(lines[rule_idx])
    if not rule_indent:
        return rule_idx + 1, None, None
    base = rule_indent.group(1)
    base_len = len(base)
    insert_at = rule_idx + 1
    replace_start: int | None = None
    replace_end: int | None = None
    idx = rule_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if not line.strip():
            insert_at = idx + 1
            idx += 1
            continue
        cur_indent = len(line) - len(line.lstrip())
        if RULE_PATTERN.match(line) or cur_indent <= base_len:
            break
        if is_executable_line(line):
            break
        if should_replace_line(line):
            if replace_start is None:
                replace_start = idx
            replace_end = idx + 1
            insert_at = replace_start
            idx += 1
            continue
        replace_start = None
        replace_end = None
        insert_at = idx + 1
        idx += 1
    return insert_at, replace_start, replace_end


def find_rule_insert_anchor(lines: list[str], rule_idx: int) -> int:
    insert_at, _, _ = _scan_rule_body(lines, rule_idx)
    return insert_at


def is_form_locked(lines: list[str], rule_idx: int) -> bool:
    base_len = _rule_indent_len(lines[rule_idx])
    idx = rule_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if not line.strip():
            idx += 1
            continue
        cur_indent = len(line) - len(line.lstrip())
        if RULE_PATTERN.match(line) or cur_indent <= base_len:
            break
        if EXECUTABLE_START.match(line):
            block_end = idx + 1
            while block_end < len(lines):
                next_line = lines[block_end]
                if not next_line.strip():
                    block_end += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if RULE_PATTERN.match(next_line) or next_indent <= base_len:
                    break
                if (
                    EXECUTABLE_START.match(next_line)
                    and next_indent <= cur_indent + 2
                ):
                    break
                block_end += 1
            block = lines[idx:block_end]
            if any("# @dsl" in item for item in block):
                return True
            idx = block_end
            continue
        idx += 1
    return False


def indent_block(block: list[str], base_indent: str) -> list[str]:
    non_empty = [line for line in block if line.strip()]
    if not non_empty:
        return []
    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty)
    child_base = f"{base_indent}    "
    result: list[str] = []
    for line in block:
        if not line.strip():
            result.append("")
            continue
        extra = len(line) - len(line.lstrip()) - min_indent
        result.append(f"{child_base}{' ' * extra}{line.lstrip()}")
    return result


def _needs_blank_before_skeleton(lines: list[str], insert_at: int) -> bool:
    if insert_at <= 0:
        return True
    prev = lines[insert_at - 1]
    return bool(prev.strip())


def apply_in_place_update(
    path: Path, config: FormLockConfig, questions: list[UnknownPrefixQuestion]
) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    changed = False
    rule_indices = [
        idx for idx, line in enumerate(lines) if RULE_PATTERN.match(line)
    ]

    offset = 0
    for rule_idx in rule_indices:
        adjusted_idx = rule_idx + offset
        if adjusted_idx >= len(lines):
            break
        rule_line = lines[adjusted_idx]
        if is_form_locked(lines, adjusted_idx):
            continue

        prefix, template_name = map_rule_to_template(rule_line, config)
        if template_name is None:
            questions.append(
                UnknownPrefixQuestion(
                    path=path,
                    line_no=adjusted_idx + 1,
                    prefix=prefix,
                )
            )
            continue

        tmpl_path = config.sbe_form_lock_dir / template_name
        block = extract_template_block(tmpl_path)
        rule_indent = RULE_PATTERN.match(rule_line)
        if not rule_indent:
            continue
        indented = indent_block(block, rule_indent.group(1))

        insert_at, replace_start, replace_end = _scan_rule_body(lines, adjusted_idx)
        new_segment: list[str] = []
        if _needs_blank_before_skeleton(lines, insert_at):
            new_segment.append("")
        new_segment.extend(indented)

        if replace_start is not None and replace_end is not None:
            lines = lines[:replace_start] + new_segment + lines[replace_end:]
            offset += len(new_segment) - (replace_end - replace_start)
        else:
            lines = lines[:insert_at] + new_segment + lines[insert_at:]
            offset += len(new_segment)
        changed = True

    if changed:
        trailing_newline = original.endswith("\n")
        rendered = "\n".join(lines)
        if trailing_newline or not rendered.endswith("\n"):
            rendered += "\n"
        path.write_text(rendered, encoding="utf-8")
    return changed


def discover_feature_paths(feature_specs_dir: Path) -> list[Path]:
    if not feature_specs_dir.is_dir():
        return []
    return sorted(feature_specs_dir.rglob("*.feature"))


def question_to_json_dict(question: UnknownPrefixQuestion) -> dict[str, str]:
    prefix = question.prefix or "?"
    return {
        "where": f"{question.path.name}:{question.line_no}",
        "type": prefix,
        "text": (
            "unknown rule type prefix "
            f"`{prefix}`; must match form-lock.profile.yml rule_prefix_to_template"
        ),
    }


def questions_to_json_dicts(
    questions: list[UnknownPrefixQuestion],
) -> list[dict[str, str]]:
    return [question_to_json_dict(question) for question in questions]


def build_apply_report(
    *,
    changed_count: int,
    feature_count: int,
    questions: list[UnknownPrefixQuestion],
    changed_features: list[str],
) -> dict[str, Any]:
    return {
        "changed_count": changed_count,
        "feature_count": feature_count,
        "changed_features": changed_features,
        "questions": questions_to_json_dicts(questions),
        "report": {
            "summary": (
                f"changed={changed_count} features={feature_count} "
                f"questions={len(questions)}"
            ),
        },
    }


def emit_apply_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)
