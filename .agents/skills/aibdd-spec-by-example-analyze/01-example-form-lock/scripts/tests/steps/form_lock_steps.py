"""Form-lock BDD step definitions."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from behave import given, then, when

from lib.form_lock import (
    CORE_BOUNDARIES_ROOT,
    SBE_FORM_LOCK_DIR,
    apply_in_place_update,
    load_profile_from_path,
    repo_root_from_module,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[2]


def _write_file(context, relpath: str) -> Path:
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.last_file_path = target
    return target


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


def _format_unknown_prefix_questions(questions) -> str:
    lines: list[str] = []
    for q in questions:
        lines.append(f"- where: {q.path.name}:{q.line_no}")
        lines.append(f"  type: {q.prefix}")
        lines.append(
            "  text: unknown rule type prefix "
            f"`{q.prefix}`; must match form-lock.profile.yml rule_prefix_to_template"
        )
    return "\n".join(lines)


@given("the web-service form-lock profile from repo assets")
def step_load_repo_web_service_profile(context):
    profile_path = (
        CORE_BOUNDARIES_ROOT
        / "web-service"
        / SBE_FORM_LOCK_DIR
        / "form-lock.profile.yml"
    )
    context.files["profile_path"] = profile_path
    context.last_config = load_profile_from_path(profile_path)


@given('a boundary.yml at "{relpath}" with content')
@given('a boundary.yml at "{relpath}" with content:')
def step_create_boundary_yml(context, relpath: str):
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.files["boundary_yml"] = target


@given('a form-lock profile at "{relpath}" with content')
@given('a form-lock profile at "{relpath}" with content:')
def step_create_profile_yml(context, relpath: str):
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text, encoding="utf-8")
    context.files["profile_path"] = target


@given("canonical web-service templates are copied beside the profile")
def step_copy_web_service_templates(context):
    profile_path: Path = context.files["profile_path"]
    src_sbe_form_lock_dir = CORE_BOUNDARIES_ROOT / "web-service" / SBE_FORM_LOCK_DIR
    dst_sbe_form_lock_dir = profile_path.parent
    for name in (
        "precondition-state.tmpl",
        "precondition-param.tmpl",
        "postcondition-response.tmpl",
        "postcondition-state.tmpl",
    ):
        shutil.copyfile(src_sbe_form_lock_dir / name, dst_sbe_form_lock_dir / name)


@given("a minimal precondition-state template beside the profile")
def step_minimal_template(context):
    profile_path: Path = context.files["profile_path"]
    tmpl = profile_path.parent / "precondition-state.tmpl"
    tmpl.write_text(
        'Rule: 前置（狀態） - x\n\n  Example: test skeleton\n    # @dsl\n    Given <dsl>\n',
        encoding="utf-8",
    )
    context.files["template_path"] = tmpl


@given('a temporary file at "{relpath}" with content')
@given('a temporary file at "{relpath}" with content:')
def step_create_temp_file_with_content(context, relpath: str):
    _write_file(context, relpath)


@given("form-lock apply is run on the last feature file")
@when("form-lock apply is run on the last feature file")
def step_apply_form_lock(context):
    config = context.last_config
    if config is None and "profile_path" in context.files:
        config = load_profile_from_path(context.files["profile_path"])
        context.last_config = config
    path = context.last_file_path
    context.last_questions = []
    context.last_changed = apply_in_place_update(path, config, context.last_questions)


@when("form-lock apply is run again on the last feature file")
def step_apply_form_lock_again(context):
    step_apply_form_lock(context)


@when("load_form_lock_profile CLI is run on the profile path")
def step_run_loader_cli(context):
    profile_path = context.files["profile_path"]
    script = _SCRIPTS_DIR / "cli" / "load_form_lock_profile.py"
    proc = subprocess.run(
        ["python3", str(script), "--profile-path", str(profile_path)],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.returncode == 0 else None


@when("apply_form_lock CLI is run on the last feature file")
def step_run_apply_cli(context):
    profile_path = context.files["profile_path"]
    feature_path = context.last_file_path
    script = _SCRIPTS_DIR / "cli" / "apply_form_lock.py"
    proc = subprocess.run(
        [
            "python3",
            str(script),
            str(feature_path),
            "--profile-path",
            str(profile_path),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root_from_module(),
    )
    context.last_result = proc
    context.last_json = json.loads(proc.stdout) if proc.returncode == 0 else None


@then('boundary_type is "{expected}"')
def step_boundary_type(context, expected: str):
    assert context.last_config.boundary_type == expected


@then("rule prefixes are sorted longest-first")
def step_prefixes_sorted(context):
    prefixes = [p for p, _ in context.last_config.rule_prefix_to_template]
    lengths = [len(p) for p in prefixes]
    assert lengths == sorted(lengths, reverse=True)


@then("CLI exit code is 0")
def step_cli_ok(context):
    assert context.last_result.returncode == 0


@then('CLI JSON boundary_type is "{expected}"')
def step_cli_boundary_type(context, expected: str):
    assert context.last_json["boundary_type"] == expected


@then("CLI JSON projection should equal:")
def step_cli_json_projection_equals(context):
    expected = json.loads(context.text or "{}")
    actual = {
        "boundary_type": context.last_json["boundary_type"],
        "rule_prefix_to_template": context.last_json["rule_prefix_to_template"],
    }
    assert actual == expected


@then("CLI apply JSON report should equal:")
def step_cli_apply_json_report_equals(context):
    expected = json.loads(context.text or "{}")
    assert context.last_json == expected


@then('no file exists at "{relpath}"')
def step_no_file_exists(context, relpath: str):
    assert not (context.tmp_root / relpath).exists()


@then("the last feature file content should equal:")
def step_feature_content_equals(context):
    actual = context.last_file_path.read_text(encoding="utf-8")
    expected = context.text or ""
    assert _normalize_text(actual) == _normalize_text(expected)


@then("unknown prefix questions should equal:")
def step_unknown_prefix_questions_equal(context):
    actual = _format_unknown_prefix_questions(context.last_questions)
    expected = context.text or ""
    assert _normalize_text(actual) == _normalize_text(expected)
