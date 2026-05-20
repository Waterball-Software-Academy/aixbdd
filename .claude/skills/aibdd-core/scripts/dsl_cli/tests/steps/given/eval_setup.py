"""Given steps that prep a DSL corpus + run evaluator for eval-rules features."""

from __future__ import annotations

from behave import given

from dsl_cli.dsl_reader import load_dsl_files


def _write_and_load(context, relpath: str):
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text)
    context.last_file_path = target
    context.eval_dsl_paths = getattr(context, "eval_dsl_paths", [])
    context.eval_dsl_paths.append(target)
    context.eval_entries_by_file = load_dsl_files(context.eval_dsl_paths)


@given('the following DSL entries in "{relpath}"')
@given('the following DSL entries in "{relpath}":')
def step_given_entries_in_file(context, relpath: str):
    _write_and_load(context, relpath)


@given("a shared DSL namespace containing")
@given("a shared DSL namespace containing:")
def step_given_shared_namespace(context):
    context.eval_shared_names = {row["name"] for row in context.table}
