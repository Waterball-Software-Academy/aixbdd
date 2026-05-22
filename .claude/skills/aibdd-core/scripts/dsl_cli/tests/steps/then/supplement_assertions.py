"""Then steps for supplement-required-fields features.

Two assertion families:

  1. DSL file inspection — `dsl entry "<name>" in "<file>" ...`
     Loads the dsl file fresh from disk so we observe the post-supplement
     state (not the entries snapshotted before supplement ran).

  2. SupplementReport inspection — checks the in-memory report parked on
     `context.supplement_report` by the When step.
"""

from __future__ import annotations

from pathlib import Path

from behave import then

from dsl_cli.dsl_reader import load_dsl_files


def _entry(context, dsl_relpath: str, name: str):
    path = context.tmp_root / dsl_relpath
    assert path.is_file(), f"dsl file {dsl_relpath!r} not found at {path}"
    entries = load_dsl_files([path])[path]
    matches = [e for e in entries if e.name == name]
    assert matches, (
        f"no entry named {name!r} in {dsl_relpath!r}; "
        f"got {[e.name for e in entries]}"
    )
    return matches[0]


@then('dsl entry "{name}" in "{dsl_relpath}" has datatable binding "{key}"')
def step_entry_has_dt_binding(context, name: str, dsl_relpath: str, key: str):
    e = _entry(context, dsl_relpath, name)
    assert key in e.datatable_bindings, (
        f"{name}.datatable_bindings missing key {key!r}; "
        f"got {list(e.datatable_bindings)}"
    )


@then(
    'dsl entry "{name}" in "{dsl_relpath}" has no datatable binding "{key}"'
)
def step_entry_has_no_dt_binding(context, name: str, dsl_relpath: str, key: str):
    e = _entry(context, dsl_relpath, name)
    assert key not in e.datatable_bindings, (
        f"{name}.datatable_bindings unexpectedly has key {key!r}; "
        f"value: {e.datatable_bindings[key]!r}"
    )


@then('dsl entry "{name}" in "{dsl_relpath}" has empty datatable_bindings')
def step_entry_empty_dt(context, name: str, dsl_relpath: str):
    e = _entry(context, dsl_relpath, name)
    assert not e.datatable_bindings, (
        f"{name}.datatable_bindings expected empty, "
        f"got {dict(e.datatable_bindings)!r}"
    )


@then(
    'dsl entry "{name}" in "{dsl_relpath}" datatable binding "{key}" '
    'has required "{required_str:w}"'
)
def step_dt_required(
    context, name: str, dsl_relpath: str, key: str, required_str: str
):
    e = _entry(context, dsl_relpath, name)
    assert key in e.datatable_bindings, (
        f"{name}.datatable_bindings missing key {key!r}"
    )
    expected = required_str.lower() == "true"
    actual = e.datatable_bindings[key].required
    assert actual == expected, (
        f"{name}.datatable_bindings[{key}].required: "
        f"expected {expected}, got {actual}"
    )


@then(
    'dsl entry "{name}" in "{dsl_relpath}" datatable binding "{key}" '
    'has target "{expected}"'
)
def step_dt_target(
    context, name: str, dsl_relpath: str, key: str, expected: str
):
    e = _entry(context, dsl_relpath, name)
    assert key in e.datatable_bindings
    actual = e.datatable_bindings[key].target
    assert actual == expected, (
        f"{name}.datatable_bindings[{key}].target: "
        f"expected {expected!r}, got {actual!r}"
    )


@then(
    'dsl entry "{name}" in "{dsl_relpath}" datatable binding "{key}" '
    'has default_value "{expected}"'
)
def step_dt_default_value(
    context, name: str, dsl_relpath: str, key: str, expected: str
):
    e = _entry(context, dsl_relpath, name)
    assert key in e.datatable_bindings
    actual = e.datatable_bindings[key].default_value
    assert actual == expected, (
        f"{name}.datatable_bindings[{key}].default_value: "
        f"expected {expected!r}, got {actual!r}"
    )


# ---- SupplementReport ----


@then("SupplementReport contains {n:d} supplemented field")
@then("SupplementReport contains {n:d} supplemented fields")
def step_report_supplemented_count(context, n: int):
    actual = len(context.supplement_report.supplemented_fields)
    assert actual == n, (
        f"SupplementReport.supplemented_fields: expected {n}, got {actual}; "
        f"items: {context.supplement_report.supplemented_fields}"
    )


@then(
    'SupplementReport supplemented "{key}" into entry "{name}" '
    'in "{dsl_relpath}"'
)
def step_report_supplemented_record(
    context, key: str, name: str, dsl_relpath: str
):
    target_path = Path(dsl_relpath)
    matches = [
        s
        for s in context.supplement_report.supplemented_fields
        if s.field_key == key
        and s.entry_name == name
        and Path(s.dsl_file) == target_path
    ]
    assert matches, (
        f"SupplementReport missing supplemented record "
        f"(key={key!r}, entry={name!r}, file={dsl_relpath!r}); "
        f"got {context.supplement_report.supplemented_fields}"
    )


@then("SupplementReport contains {n:d} skipped entry")
@then("SupplementReport contains {n:d} skipped entries")
def step_report_skipped_count(context, n: int):
    actual = len(context.supplement_report.skipped_entries)
    assert actual == n, (
        f"SupplementReport.skipped_entries: expected {n}, got {actual}; "
        f"items: {context.supplement_report.skipped_entries}"
    )


@then(
    'SupplementReport skipped entry "{name}" in "{dsl_relpath}" '
    'with reason "{reason}"'
)
def step_report_skipped_record(
    context, name: str, dsl_relpath: str, reason: str
):
    target_path = Path(dsl_relpath)
    matches = [
        sk
        for sk in context.supplement_report.skipped_entries
        if sk.entry_name == name
        and Path(sk.dsl_file) == target_path
        and sk.reason == reason
    ]
    assert matches, (
        f"SupplementReport missing skipped record "
        f"(entry={name!r}, file={dsl_relpath!r}, reason={reason!r}); "
        f"got {context.supplement_report.skipped_entries}"
    )
