"""Universal eval rules — apply to every DSL entry regardless of preset.

Rule chain: each rule is a callable that takes (entry, entry_file) and yields
zero or more Violations. `evaluate()` runs them all and assembles an
EvalReport. Some rules (name-uniqueness) operate on the cross-entry corpus
rather than per-entry; they are dispatched after the per-entry sweep.

Per Policy 3 / Risk R5: handler-specific scheme legality is OUT of scope here.
Plugins guarantee scheme legality constructively in generate_templates.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from dsl_cli.models import DSLEntry, EvalReport, Violation

# -- per-entry rules --------------------------------------------------------


FORMAT_PARAMS_CAP = 3
DATATABLE_REQUIRED_CAP = 6

# Five valid target URI schemes; see spec.md §1 Target URI Schemes table.
_SCHEME_RE = re.compile(
    r"^("
    r"(response:\$.+)"           # response:JSONPath
    r"|(literal:[A-Za-z0-9_\-]+)"  # literal:<type>
    r"|(stub_payload:[A-Za-z0-9_\-.]+)"  # stub_payload:<field>
    r"|([^#\s]+#.+)"             # <spec_file>#<anchor>  (OpenAPI or DBML)
    r")$"
)

_FORMAT_PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}")
_RESIDUAL_CANDIDATE_COMMENT_RE = re.compile(r"^\s*#\s*候選參數", re.MULTILINE)


def rule_format_params_cap(entry: DSLEntry, entry_file: Path):
    placeholders = _FORMAT_PLACEHOLDER_RE.findall(entry.format)
    if len(placeholders) > FORMAT_PARAMS_CAP:
        yield Violation(
            rule_id="format-params-cap",
            entry_name=entry.name,
            entry_file=entry_file,
            message=(
                f"format 句型含 {len(placeholders)} 個參數，超過上限 {FORMAT_PARAMS_CAP}"
            ),
            hint="拆成兩條 DSL instruction，或把次要參數遷進 datatable_bindings",
        )


def rule_datatable_cap(entry: DSLEntry, entry_file: Path):
    required_count = sum(
        1
        for b in entry.datatable_bindings.values()
        if b.required and b.default_value is None
    )
    if required_count > DATATABLE_REQUIRED_CAP:
        yield Violation(
            rule_id="datatable-cap",
            entry_name=entry.name,
            entry_file=entry_file,
            message=(
                f"datatable_bindings 必填欄位數 {required_count}，超過上限 {DATATABLE_REQUIRED_CAP}"
            ),
            hint="為次要欄位補 default_value，使其在 DataTable 變成可選",
        )


def rule_schema_completeness(entry: DSLEntry, entry_file: Path):
    if not entry.format or entry.format.strip() == "<FILL IN>":
        yield Violation(
            rule_id="schema-completeness",
            entry_name=entry.name,
            entry_file=entry_file,
            message="format 仍為 `<FILL IN>` 占位符；SEMANTIC 階段尚未填字",
        )
    for field in ("name", "handler", "target_part_path"):
        value = getattr(entry, field, "")
        if not value:
            yield Violation(
                rule_id="schema-completeness",
                entry_name=entry.name or "<unnamed>",
                entry_file=entry_file,
                message=f"必要欄 {field} 為空",
            )
    for key, b in entry.datatable_bindings.items():
        if b.default_value is not None and b.default_value.strip() == "<FILL IN>":
            yield Violation(
                rule_id="schema-completeness",
                entry_name=entry.name,
                entry_file=entry_file,
                message=f"datatable_bindings[{key}].default_value 仍為 `<FILL IN>` 占位符；SEMANTIC 階段尚未填入",
            )


def rule_format_key_binding_bijection(entry: DSLEntry, entry_file: Path):
    placeholders = set(_FORMAT_PLACEHOLDER_RE.findall(entry.format))
    param_keys = set(entry.param_bindings.keys())
    missing_from_format = param_keys - placeholders
    missing_from_bindings = placeholders - param_keys
    if missing_from_format:
        yield Violation(
            rule_id="format-key-binding-bijection",
            entry_name=entry.name,
            entry_file=entry_file,
            message=(
                f"param_bindings 內存在 {sorted(missing_from_format)}，"
                f"但 format 中未出現對應 {{key}} 引用"
            ),
        )
    if missing_from_bindings:
        yield Violation(
            rule_id="format-key-binding-bijection",
            entry_name=entry.name,
            entry_file=entry_file,
            message=(
                f"format 中引用 {{key}} {sorted(missing_from_bindings)}，"
                f"但 param_bindings 未定義"
            ),
        )


def rule_target_uri_scheme_validity(entry: DSLEntry, entry_file: Path):
    # target_part_path must be a Spec anchor (the first two schemes).
    if entry.target_part_path and "#" not in entry.target_part_path:
        yield Violation(
            rule_id="target-uri-scheme-validity",
            entry_name=entry.name,
            entry_file=entry_file,
            message=(
                f"target_part_path {entry.target_part_path!r} 非 Spec anchor"
                f"（必須 `<spec_file>#<anchor>` 形態）"
            ),
        )
    # Every binding.target must match one of the 5 schemes.
    for src_name, src in (
        ("param_bindings", entry.param_bindings),
        ("datatable_bindings", entry.datatable_bindings),
    ):
        for key, binding in src.items():
            if not _SCHEME_RE.match(binding.target):
                yield Violation(
                    rule_id="target-uri-scheme-validity",
                    entry_name=entry.name,
                    entry_file=entry_file,
                    message=(
                        f"{src_name}[{key}].target {binding.target!r} 不符合任何"
                        f" Target URI scheme（spec anchor / response: / literal: / stub_payload:）"
                    ),
                )


# -- cross-entry rules ------------------------------------------------------


def rule_name_uniqueness(
    entries_by_file: dict[Path, list[DSLEntry]],
    shared_names: set[str],
):
    seen: dict[str, tuple[Path, str]] = {}
    for shared in shared_names:
        seen[shared] = (Path("<shared-dsl>"), "<shared-dsl>")
    for path, entries in entries_by_file.items():
        for entry in entries:
            if entry.name in seen:
                prev_file, prev_name = seen[entry.name]
                yield Violation(
                    rule_id="name-uniqueness",
                    entry_name=entry.name,
                    entry_file=path,
                    message=(
                        f"entry name {entry.name!r} 與 {prev_file} 中之 "
                        f"{prev_name!r} 撞名（含 shared-dsl 範圍）"
                    ),
                )
            else:
                seen[entry.name] = (path, entry.name)


def rule_residual_candidate_comment_block(
    entries_by_file: dict[Path, list[DSLEntry]],
):
    for path in entries_by_file:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _RESIDUAL_CANDIDATE_COMMENT_RE.search(text):
            yield Violation(
                rule_id="residual-candidate-comment-block",
                entry_name="<file-scope>",
                entry_file=path,
                message="仍殘留候選參數註解區塊；SEMANTIC 清理未完成",
                hint="刪除 `# 候選參數...` 與其子註解後再重跑 eval",
            )


# -- driver -----------------------------------------------------------------


_PER_ENTRY_RULES = (
    rule_format_params_cap,
    rule_datatable_cap,
    rule_schema_completeness,
    rule_format_key_binding_bijection,
    rule_target_uri_scheme_validity,
)


def evaluate(
    entries_by_file: dict[Path, list[DSLEntry]],
    shared_names: Iterable[str] = (),
) -> EvalReport:
    violations: list[Violation] = []
    total = 0
    for path, entries in entries_by_file.items():
        for entry in entries:
            total += 1
            for rule in _PER_ENTRY_RULES:
                violations.extend(rule(entry, path))
    violations.extend(rule_name_uniqueness(entries_by_file, set(shared_names)))
    violations.extend(rule_residual_candidate_comment_block(entries_by_file))
    return EvalReport(
        status="PASS" if not violations else "FAIL",
        total_entries=total,
        violations=violations,
    )
