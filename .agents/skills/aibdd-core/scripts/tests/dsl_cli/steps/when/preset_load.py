"""When steps for preset_loader L1 features.

`boundaries/` lives at `context.tmp_root / 'boundaries'`. The loader is invoked
with that path directly — no chdir needed since the loader is purely
path-based and doesn't read cwd.
"""

from __future__ import annotations

from behave import when

from dsl_cli.preset_loader import load_preset_plugin


def _boundaries_root(context):
    return context.tmp_root / "boundaries"


@when('preset_loader loads "{preset}"')
def step_load_preset(context, preset: str):
    context.loaded_module = load_preset_plugin(preset, _boundaries_root(context))
    context.loaded_modules_history = getattr(context, "loaded_modules_history", [])
    context.loaded_modules_history.append(context.loaded_module)


@when('preset_loader loads "{preset}" again')
def step_load_preset_again(context, preset: str):
    again = load_preset_plugin(preset, _boundaries_root(context))
    context.loaded_modules_history.append(again)


@when('preset_loader loads "{preset}" and captures the exception')
def step_load_preset_capturing(context, preset: str):
    try:
        load_preset_plugin(preset, _boundaries_root(context))
    except Exception as exc:
        context.captured_exception = exc
        return
    context.captured_exception = None
