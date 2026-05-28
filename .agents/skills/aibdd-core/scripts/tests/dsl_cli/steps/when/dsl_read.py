"""When steps for dsl_reader features."""

from __future__ import annotations

from behave import when

from dsl_cli.dsl_reader import index_resolved_parts, load_dsl_files


@when("dsl_reader loads the last file")
def step_load_last(context):
    loaded = load_dsl_files([context.last_file_path])
    # flatten for assertion convenience
    context.loaded_dsl_by_file = loaded
    context.loaded_entries = loaded[context.last_file_path]


@when('dsl_reader loads files aliased "{a}" and "{b}"')
def step_load_two_aliased(context, a: str, b: str):
    paths = [context.files[a], context.files[b]]
    context.loaded_dsl_by_file = load_dsl_files(paths)
    context.loaded_entries = [
        entry
        for entries in context.loaded_dsl_by_file.values()
        for entry in entries
    ]


@when("index_resolved_parts is computed on the loaded entries")
def step_index_resolved_parts(context):
    context.resolved_parts = index_resolved_parts(context.loaded_dsl_by_file)
