"""Then steps for dsl_cli query features."""

from __future__ import annotations

import json

from behave import then

from dsl_cli.reporter import render_query_json


@then("query match output should equal:")
def step_query_match_output_equals(context):
    expected = json.loads(context.text or "[]")
    actual = json.loads(render_query_json(context.query_matches))
    assert actual == expected, f"expected query output {expected!r}, got {actual!r}"


@then("query match output should equal the previous query match output")
def step_query_match_output_equals_previous(context):
    previous = json.loads(render_query_json(context.previous_query_matches))
    actual = json.loads(render_query_json(context.query_matches))
    assert actual == previous, f"expected query output {previous!r}, got {actual!r}"
