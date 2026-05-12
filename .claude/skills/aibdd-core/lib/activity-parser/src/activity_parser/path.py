"""Path — AST → Paths (Policy 1: every Action Node at least once).

MVP heuristic:
    Treat the AST as a linear list of nodes. Whenever a DECISION appears,
    emit one Path per distinct BRANCH guard that follows it until the next
    STEP. Policy 1 demands every action node be traversed at least once;
    this simple algorithm produces (1 + number-of-branches-minus-1) paths
    which is enough for the MVP plan.

    Policy 2 (exhaustive) is deferred.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .parser import ActivityAst, Node


@dataclass(slots=True)
class PathStep:
    node_id: str | None
    label: str
    kind: str
    guard: str | None = None


@dataclass(slots=True)
class ExtractedPath:
    number: int
    title: str | None
    steps: list[PathStep] = field(default_factory=list)


def extract_paths(ast: ActivityAst, *, policy: str = "node-once") -> list[ExtractedPath]:
    if policy != "node-once":
        raise NotImplementedError(f"policy {policy!r} not supported in MVP")

    # Minimal MVP: emit one main Path covering every STEP + (for each DECISION)
    # one additional Path per branch guard.
    paths: list[ExtractedPath] = []

    main_steps = [
        PathStep(node_id=n.id, label=n.label, kind=n.kind)
        for n in ast.nodes
        if n.is_action
    ]
    paths.append(ExtractedPath(number=1, title=ast.title or "Main happy path", steps=main_steps))

    num = 2
    nodes = ast.nodes
    for idx, n in enumerate(nodes):
        if n.kind != "DECISION":
            continue
        # PF-04 (Round 1 reinforcement): support TWO BRANCH id dialects:
        # (a) dotted children of the DECISION id (e.g. DECISION:3 → BRANCH:3.1, BRANCH:3.2)
        # (b) sibling suffixed IDs (e.g. DECISION:3a → BRANCH:3a.合法, BRANCH:3a.非法 OR
        #     DECISION:3a → BRANCH:3b, BRANCH:3c — IDs that follow the decision contiguously)
        dec_id = n.id or ""
        guards = [
            x
            for x in nodes
            if x.kind == "BRANCH"
            and (
                (x.id or "").startswith(dec_id + ".")                    # dialect (a)
                or _is_sibling_branch_id(x.id or "", dec_id)              # dialect (b)
            )
        ]
        # Fallback dialect (c): contiguous BRANCH nodes immediately following the DECISION,
        # regardless of ID pattern. Seen in hand-authored activities that lack explicit
        # child-id / sibling-id discipline.
        if not guards:
            guards = []
            for follow in nodes[idx + 1 :]:
                if follow.kind == "BRANCH":
                    guards.append(follow)
                elif follow.kind in ("STEP", "DECISION", "FORK", "PARALLEL", "END"):
                    # stop scan once a non-BRANCH is encountered
                    break

        for g in guards[1:]:  # main path covers the first branch; emit extras for alternative branches
            steps = list(main_steps)
            steps.append(
                PathStep(node_id=g.id, label=g.label or (g.guard or ""), kind="BRANCH", guard=g.guard)
            )
            paths.append(
                ExtractedPath(
                    number=num,
                    title=f"Alternative branch: {g.guard or g.id}",
                    steps=steps,
                )
            )
            num += 1

    return paths


def _is_sibling_branch_id(branch_id: str, decision_id: str) -> bool:
    """Detect sibling-style BRANCH IDs like DECISION:3a → BRANCH:3a.合法 OR BRANCH:3b.

    A branch is considered a sibling of the decision if its id shares the same
    numeric prefix but is not the decision id itself. Examples:

    - decision_id="3a", branch_id="3a.合法"   → True
    - decision_id="3a", branch_id="3b"         → True (next alpha suffix)
    - decision_id="3",  branch_id="4"          → False (different decision)
    - decision_id="",   branch_id=""           → False
    """
    if not decision_id or not branch_id or decision_id == branch_id:
        return False
    # Extract numeric prefix of decision_id (e.g. "3" from "3a" or "3.1")
    dec_num_prefix = ""
    for ch in decision_id:
        if ch.isdigit():
            dec_num_prefix += ch
        else:
            break
    if not dec_num_prefix:
        return False
    # Branch id must start with same numeric prefix
    if not branch_id.startswith(dec_num_prefix):
        return False
    # Branch id's character right after prefix must be a letter / dot / end-of-string
    rest = branch_id[len(dec_num_prefix) :]
    if rest == "":
        return False
    return rest[0].isalpha() or rest[0] == "."
