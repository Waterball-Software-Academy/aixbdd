"""Impact-matrix BDD step definitions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from behave import given, then, when

from lib.impact_matrix import (
    delete_entry,
    filter_entries,
    init_matrix,
    list_entries,
    load_matrix,
    repo_root_from_module,
    upsert_entry,
    validate_matrix,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]
_CLI = _SCRIPTS_DIR / "cli" / "manage_impact_matrix.py"


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _format_questions(questions) -> str:
    lines: list[str] = []
    for q in questions:
        lines.append(f"- where: {q.where}")
        lines.append(f"  type: {q.type}")
        lines.append(f"  text: {q.text}")
    return "\n".join(lines)


def _build_query_args(
    *,
    suffix: str | None = None,
    change_types: str | None = None,
    path_prefix: str | None = None,
) -> list[str]:
    args = ["query"]
    if suffix is not None:
        args.extend(["--suffix", suffix])
    if change_types:
        for change_type in change_types.split(","):
            args.extend(["--change-type", change_type.strip()])
    if path_prefix is not None:
        args.extend(["--path-prefix", path_prefix])
    return args


@given("an impact matrix file at the default test path")
def step_default_matrix_path(context):
    context.matrix_path.parent.mkdir(parents=True, exist_ok=True)


@given('an impact matrix file at "{relpath}" with content:')
def step_create_matrix_with_content(context, relpath: str):
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.matrix_path = target


@when("impact matrix init is run on the default test path")
def step_init_matrix(context):
    init_matrix(context.matrix_path)


@when(
    'impact matrix upsert is run with path "{entry_path}" '
    'change_type "{change_type}" impact_summary "{impact_summary}"'
)
@given(
    'impact matrix upsert is run with path "{entry_path}" '
    'change_type "{change_type}" impact_summary "{impact_summary}"'
)
def step_upsert_matrix(context, entry_path: str, change_type: str, impact_summary: str):
    upsert_entry(
        context.matrix_path,
        entry_path=entry_path,
        change_type=change_type,
        impact_summary=impact_summary,
    )


@when('impact matrix delete is run with path "{entry_path}"')
def step_delete_matrix(context, entry_path: str):
    delete_entry(context.matrix_path, entry_path=entry_path)


@when("impact matrix validate is run on the default test path")
def step_validate_matrix(context):
    data = load_matrix(context.matrix_path)
    try:
        matrix_label = context.matrix_path.relative_to(context.tmp_root).as_posix()
    except ValueError:
        matrix_label = context.matrix_path.name
    context.last_questions, _ = validate_matrix(data, matrix_path=matrix_label)


@when(
    'impact matrix query is run with suffix "{suffix}" change_types "{change_types}" '
    'path_prefix "{path_prefix}"'
)
def step_query_matrix(context, suffix: str, change_types: str, path_prefix: str):
    data = load_matrix(context.matrix_path)
    parsed_change_types = (
        [value.strip() for value in change_types.split(",") if value.strip()]
        if change_types.strip() not in {"", "-"}
        else None
    )
    parsed_path_prefix = path_prefix.strip() if path_prefix.strip() not in {"", "-"} else None
    parsed_suffix = suffix.strip() if suffix.strip() not in {"", "-"} else None
    context.last_queried_entries = filter_entries(
        data,
        suffix=parsed_suffix,
        change_types=parsed_change_types,
        path_prefix=parsed_path_prefix,
    )


@when('impact matrix query is run with path_prefix "{path_prefix}"')
def step_query_path_prefix_only(context, path_prefix: str):
    data = load_matrix(context.matrix_path)
    context.last_queried_entries = filter_entries(data, path_prefix=path_prefix)


@when("manage_impact_matrix CLI init is run on the default test path")
def step_cli_init(context):
    proc = subprocess.run(
        ["python3", str(_CLI), "--matrix", str(context.matrix_path), "init"],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


@when(
    'manage_impact_matrix CLI upsert is run with path "{entry_path}" '
    'change_type "{change_type}" impact_summary "{impact_summary}"'
)
def step_cli_upsert(context, entry_path: str, change_type: str, impact_summary: str):
    proc = subprocess.run(
        [
            "python3",
            str(_CLI),
            "--matrix",
            str(context.matrix_path),
            "upsert",
            "--path",
            entry_path,
            "--change-type",
            change_type,
            "--impact-summary",
            impact_summary,
        ],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


@given("project arguments bind IMPACT_MATRIX_YML to the default test matrix path")
def step_bind_project_arguments(context):
    args_dir = context.tmp_root / ".aibdd"
    args_dir.mkdir(parents=True, exist_ok=True)
    rel = context.matrix_path.relative_to(context.tmp_root).as_posix()
    (args_dir / "arguments.yml").write_text(
        f"IMPACT_MATRIX_YML: {rel}\n",
        encoding="utf-8",
    )


@when('manage_impact_matrix CLI query is run with suffix "{suffix}" from project CWD without matrix flag')
def step_cli_query_from_project_cwd(context, suffix: str):
    proc = subprocess.run(
        [
            "python3",
            str(_CLI),
            *_build_query_args(suffix=suffix),
        ],
        capture_output=True,
        text=True,
        cwd=context.tmp_root,
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


@when(
    'manage_impact_matrix CLI query is run with suffix "{suffix}" '
    'change_types "{change_types}" path_prefix "{path_prefix}"'
)
def step_cli_query_with_filters(
    context, suffix: str, change_types: str, path_prefix: str
):
    proc = subprocess.run(
        [
            "python3",
            str(_CLI),
            "--matrix",
            str(context.matrix_path),
            *_build_query_args(
                suffix=suffix,
                change_types=change_types,
                path_prefix=path_prefix,
            ),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


@when('manage_impact_matrix CLI query is run with suffix "{suffix}"')
def step_cli_query_suffix(context, suffix: str):
    proc = subprocess.run(
        [
            "python3",
            str(_CLI),
            "--matrix",
            str(context.matrix_path),
            *_build_query_args(suffix=suffix),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.stdout.strip() else None


@then("the impact matrix YAML should equal:")
def step_matrix_yaml_equals(context):
    actual = context.matrix_path.read_text(encoding="utf-8")
    assert _normalize_text(actual) == _normalize_text(context.text)


@then("impact matrix entries should equal:")
def step_entries_equal(context):
    data = load_matrix(context.matrix_path)
    actual = json.dumps(list_entries(data), ensure_ascii=False, indent=2)
    assert _normalize_text(actual) == _normalize_text(context.text)


@then("impact matrix validation questions should equal:")
def step_questions_equal(context):
    actual = _format_questions(context.last_questions)
    assert _normalize_text(actual) == _normalize_text(context.text)


@then("queried impact matrix entries should equal:")
def step_queried_entries_equal(context):
    actual = json.dumps(context.last_queried_entries, ensure_ascii=False, indent=2)
    assert _normalize_text(actual) == _normalize_text(context.text)


@then("CLI exit code is {code:d}")
def step_cli_exit_code(context, code: int):
    assert context.last_result.returncode == code


@then("CLI impact matrix JSON report should equal:")
def step_cli_json_equals(context):
    actual = json.dumps(context.last_json, ensure_ascii=False, indent=2, sort_keys=True)
    expected = json.dumps(json.loads(context.text), ensure_ascii=False, indent=2, sort_keys=True)
    assert actual == expected
