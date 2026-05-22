"""When steps for supplement-required-fields end-to-end features.

Auto-discovers spec / dsl files from `context.tmp_root` via rglob so feature
files don't need to encode paths in the step text. Runs the supplement core
function in-process and parks the SupplementReport on the context.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from behave import when

from dsl_cli.supplement import run_supplement


@contextmanager
def _chdir(target: Path):
    prev = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(prev)


def _discover_specs(root: Path) -> list[Path]:
    specs: list[Path] = []
    specs.extend(sorted(root.rglob("*.api.yml")))
    specs.extend(sorted(root.rglob("*.openapi.yml")))
    specs.extend(sorted(root.rglob("*.dbml")))
    return [p.relative_to(root) for p in specs]


def _discover_dsl(root: Path) -> list[Path]:
    return [p.relative_to(root) for p in sorted(root.rglob("*.dsl.yml"))]


@when("dsl_cli supplement-required-fields runs")
def step_run_supplement(context):
    with _chdir(context.tmp_root):
        context.supplement_report = run_supplement(
            spec_paths=_discover_specs(context.tmp_root),
            dsl_paths=_discover_dsl(context.tmp_root),
        )
