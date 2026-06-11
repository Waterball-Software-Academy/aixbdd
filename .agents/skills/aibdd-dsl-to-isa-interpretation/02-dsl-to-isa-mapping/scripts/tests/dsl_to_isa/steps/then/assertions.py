"""Then assertion steps for dsl_to_isa suite.

All assertion steps catch low-level Python errors (IndexError, KeyError, etc.)
and re-raise them as AssertionError with a clear "expected X, got Y" message.
This ensures Legal Red — failures are always assertion diffs, never tracebacks.

Behave 1.3 quirk: step matchers that accept a doc string must be decorated with
both the colon and no-colon variants (see _shared/fixtures.py comment).
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

from behave import then
from ruamel.yaml import YAML

_yaml = YAML()
_yaml.preserve_quotes = True

# Add lib dir to path so we can import the shared preprocessor
_TESTS_DIR = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _TESTS_DIR.parent  # tests/.. = scripts/
_LIB_DIR = _SCRIPTS_DIR / "lib"
for _p in (_LIB_DIR, _SCRIPTS_DIR):
    _ps = str(_p)
    if _ps not in sys.path:
        sys.path.insert(0, _ps)

from dsl_to_isa.orchestrator import fix_flow_map_values  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml_with_preprocessor(path: Path):
    """Load YAML file applying the DSL flow-map brace fix.

    Mirrors orchestrator._load_yaml_file so fixture YAML containing
    `{ target: some/{param}/path }` parses cleanly.
    """
    raw = path.read_text(encoding="utf-8")
    return _yaml.load(fix_flow_map_values(raw))


def _parse_keys_literal(text: str) -> list[str]:
    """Parse a JSON-array-like literal such as '["a", "b"]' or '[]'."""
    text = text.strip()
    if text in ("[]", "[ ]"):
        return []
    inner = text.strip("[]")
    parts = [p.strip().strip('"').strip("'") for p in inner.split(",")]
    return [p for p in parts if p]


def _find_dsl_files(context) -> list[Path]:
    """Collect dsl corpus files under tmp_root (`dsl.yml` and `*.dsl.yml`)."""
    paths: list[Path] = []
    for pattern in ("dsl.yml", "*.dsl.yml"):
        paths.extend(context.tmp_root.rglob(pattern))
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in sorted(paths):
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def _find_step_in_file(context, relpath: str, name: str) -> dict:
    """Load one dsl file by repo-relative path and return the named step."""
    dsl_path = context.tmp_root / relpath
    if not dsl_path.is_file():
        raise AssertionError(
            f"expected dsl file at {relpath!r} but {dsl_path} does not exist"
        )
    data = _load_yaml_with_preprocessor(dsl_path)
    if not data:
        raise AssertionError(f"dsl file {relpath!r} is empty or not a mapping")
    for step in data.get("dsl_steps", []):
        if step.get("name") == name:
            return dict(step)
    raise AssertionError(
        f"dsl step {name!r} not found in {relpath!r}; "
        f"available names: {[s.get('name') for s in data.get('dsl_steps', [])]}"
    )


def _find_step(context, name: str) -> dict:
    """Re-read all dsl.yml under tmp_root and find step by name field."""
    dsl_files = _find_dsl_files(context)
    if not dsl_files:
        raise AssertionError(
            f"expected to find dsl step {name!r} but no dsl.yml files exist under {context.tmp_root}"
        )
    for dsl_path in dsl_files:
        data = _load_yaml_with_preprocessor(dsl_path)
        if not data:
            continue
        for step in data.get("dsl_steps", []):
            if step.get("name") == name:
                return dict(step)
    searched = [str(p.relative_to(context.tmp_root)) for p in dsl_files]
    raise AssertionError(
        f"dsl step {name!r} not found in any dsl.yml; searched: {searched}"
    )


def _get_isa_steps(step_dict: dict, step_name: str) -> list:
    if "isa_steps" not in step_dict:
        raise AssertionError(
            f"dsl step {step_name!r} has no 'isa_steps' key; "
            f"skeleton may not have run — got keys: {list(step_dict.keys())}"
        )
    isa_steps = step_dict["isa_steps"]
    if not isinstance(isa_steps, list):
        raise AssertionError(
            f"dsl step {step_name!r} isa_steps is not a list; got {type(isa_steps).__name__!r}"
        )
    return isa_steps


def _get_isa_step_n(step_dict: dict, step_name: str, index: int) -> dict:
    isa_steps = _get_isa_steps(step_dict, step_name)
    if len(isa_steps) <= index:
        raise AssertionError(
            f"dsl step {step_name!r} isa_steps has length {len(isa_steps)}; "
            f"no entry at index {index}"
        )
    entry = isa_steps[index]
    if not isinstance(entry, dict):
        raise AssertionError(
            f"dsl step {step_name!r} isa_steps[{index}] is not a dict; "
            f"got {type(entry).__name__!r}"
        )
    return dict(entry)


def _get_isa_step_0(step_dict: dict, step_name: str) -> dict:
    return _get_isa_step_n(step_dict, step_name, 0)


def _load_isa_yml(context) -> dict:
    isa_path = context.tmp_root / "contracts" / "isa.yml"
    if not isa_path.exists():
        raise AssertionError(
            f"contracts/isa.yml not found at {isa_path}; cannot perform re-match assertion"
        )
    return _load_yaml_with_preprocessor(isa_path)


def _build_instruction_format_map(isa_data: dict) -> dict[str, str]:
    result = {}
    for instr in isa_data.get("instructions", []):
        name = instr.get("name")
        fmt = instr.get("format")
        if name and fmt:
            result[name] = fmt
    return result


# ---------------------------------------------------------------------------
# Exit code assertions
# ---------------------------------------------------------------------------

@then("the run exits zero")
def step_run_exits_zero(context):
    rc = context.last_run.returncode
    assert rc == 0, (
        f"expected exit code 0, got {rc}\n"
        f"stderr: {context.last_run.stderr!r}\n"
        f"stdout: {context.last_run.stdout!r}"
    )


@then("the run exits non-zero")
def step_run_exits_nonzero(context):
    rc = context.last_run.returncode
    assert rc != 0, (
        f"expected non-zero exit code, got {rc}\n"
        f"stdout: {context.last_run.stdout!r}"
    )


# ---------------------------------------------------------------------------
# stdout / stderr content assertions
# ---------------------------------------------------------------------------

@then('stderr contains "{text}"')
def step_stderr_contains(context, text: str):
    stderr = context.last_run.stderr
    assert text in stderr, (
        f"expected stderr to contain {text!r}\n"
        f"actual stderr: {stderr!r}"
    )


@then('stdout contains "{text}"')
def step_stdout_contains(context, text: str):
    stdout = context.last_run.stdout
    assert text in stdout, (
        f"expected stdout to contain {text!r}\n"
        f"actual stdout: {stdout!r}"
    )


# ---------------------------------------------------------------------------
# DSL step structural assertions
# ---------------------------------------------------------------------------

def _extract_param_keys(params, step_name: str) -> list[str]:
    """Extract param keys from any supported params shape.

    Canonical shapes (chosen by whether any binding declares a default):
      - flat-list-of-strings `[<DSL key>, ...]` when no binding has a default
        (every param required);
      - mapping `{<DSL key>: <default_value or None>}` when at least one
        binding has a default (required keys carry None).
    Legacy list-of-single-key-dict is still tolerated for backward-compat.
    """
    if isinstance(params, dict):
        return list(params.keys())
    if isinstance(params, list):
        keys = []
        for p in params:
            if isinstance(p, dict) and len(p) == 1:
                keys.append(next(iter(p.keys())))
            elif isinstance(p, str):
                keys.append(p)
            else:
                keys.append(str(p))
        return keys
    raise AssertionError(
        f"dsl step {step_name!r} params is unexpected type {type(params).__name__!r}"
    )


@then('dsl step "{name}" has empty params list')
def step_dsl_params_empty(context, name: str):
    step = _find_step(context, name)
    params = step.get("params")
    if params is None:
        raise AssertionError(
            f"dsl step {name!r} has no 'params' key after translation; "
            f"got keys: {list(step.keys())}"
        )
    actual_keys = _extract_param_keys(params, name)
    assert actual_keys == [], (
        f"dsl step {name!r} expected empty params list, got keys: {actual_keys}"
    )


@then('dsl step "{name}" has params keys [{keys_literal}] in order')
def step_dsl_params_keys_in_order(context, name: str, keys_literal: str):
    step = _find_step(context, name)
    expected_keys = _parse_keys_literal("[" + keys_literal + "]")

    params = step.get("params")
    if params is None:
        raise AssertionError(
            f"dsl step {name!r} has no 'params' key after translation; "
            f"got keys: {list(step.keys())}"
        )
    actual_keys = _extract_param_keys(params, name)
    assert actual_keys == expected_keys, (
        f"dsl step {name!r} params keys mismatch\n"
        f"  expected (in order): {expected_keys}\n"
        f"  actual   (in order): {actual_keys}"
    )


def _to_plain(obj):
    """Normalize ruamel scalar-string subclasses to plain Python for comparison."""
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_plain(x) for x in obj]
    if isinstance(obj, str):
        return str(obj)
    return obj


@then('dsl step "{name}" has params equal to')
@then('dsl step "{name}" has params equal to:')
def step_dsl_params_equal(context, name: str):
    step = _find_step(context, name)
    params = step.get("params")
    if params is None:
        raise AssertionError(
            f"dsl step {name!r} has no 'params' key after translation; "
            f"got keys: {list(step.keys())}"
        )
    expected = _yaml.load(io.StringIO(context.text))
    actual_plain = _to_plain(params)
    expected_plain = _to_plain(expected)
    assert actual_plain == expected_plain, (
        f"dsl step {name!r} params mismatch\n"
        f"  expected: {expected_plain}\n"
        f"  actual:   {actual_plain}"
    )


@then("dsl step \"{name}\" has params length {n:d}")
def step_dsl_params_length(context, name: str, n: int):
    step = _find_step(context, name)
    params = step.get("params")
    if params is None:
        raise AssertionError(
            f"dsl step {name!r} has no 'params' key after translation; "
            f"got keys: {list(step.keys())}"
        )
    if isinstance(params, dict):
        actual = len(params)
    elif isinstance(params, list):
        actual = len(params)
    else:
        raise AssertionError(
            f"dsl step {name!r} params is unexpected type {type(params).__name__!r}"
        )
    assert actual == n, (
        f"dsl step {name!r} params length: expected {n}, got {actual}"
    )


def _assert_instruction(step_dict, name, expected, index=0):
    entry = _get_isa_step_n(step_dict, name, index)
    actual = entry.get("instruction", "<key 'instruction' missing>")
    assert actual == expected, (
        f"dsl step {name!r} isa_steps[{index}].instruction mismatch\n"
        f"  expected: {expected!r}\n"
        f"  actual:   {actual!r}"
    )


@then('dsl step "{name}" has isa_steps[{index:d}].instruction equal to "{expected}"')
def step_dsl_isa_instruction_dquote(context, name: str, index: int, expected: str):
    _assert_instruction(_find_step(context, name), name, expected, index)


@then("dsl step \"{name}\" has isa_steps[{index:d}].instruction equal to '{expected}'")
def step_dsl_isa_instruction_squote(context, name: str, index: int, expected: str):
    _assert_instruction(_find_step(context, name), name, expected, index)


def _assert_isa_table_equal(step: dict, step_name: str, expected_yaml: str, index=0) -> None:
    entry = _get_isa_step_n(step, step_name, index)
    actual_table = entry.get("table")
    if actual_table is None:
        raise AssertionError(
            f"dsl step {step_name!r} isa_steps[{index}] has no 'table' key; "
            f"got keys: {list(entry.keys())}"
        )
    expected_table = _yaml.load(io.StringIO(expected_yaml))
    assert actual_table == expected_table, (
        f"dsl step {step_name!r} isa_steps[{index}].table mismatch\n"
        f"  expected: {dict(expected_table)}\n"
        f"  actual:   {dict(actual_table) if isinstance(actual_table, dict) else actual_table}"
    )


@then('dsl step "{name}" has isa_steps[{index:d}].table equal to')
@then('dsl step "{name}" has isa_steps[{index:d}].table equal to:')
def step_dsl_isa_table_equal(context, name: str, index: int):
    _assert_isa_table_equal(_find_step(context, name), name, context.text, index)


@then('dsl file at "{relpath}" step "{name}" has isa_steps[0].table equal to')
@then('dsl file at "{relpath}" step "{name}" has isa_steps[0].table equal to:')
def step_dsl_file_isa_table_equal(context, relpath: str, name: str):
    _assert_isa_table_equal(_find_step_in_file(context, relpath, name), name, context.text)


@then('dsl file at "{relpath}" step "{name}" has isa_steps[0].instruction equal to "{expected}"')
def step_dsl_file_isa_instruction_dquote(context, relpath: str, name: str, expected: str):
    _assert_instruction(_find_step_in_file(context, relpath, name), name, expected)


@then("dsl file at \"{relpath}\" step \"{name}\" has isa_steps[0].instruction equal to '{expected}'")
def step_dsl_file_isa_instruction_squote(context, relpath: str, name: str, expected: str):
    _assert_instruction(_find_step_in_file(context, relpath, name), name, expected)


@then('dsl step "{name}" has isa_steps[0].table key "{key}" with value ""')
def step_dsl_isa_table_key_empty_value(context, name: str, key: str):
    """Explicit matcher for empty-string value (parse can't match `{value}` to '')."""
    step_dsl_isa_table_key_value(context, name, key, "")


@then('dsl step "{name}" has isa_steps[0].table key "{key}" with value "{value}"')
def step_dsl_isa_table_key_value(context, name: str, key: str, value: str):
    step = _find_step(context, name)
    entry = _get_isa_step_0(step, name)

    table = entry.get("table")
    if table is None:
        raise AssertionError(
            f"dsl step {name!r} isa_steps[0] has no 'table' key; "
            f"got keys: {list(entry.keys())}"
        )
    if not isinstance(table, dict):
        raise AssertionError(
            f"dsl step {name!r} isa_steps[0].table is not a dict; "
            f"got {type(table).__name__!r}: {table!r}"
        )
    if key not in table:
        raise AssertionError(
            f"dsl step {name!r} isa_steps[0].table missing key {key!r}; "
            f"available keys: {list(table.keys())}"
        )
    actual = str(table[key])
    assert actual == value, (
        f"dsl step {name!r} isa_steps[0].table[{key!r}] mismatch\n"
        f"  expected: {value!r}\n"
        f"  actual:   {actual!r}"
    )


@then("dsl step \"{name}\" has isa_steps[0].table length {n:d}")
def step_dsl_isa_table_length(context, name: str, n: int):
    step = _find_step(context, name)
    entry = _get_isa_step_0(step, name)

    table = entry.get("table")
    if table is None:
        raise AssertionError(
            f"dsl step {name!r} isa_steps[0] has no 'table' key; "
            f"got keys: {list(entry.keys())}"
        )
    if not isinstance(table, dict):
        raise AssertionError(
            f"dsl step {name!r} isa_steps[0].table is not a dict; "
            f"got {type(table).__name__!r}: {table!r}"
        )
    actual = len(table)
    assert actual == n, (
        f"dsl step {name!r} isa_steps[0].table length: expected {n}, got {actual}\n"
        f"  actual table: {dict(table)}"
    )


@then("dsl step \"{name}\" has isa_steps length {n:d}")
def step_dsl_isa_steps_length(context, name: str, n: int):
    step = _find_step(context, name)
    isa_steps = _get_isa_steps(step, name)
    actual = len(isa_steps)
    assert actual == n, (
        f"dsl step {name!r} isa_steps length: expected {n}, got {actual}"
    )


# ---------------------------------------------------------------------------
# Summary assertion
# ---------------------------------------------------------------------------

@then("summary reports first_write_count {first:d} and idempotent_skip_count {skip:d}")
def step_summary_counts(context, first: int, skip: int):
    stdout = context.last_run.stdout
    m = re.search(r"first_write_count=(\d+)", stdout)
    m2 = re.search(r"idempotent_skip_count=(\d+)", stdout)
    if not m or not m2:
        raise AssertionError(
            f"expected summary line in stdout with first_write_count and idempotent_skip_count\n"
            f"actual stdout: {stdout!r}"
        )
    actual_first = int(m.group(1))
    actual_skip = int(m2.group(1))
    assert actual_first == first and actual_skip == skip, (
        f"summary mismatch\n"
        f"  expected: first_write_count={first} idempotent_skip_count={skip}\n"
        f"  actual:   first_write_count={actual_first} idempotent_skip_count={actual_skip}"
    )


# ---------------------------------------------------------------------------
# Regex re-match assertion
# ---------------------------------------------------------------------------

@then("every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format")
def step_rematch_non_sentinel(context):
    """Check every translated step whose instruction is not a FILL-IN sentinel.

    Skeleton produces <NOT YET IMPLEMENTED> for all steps, which IS a sentinel,
    so the non-sentinel set is empty and this assertion trivially passes.
    (<FILL IN>) from security-placeholder is also a sentinel.
    """
    SENTINELS = ("<NOT YET IMPLEMENTED>", "<FILL IN>")

    isa_data = _load_isa_yml(context)
    format_map = _build_instruction_format_map(isa_data)

    dsl_files = _find_dsl_files(context)
    failures = []

    for dsl_path in dsl_files:
        data = _load_yaml_with_preprocessor(dsl_path)
        if not data:
            continue
        for step in data.get("dsl_steps", []):
            isa_steps = step.get("isa_steps")
            if not isa_steps or not isinstance(isa_steps, list) or len(isa_steps) == 0:
                continue
            entry = isa_steps[0]
            if not isinstance(entry, dict):
                continue
            instruction = entry.get("instruction", "")
            is_sentinel = any(s in str(instruction) for s in SENTINELS)
            if is_sentinel:
                continue
            matched = False
            for fmt_regex in format_map.values():
                if re.fullmatch(fmt_regex, str(instruction)):
                    matched = True
                    break
            if not matched:
                failures.append(
                    f"  step {step.get('name')!r}: instruction {instruction!r} "
                    f"did not match any isa.yml format regex"
                )

    if failures:
        raise AssertionError(
            "Some non-sentinel instructions failed to re-match isa.yml format:\n"
            + "\n".join(failures)
        )
