"""When steps for dsl_cli query features."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from dsl_cli.orchestrator import run_query


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


def _parse_handlers(handlers: str | None) -> list[str] | None:
    if handlers is None:
        return None
    handler_list = [item.strip() for item in handlers.split(",") if item.strip()]
    return handler_list if handler_list else None


@when('dsl_cli query runs with handlers "{handlers}" against the last file')
def step_query_last_file(context, handlers: str):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query([rel], _parse_handlers(handlers))


@when(
    'dsl_cli query runs with handlers "{handlers}" against files aliased "{a}" and "{b}"'
)
def step_query_two_files(context, handlers: str, a: str, b: str):
    paths = [
        context.files[a].relative_to(context.tmp_root),
        context.files[b].relative_to(context.tmp_root),
    ]
    with _chdir(context.tmp_root):
        context.query_matches = run_query(paths, _parse_handlers(handlers))


@when(
    'dsl_cli query runs with handlers "{handlers}" and source-scope "{scope}" '
    'against regular file alias "{regular}" and shared file alias "{shared}"'
)
def step_query_with_scope(context, handlers: str, scope: str, regular: str, shared: str):
    regular_path = context.files[regular].relative_to(context.tmp_root)
    shared_path = context.files[shared].relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query(
            [regular_path],
            _parse_handlers(handlers),
            shared_dsl_path=shared_path,
            source_scope=scope,
        )


@when(
    'dsl_cli query runs with handler "{handler}" and source-scope "shared" against shared alias "{shared}"'
)
def step_query_shared_only(context, handler: str, shared: str):
    shared_path = context.files[shared].relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query(
            [],
            [handler],
            shared_dsl_path=shared_path,
            source_scope="shared",
        )


@when('dsl_cli query runs with step-text "{step_text}" against the last file')
def step_query_by_step_text_last_file(context, step_text: str):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query([rel], step_text=step_text)


@when(
    'dsl_cli step-text query runs with handlers "{handlers}" and text "{step_text}" against the last file'
)
def step_query_by_step_text_and_handlers(context, handlers: str, step_text: str):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query(
            [rel],
            _parse_handlers(handlers),
            step_text=step_text,
        )


@when(
    'dsl_cli query runs with step-text "{step_text}" against files aliased "{a}" and "{b}"'
)
def step_query_by_step_text_two_files(context, step_text: str, a: str, b: str):
    paths = [
        context.files[a].relative_to(context.tmp_root),
        context.files[b].relative_to(context.tmp_root),
    ]
    with _chdir(context.tmp_root):
        context.query_matches = run_query(paths, step_text=step_text)


@when(
    'dsl_cli query runs with step-text "{step_text}" and source-scope "shared" against shared alias "{shared}"'
)
def step_query_by_step_text_shared_only(context, step_text: str, shared: str):
    shared_path = context.files[shared].relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query(
            [],
            step_text=step_text,
            shared_dsl_path=shared_path,
            source_scope="shared",
        )


@when(
    'dsl_cli query runs with step-text "{step_text}" and source-scope "all" '
    'against regular file alias "{regular}" and shared file alias "{shared}"'
)
def step_query_by_step_text_with_scope_all(
    context, step_text: str, regular: str, shared: str
):
    regular_path = context.files[regular].relative_to(context.tmp_root)
    shared_path = context.files[shared].relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.query_matches = run_query(
            [regular_path],
            step_text=step_text,
            shared_dsl_path=shared_path,
            source_scope="all",
        )


@when(
    'dsl_cli query runs with step-text "{step_text}" against the last file again'
)
def step_query_by_step_text_last_file_again(context, step_text: str):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.previous_query_matches = context.query_matches
        context.query_matches = run_query([rel], step_text=step_text)
