"""Then steps asserting on the list of Parts the parser produced."""

from __future__ import annotations

from behave import then


def _single_part(context):
    assert len(context.parts) == 1, (
        f"expected exactly 1 part for these single-operation features; got {len(context.parts)}"
    )
    return context.parts[0]


@then('exactly {count:d} part of kind "{kind}" is returned')
@then('exactly {count:d} parts of kind "{kind}" are returned')
def step_assert_part_count_and_kind(context, count: int, kind: str):
    matching = [p for p in context.parts if p.kind.value == kind]
    assert len(matching) == count, (
        f"expected {count} parts of kind {kind!r}; got {len(matching)} "
        f"(all parts: {[p.kind.value for p in context.parts]})"
    )


@then('the part\'s path is "{expected}"')
def step_assert_part_path(context, expected: str):
    assert _single_part(context).path == expected


@then('the part\'s method is "{expected}"')
def step_assert_part_method(context, expected: str):
    assert _single_part(context).method == expected


@then('the part\'s operation_id is "{expected}"')
def step_assert_part_operation_id(context, expected: str):
    assert _single_part(context).operation_id == expected


@then('the part\'s target_part_path is "{expected}"')
def step_assert_target_part_path(context, expected: str):
    assert _single_part(context).target_part_path == expected, (
        f"target_part_path mismatch:\n  expected: {expected}\n  actual:   {_single_part(context).target_part_path}"
    )


@then("the part's request_inputs has entries")
@then("the part's request_inputs has entries:")
def step_assert_request_inputs(context):
    part = _single_part(context)
    actual = {ri.name: ri for ri in part.request_inputs}
    for row in context.table:
        name = row["name"]
        assert name in actual, f"missing request_input {name!r}; got {list(actual)}"
        ri = actual[name]
        if "source" in row.headings:
            assert ri.source == row["source"], (
                f"request_input {name}.source: expected {row['source']!r}, got {ri.source!r}"
            )
        if "required" in row.headings:
            expected_req = row["required"].strip().lower() == "true"
            assert ri.required == expected_req, (
                f"request_input {name}.required: expected {expected_req}, got {ri.required}"
            )


@then('the request_input named "{name}" has target_part_path "{expected}"')
def step_assert_request_input_target(context, name: str, expected: str):
    part = _single_part(context)
    matches = [ri for ri in part.request_inputs if ri.name == name]
    assert matches, f"no request_input named {name!r}"
    assert matches[0].target_part_path == expected, (
        f"request_input {name}.target_part_path mismatch:\n"
        f"  expected: {expected}\n"
        f"  actual:   {matches[0].target_part_path}"
    )


@then("the part's response_properties has entries")
@then("the part's response_properties has entries:")
def step_assert_response_properties(context):
    part = _single_part(context)
    actual = {rp.name: rp for rp in part.response_properties}
    for row in context.table:
        name = row["name"]
        assert name in actual, f"missing response_property {name!r}; got {list(actual)}"
        rp = actual[name]
        if "json_path" in row.headings:
            assert rp.json_path == row["json_path"], (
                f"response_property {name}.json_path: expected {row['json_path']!r}, got {rp.json_path!r}"
            )


@then('the response_property named "{name}" has target_part_path "{expected}"')
def step_assert_response_property_target(context, name: str, expected: str):
    part = _single_part(context)
    matches = [rp for rp in part.response_properties if rp.name == name]
    assert matches, f"no response_property named {name!r}"
    assert matches[0].target_part_path == expected


# ---- DBML-flavoured assertions (work by table_name, not single-part) ----


def _part_by_table_name(context, table_name: str):
    matches = [p for p in context.parts if getattr(p, "table_name", None) == table_name]
    assert matches, f"no dbml_table part named {table_name!r}; got {[getattr(p, 'table_name', '?') for p in context.parts]}"
    return matches[0]


def _part_by_ref(context, ref_text: str):
    parts = [
        p
        for p in context.parts
        if getattr(getattr(p, "kind", None), "value", None) == "dbml_ref"
        and (
            f"{getattr(p, 'from_table', '')}.{getattr(p, 'from_column', '')} "
            f"{getattr(p, 'operator', '')} "
            f"{getattr(p, 'to_table', '')}.{getattr(p, 'to_column', '')}"
        )
        == ref_text
    ]
    assert parts, (
        f"no dbml_ref part {ref_text!r}; got "
        f"{[p.target_part_path for p in context.parts if getattr(getattr(p, 'kind', None), 'value', None) == 'dbml_ref']}"
    )
    return parts[0]


