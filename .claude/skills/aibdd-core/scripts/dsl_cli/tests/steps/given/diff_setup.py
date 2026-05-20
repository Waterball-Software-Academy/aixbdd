"""Given steps for diff.py prefix-match feature.

Parts and resolved targets are described purely by `target_part_path`. We use
a minimal `_FakePart` stand-in (Principle 4 doesn't apply here — diff operates
on Part identity strings, not on spec_parser output structure).
"""

from __future__ import annotations

from dataclasses import dataclass

from behave import given


@dataclass(frozen=True)
class _FakePart:
    target_part_path: str


@given("the following parts")
@given("the following parts:")
def step_given_parts(context):
    context.parts = [_FakePart(row["target_part_path"]) for row in context.table]


@given("the following resolved targets")
@given("the following resolved targets:")
def step_given_resolved(context):
    context.resolved_targets = [row["target_part_path"] for row in context.table]
