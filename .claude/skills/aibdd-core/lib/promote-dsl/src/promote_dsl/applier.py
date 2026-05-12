"""Applier — build a move plan from a signed-off promotion-proposal.md
and optionally execute it.

MVP scaffold. Actual step-def file moves are TODO; this module emits the
plan shape so downstream tooling (shell scripts / git hooks) can consume it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class MovePlanStep:
    """One atomic piece of the promotion plan."""

    kind: str                          # "append-core" | "remove-local" | "move-stepdef" | "append-manifest"
    source: str | None = None
    target: str | None = None
    payload: str | None = None
    notes: str | None = None


@dataclass(slots=True)
class MovePlan:
    proposal_path: Path
    dsl_core: Path
    steps: list[MovePlanStep] = field(default_factory=list)


def _parse_signoff(proposal_text: str) -> str:
    """Crudely extract the ``Decision: <value>`` line; MVP only."""
    for line in proposal_text.splitlines():
        line = line.strip()
        if line.lower().startswith("decision:"):
            return line.split(":", 1)[1].strip().strip("_").strip()
    return "pending"


def build_plan(proposal_path: Path, dsl_core: Path) -> MovePlan:
    """Read proposal, validate sign-off, and emit a move plan.

    MVP: returns a plan with plan-only intent (no actual file work). Wire up
    the real promotion logic in a follow-up task tracked under
    ``docs/sub-proposals/01-dsl-promotion-detail.md``.
    """
    text = proposal_path.read_text(encoding="utf-8")
    decision = _parse_signoff(text)
    if decision != "apply":
        raise RuntimeError(
            f"proposal at {proposal_path} has decision={decision!r}; refusing to apply. "
            "Edit the `Signed-off` block and set Decision to 'apply' after human review."
        )

    plan = MovePlan(proposal_path=proposal_path, dsl_core=dsl_core)
    plan.steps.append(
        MovePlanStep(
            kind="append-core",
            target=str(dsl_core),
            notes="TODO: parse 'Proposed shared dsl.md additions' block and append YAML entries.",
        )
    )
    plan.steps.append(
        MovePlanStep(
            kind="remove-local",
            notes="TODO: for each candidate, remove matching entry from per-spec dsl.md, leave pointer comment.",
        )
    )
    plan.steps.append(
        MovePlanStep(
            kind="move-stepdef",
            notes="TODO: read bdd-constitution.md; move step-def code to shared location; keep git history.",
        )
    )
    plan.steps.append(
        MovePlanStep(
            kind="append-manifest",
            notes="TODO: append promotion entry to each affected archive-manifest.yml (if present).",
        )
    )
    return plan


def format_plan(plan: MovePlan) -> str:
    lines = [
        f"# Promotion plan",
        f"proposal: {plan.proposal_path}",
        f"dsl-core: {plan.dsl_core}",
        "",
    ]
    for idx, step in enumerate(plan.steps, 1):
        lines.append(f"{idx}. [{step.kind}]")
        if step.source:
            lines.append(f"   source: {step.source}")
        if step.target:
            lines.append(f"   target: {step.target}")
        if step.notes:
            lines.append(f"   notes:  {step.notes}")
    return "\n".join(lines)


def execute_plan(plan: MovePlan) -> None:
    """Execute the plan. MVP = no-op with notice; real execution deferred."""
    # NOTE: deliberately a no-op until sub-proposal #1 pins the algorithm.
    # Raising is too harsh; printing a warning keeps the CLI testable.
    print(
        "applier.execute_plan is a no-op in MVP — see "
        "docs/sub-proposals/01-dsl-promotion-detail.md for the deferred algorithm."
    )
