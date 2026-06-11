"""Additional Given steps for dsl_to_isa suite."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from behave import given

_TESTS_DIR = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _TESTS_DIR.parent  # tests/.. = scripts/
_CLI = _SCRIPTS_DIR / "cli" / "dsl_to_isa.py"


@given("the env var BOUNDARY_SHARED_DSL is unset")
def step_unset_boundary_shared_dsl(context):
    context.env_overrides["BOUNDARY_SHARED_DSL"] = None


@given("TRUTH_BOUNDARY_PACKAGES_DIR contains no dsl.yml")
def step_empty_packages_dir(context):
    context.empty_packages_dir = True


@given('the file at "{relpath}" is replaced with content')
@given('the file at "{relpath}" is replaced with content:')
def step_replace_file_with_content(context, relpath: str):
    target = context.tmp_root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(context.text)


@given("dsl_to_isa has translated the last dsl file")
def step_given_translate_last_dsl(context):
    """Alias that triggers translation inside a Given block (for idempotent-write setup)."""
    _run_translate(context, context.last_file_path)


def _build_env(context, dsl_path=None):
    """Build the env dict for the subprocess."""
    env = os.environ.copy()
    tmp = context.tmp_root

    env["CONTRACTS_DIR"] = str(tmp / "contracts")
    env["DATA_DIR"] = str(tmp / "data")

    # Apply BOUNDARY_SHARED_DSL
    if "BOUNDARY_SHARED_DSL" in context.env_overrides:
        val = context.env_overrides["BOUNDARY_SHARED_DSL"]
        if val is None:
            env.pop("BOUNDARY_SHARED_DSL", None)
        else:
            env["BOUNDARY_SHARED_DSL"] = val
    elif dsl_path is not None:
        env["BOUNDARY_SHARED_DSL"] = str(dsl_path)
    else:
        env.pop("BOUNDARY_SHARED_DSL", None)

    # Apply TRUTH_BOUNDARY_PACKAGES_DIR
    if context.empty_packages_dir:
        empty_dir = tmp / "_empty_specs"
        empty_dir.mkdir(parents=True, exist_ok=True)
        env["TRUTH_BOUNDARY_PACKAGES_DIR"] = str(empty_dir)
    elif dsl_path is None:
        # Use specs dir if it exists
        specs_dir = tmp / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)
        env["TRUTH_BOUNDARY_PACKAGES_DIR"] = str(specs_dir)
    else:
        env.pop("TRUTH_BOUNDARY_PACKAGES_DIR", None)

    return env


def _run_translate(context, dsl_path=None):
    env = _build_env(context, dsl_path)
    result = subprocess.run(
        [sys.executable, str(_CLI)],
        env=env,
        capture_output=True,
        text=True,
    )
    context.last_run = result
