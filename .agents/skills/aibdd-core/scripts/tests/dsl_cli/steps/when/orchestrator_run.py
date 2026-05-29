"""When steps for L4 orchestrator end-to-end features.

The steps invoke run_generate_dsl_instructions / run_eval directly (not via
subprocess) so behave can assert on the returned dataclass values. The CLI
itself is covered by manual smoke testing (per the plan) — the orchestrator
function is the same code path argparse hands off to.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from dsl_cli.orchestrator import run_eval, run_generate_dsl_instructions

# .../when/orchestrator_run.py
# parents: [0] when/ [1] steps/ [2] dsl_cli/ [3] tests/ [4] scripts/ [5] aibdd-core/
_BOUNDARIES_ROOT = Path(__file__).resolve().parents[5] / "assets" / "boundaries"


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


def _spec_paths(context):
    return [
        Path("specs/contracts/room.api.yml"),
        Path("specs/data/data.dbml"),
    ]


def _dsl_paths(context):
    return [
        Path("specs/contracts/room.dsl.yml"),
        Path("specs/data/data.dsl.yml"),
    ]


def _existing_specs(context):
    return [p for p in _spec_paths(context) if (context.tmp_root / p).is_file()]


def _existing_or_seed_dsls(context):
    paths = []
    for p in _dsl_paths(context):
        full = context.tmp_root / p
        if not full.is_file():
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("dsl_steps: []\n")
        paths.append(p)
    return paths


@when('dsl_cli generate-dsl-instructions runs for boundary "{boundary}"')
def step_run_generate(context, boundary: str):
    with _chdir(context.tmp_root):
        context.generation_report = run_generate_dsl_instructions(
            boundary=boundary,
            spec_paths=_existing_specs(context),
            dsl_paths=_existing_or_seed_dsls(context),
            boundaries_root=_BOUNDARIES_ROOT,
        )


@when('dsl_cli generate-dsl-instructions runs again for boundary "{boundary}"')
def step_run_generate_again(context, boundary: str):
    with _chdir(context.tmp_root):
        context.second_generation_report = run_generate_dsl_instructions(
            boundary=boundary,
            spec_paths=_existing_specs(context),
            dsl_paths=_existing_or_seed_dsls(context),
            boundaries_root=_BOUNDARIES_ROOT,
        )


@when("dsl_cli eval runs against the last file")
def step_run_eval(context):
    rel = context.last_file_path.relative_to(context.tmp_root)
    with _chdir(context.tmp_root):
        context.eval_report = run_eval(dsl_paths=[rel])