@then('the part named "{name}" has target_part_path "{expected}"')
def step_assert_named_part_target(context, name: str, expected: str):
    part = _part_by_table_name(context, name)
    assert part.target_part_path == expected, (
        f"{name}.target_part_path mismatch:\n  expected: {expected}\n  actual:   {part.target_part_path}"
    )


@then('the ref part "{ref_text}" has target_part_path "{expected}"')
def step_assert_ref_part_target(context, ref_text: str, expected: str):
    part = _part_by_ref(context, ref_text)
    assert part.target_part_path == expected, (
        f"{ref_text}.target_part_path mismatch:\n  expected: {expected}\n  actual:   {part.target_part_path}"
    )


@then('the part named "{name}" has columns')
@then('the part named "{name}" has columns:')
def step_assert_columns(context, name: str):
    part = _part_by_table_name(context, name)
    cols_by_name = {c.name: c for c in part.columns}
    for row in context.table:
        col_name = row["name"]
        assert col_name in cols_by_name, (
            f"{name}: missing column {col_name!r}; got {list(cols_by_name)}"
        )
        col = cols_by_name[col_name]
        _maybe_assert(col, row, "type", lambda c: c.type)
        _maybe_assert_bool(col, row, "nullable", lambda c: c.nullable)
        _maybe_assert_bool(col, row, "is_pk", lambda c: c.is_pk)
        _maybe_assert_bool(col, row, "has_default", lambda c: c.has_default)


@then('the part named "{name}" has not_null_columns')
@then('the part named "{name}" has not_null_columns:')
def step_assert_not_null_columns(context, name: str):
    part = _part_by_table_name(context, name)
    actual_names = [c.name for c in part.not_null_columns]
    expected_names = [row["name"] for row in context.table]
    assert actual_names == expected_names, (
        f"{name}.not_null_columns: expected {expected_names}, got {actual_names}"
    )


@then('the column "{table}.{col}" has target_part_path "{expected}"')
def step_assert_column_target(context, table: str, col: str, expected: str):
    part = _part_by_table_name(context, table)
    matches = [c for c in part.columns if c.name == col]
    assert matches, f"{table}: no column named {col!r}"
    assert matches[0].target_part_path == expected, (
        f"{table}.{col}.target_part_path mismatch:\n  expected: {expected}\n  actual:   {matches[0].target_part_path}"
    )


@then('the column "{table}.{col}" has has_increment {expected}')
def step_assert_column_has_increment(context, table: str, col: str, expected: str):
    part = _part_by_table_name(context, table)
    matches = [c for c in part.columns if c.name == col]
    assert matches, f"{table}: no column named {col!r}"
    expected_bool = expected.strip().lower() == "true"
    assert matches[0].has_increment == expected_bool, (
        f"{table}.{col}.has_increment: expected {expected_bool}, got {matches[0].has_increment}"
    )


@then('the column "{table}.{col}" has has_default {expected}')
def step_assert_column_has_default(context, table: str, col: str, expected: str):
    part = _part_by_table_name(context, table)
    matches = [c for c in part.columns if c.name == col]
    assert matches, f"{table}: no column named {col!r}"
    expected_bool = expected.strip().lower() == "true"
    assert matches[0].has_default == expected_bool, (
        f"{table}.{col}.has_default: expected {expected_bool}, got {matches[0].has_default}"
    )


@then('the column "{table}.{col}" has default_value "{expected}"')
def step_assert_column_default_value(context, table: str, col: str, expected: str):
    part = _part_by_table_name(context, table)
    matches = [c for c in part.columns if c.name == col]
    assert matches, f"{table}: no column named {col!r}"
    actual = matches[0].default_value
    assert actual == expected, (
        f"{table}.{col}.default_value: expected {expected!r}, got {actual!r}"
    )


@then('the column "{table}.{col}" has default_value null')
def step_assert_column_default_value_null(context, table: str, col: str):
    part = _part_by_table_name(context, table)
    matches = [c for c in part.columns if c.name == col]
    assert matches, f"{table}: no column named {col!r}"
    actual = matches[0].default_value
    assert actual is None, (
        f"{table}.{col}.default_value: expected None, got {actual!r}"
    )


def _maybe_assert(col, row, heading: str, getter):
    if heading not in row.headings:
        return
    expected = row[heading]
    actual = getter(col)
    assert actual == expected, (
        f"column {col.name}.{heading}: expected {expected!r}, got {actual!r}"
    )


def _maybe_assert_bool(col, row, heading: str, getter):
    if heading not in row.headings:
        return
    expected = row[heading].strip().lower() == "true"
    actual = getter(col)
    assert actual == expected, (
        f"column {col.name}.{heading}: expected {expected}, got {actual}"
    )
