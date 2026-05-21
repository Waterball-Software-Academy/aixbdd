"""Then steps for writer features."""

from __future__ import annotations

from behave import then


@then('the routed path is "{expected}"')
def step_assert_routed_path(context, expected: str):
    actual = context.routed_path.as_posix()
    assert actual == expected, f"expected routed path {expected!r}, got {actual!r}"


@then('the file "{relpath}" contains the text "{needle}"')
def step_assert_file_contains(context, relpath: str, needle: str):
    path = context.tmp_root / relpath
    assert path.is_file(), f"file {relpath!r} not found at {path}"
    content = path.read_text()
    assert needle in content, (
        f"file {relpath!r} does not contain {needle!r}; got:\n{content}"
    )


@then('the file "{relpath}" does not contain the line "{needle}"')
def step_assert_file_not_contains_line(context, relpath: str, needle: str):
    path = context.tmp_root / relpath
    assert path.is_file(), f"file {relpath!r} not found at {path}"
    lines = [line.strip() for line in path.read_text().splitlines()]
    assert needle not in lines, (
        f"file {relpath!r} contains forbidden line {needle!r}; lines: {lines}"
    )


@then('the file "{relpath}" loads as a YAML mapping with key "{key}"')
def step_assert_file_yaml_top_key(context, relpath: str, key: str):
    from ruamel.yaml import YAML

    path = context.tmp_root / relpath
    assert path.is_file(), f"file {relpath!r} not found at {path}"
    yaml = YAML(typ="safe")
    doc = yaml.load(path.read_text())
    assert isinstance(doc, dict), (
        f"expected top-level mapping, got {type(doc).__name__}: {doc!r}"
    )
    assert key in doc, (
        f"expected key {key!r} in top-level mapping, got keys {list(doc.keys())}"
    )
