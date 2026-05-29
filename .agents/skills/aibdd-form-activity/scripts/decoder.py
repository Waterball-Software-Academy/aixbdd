#!/usr/bin/env python3
"""Activity DSL decoder.

Dual-purpose:
- SKILL.md Phase 4 syntax gate (CLI: `python3 scripts/decoder.py <file>`).
- Subject of the BDD suite under `scripts/tests/`. Spec SSOT lives in
  `scripts/tests/activity-decode.feature` (rule-by-rule contracts) and
  `scripts/tests/activity-benchmark.feature` (corpus pass/fail).

Aggregate shape is defined by the dataclasses below. Key DSL invariants:
- `[BRANCH]` / `[PARALLEL]` are path containers only
- actual work must live in nested `[STEP]` / `[FINAL]` / nested gateways
- aggregate output is still flattened via `firstNodeId` + `next`
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal


# ──────────────────────────────────────────────────────────────────────────
# Tag tokeniser — line-based, mirrors SF DslTokenizerService surface
# ──────────────────────────────────────────────────────────────────────────
# INITIAL / FINAL — bare; no `:id`, no trailing body.
_BARE_TAG_RE = re.compile(r"^(?P<indent>\s*)\[(?P<tag>INITIAL|FINAL)\]\s*$")
# MERGE / FORK / JOIN — `:id` required, no trailing body.
_CLOSER_TAG_RE = re.compile(r"^(?P<indent>\s*)\[(?P<tag>MERGE|FORK|JOIN):(?P<id>[^\]]+)\]\s*$")
# Open-shape tags — body allowed, validated downstream.
_OPEN_TAG_RE = re.compile(
    r"^(?P<indent>\s*)\[(?P<tag>ACTIVITY|ACTOR|STEP|DECISION|BRANCH|PARALLEL)"
    r"(?::(?P<id>[^\]]+))?\]\s*(?P<body>.*)$"
)
# `-> {...}` arrow-binding suffix (used by [ACTOR] -> {path} and [STEP] -> {api_binding})
_ARROW_BINDING_RE = re.compile(r"\s*->\s*\{(?P<arrow>[^}]+)\}\s*$")
# `{id:xxx}` explicit nanoid suffix
_ID_BRACE_RE = re.compile(r"\s*\{id:(?P<idval>[^}]+)\}")
# `{xxx}` plain binding (no `id:` prefix, no leading `->`)
_BRACE_RE = re.compile(r"\{(?P<val>[^}]+)\}\s*$")
_QUOTED_ACTOR_RE = re.compile(r'^@"(?P<name>(?:[^"\\]|\\.)+)"(?:\s+(?P<rest>.*))?$')
_BARE_ACTOR_RE = re.compile(r"^@(?P<name>\S+)(?:\s+(?P<rest>.*))?$")


# ──────────────────────────────────────────────────────────────────────────
# Error shape (matches `.feature` ParseError table: line + message)
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class ParseError:
    line: int
    message: str


class _ParseFailure(Exception):
    def __init__(self, line: int, message: str):
        super().__init__(message)
        self.line = line
        self.message = message


# ──────────────────────────────────────────────────────────────────────────
# Domain shapes (flattened aggregate projection)
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class Actor:
    id: str
    name: str
    actorType: Literal["external_user", "third_party_system", "system"] = "external_user"
    binding: str | None = None


@dataclass
class BranchPath:
    guard: str
    firstNodeId: str | None = None
    loopBackTarget: str | None = None


@dataclass
class ForkPath:
    firstNodeId: str


@dataclass
class UiStep:
    id: str
    displayId: str
    actorId: str
    type: Literal["ui_step"] = "ui_step"
    name: str = ""
    bindsFeature: str | None = None
    next: str | None = None


@dataclass
class Decision:
    id: str
    displayId: str
    condition: str
    type: Literal["decision"] = "decision"
    paths: list[BranchPath] = field(default_factory=list)
    next: None = None


@dataclass
class Fork:
    id: str
    displayId: str
    type: Literal["fork"] = "fork"
    paths: list[ForkPath] = field(default_factory=list)
    next: None = None


@dataclass
class Merge:
    id: str
    displayId: str
    type: Literal["merge"] = "merge"
    next: str | None = None


@dataclass
class Join:
    id: str
    displayId: str
    type: Literal["join"] = "join"
    next: str | None = None


Node = UiStep | Decision | Fork | Merge | Join


@dataclass
class InitialNode:
    id: str
    next: str | None = None


@dataclass
class FinalNode:
    id: str
    next: None = None


@dataclass
class Activity:
    name: str
    id: str
    initialNode: InitialNode
    finalNodes: list[FinalNode] = field(default_factory=list)
    actors: list[Actor] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    filePath: str = ""
    version: int = 1


@dataclass
class ParseResult:
    ok: bool
    errors: list[ParseError] = field(default_factory=list)
    activity: Activity | None = None


@dataclass(eq=False)
class _Token:
    line: int
    indent: int
    tag: str
    raw_id: str
    body: str


@dataclass(eq=False)
class _AstStep:
    line: int
    displayId: str
    actorName: str
    name: str
    bindsFeature: str | None


@dataclass(eq=False)
class _AstFinal:
    line: int


@dataclass(eq=False)
class _AstBranch:
    line: int
    guard: str
    loopTarget: str | None
    body: list[object] = field(default_factory=list)


@dataclass(eq=False)
class _AstDecision:
    line: int
    displayId: str
    condition: str
    branches: list[_AstBranch] = field(default_factory=list)


@dataclass(eq=False)
class _AstParallel:
    line: int
    body: list[object] = field(default_factory=list)


@dataclass(eq=False)
class _AstFork:
    line: int
    displayId: str
    parallels: list[_AstParallel] = field(default_factory=list)


AstNode = _AstStep | _AstFinal | _AstDecision | _AstFork


# ──────────────────────────────────────────────────────────────────────────
# Parser entry
# ──────────────────────────────────────────────────────────────────────────
def parse(text: str) -> ParseResult:
    """Decode `.activity` DSL text into ParseResult."""
    try:
        tokens = _tokenize(text)
        if not tokens or tokens[0].tag != "ACTIVITY":
            raise _ParseFailure(1, "Expected '[ACTIVITY]' declaration")

        activity_name = tokens[0].body.strip()
        if not activity_name:
            raise _ParseFailure(tokens[0].line, "Activity missing name")

        idx = 1
        actors: list[_ActorDecl] = []
        seen_actor_names: set[str] = set()
        while idx < len(tokens) and tokens[idx].tag == "ACTOR":
            actor = _parse_actor(tokens[idx])
            if actor.name in seen_actor_names:
                raise _ParseFailure(tokens[idx].line, f"Duplicate actor name: '{actor.name}'")
            seen_actor_names.add(actor.name)
            actors.append(actor)
            idx += 1

        ast_nodes, idx = _parse_body(tokens, idx, parent_indent=-1)
        if idx != len(tokens):
            raise _ParseFailure(tokens[idx].line, f"Unexpected [{tokens[idx].tag}]")

        _validate_ast(ast_nodes, actors)
        return ParseResult(ok=True, activity=_lower(activity_name, actors, ast_nodes))
    except _ParseFailure as exc:
        return ParseResult(ok=False, errors=[ParseError(exc.line, exc.message)])


# ──────────────────────────────────────────────────────────────────────────
# Per-tag body parsers
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class _ActorDecl:
    name: str
    binding: str | None


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _BARE_TAG_RE.match(raw)
        if m:
            indent = len(m.group("indent") or "")
            tokens.append(_Token(idx, indent, m.group("tag"), "", ""))
            continue
        m = _CLOSER_TAG_RE.match(raw)
        if m:
            indent = len(m.group("indent") or "")
            tokens.append(_Token(idx, indent, m.group("tag"), m.group("id").strip(), ""))
            continue
        m = _OPEN_TAG_RE.match(raw)
        if m:
            body = (m.group("body") or "").strip()
            if _ID_BRACE_RE.search(body):
                raise _ParseFailure(idx, "Inline {id:...} not allowed: ids are managed by GraphDriver")
            indent = len(m.group("indent") or "")
            tokens.append(_Token(idx, indent, m.group("tag"), (m.group("id") or "").strip(), body))
            continue
        # Fallthrough — non-tag or malformed-tag line. Indent decides which surface error.
        if raw[:1] in (" ", "\t"):
            raise _ParseFailure(idx, f"Unexpected indented free text: '{stripped}'")
        raise _ParseFailure(idx, f"Unexpected content: '{stripped}'")
    return tokens


def _parse_actor(token: _Token) -> _ActorDecl:
    body = token.body
    binding = None
    m = _ARROW_BINDING_RE.search(body)
    if m:
        binding = m.group("arrow").strip()
        body = body[: m.start()].rstrip()
    elif re.search(r"\s+->\s+\{", body):
        # `-> {…}` is present but not at end (extra trailing chars after `}`) → malformed actor.
        raise _ParseFailure(token.line, "Actor missing name")
    name = _parse_name(body, token.line)
    return _ActorDecl(name=name, binding=binding)


def _strip_plain_binding(body: str) -> tuple[str, str | None]:
    """Strip a trailing `{path}` plain-brace binding."""
    m = _BRACE_RE.search(body)
    if not m:
        return body, None
    return (body[: m.start()] + body[m.end():]).rstrip(), m.group("val").strip()


def _parse_name(text: str, line: int) -> str:
    text = text.strip()
    if not text:
        raise _ParseFailure(line, "missing name")
    if text.startswith('"'):
        if not text.endswith('"') or len(text) < 2:
            raise _ParseFailure(line, "malformed quoted name")
        return text[1:-1].replace(r"\"", '"').replace(r"\\", "\\")
    return text


def _split_actor_and_desc(body: str, line: int, *, require_actor: bool) -> tuple[str, str, str | None]:
    if _ARROW_BINDING_RE.search(body):
        raise _ParseFailure(line, "Legacy STEP binding syntax not allowed: use {path}")
    if "->" in body:
        raise _ParseFailure(line, 'Unexpected "->" in STEP content')
    probe = body.strip()
    if "{" in probe:
        last_close = probe.rfind("}")
        if last_close == -1:
            raise _ParseFailure(line, "Malformed or unclosed '{binding}' in STEP")
        after_close = probe[last_close + 1 :].strip()
        if after_close:
            raise _ParseFailure(line, f"Unexpected trailing content after binding: '{after_close}'")
        open_idx = probe.rfind("{", 0, last_close)
        if open_idx != -1 and "{" in probe[:open_idx]:
            raise _ParseFailure(line, "Only one trailing '{binding}' suffix allowed in STEP")
    body, binds_feature = _strip_plain_binding(body)
    body = body.strip()
    if not body:
        if require_actor:
            raise _ParseFailure(line, "STEP missing actor reference")
        return "", "", binds_feature  # unreachable for current callers

    actor_name: str | None = None
    desc = ""
    quoted = _QUOTED_ACTOR_RE.match(body)
    bare = _BARE_ACTOR_RE.match(body) if quoted is None else None
    if quoted:
        actor_name = quoted.group("name").replace(r"\"", '"').replace(r"\\", "\\")
        desc = (quoted.group("rest") or "").strip()
    elif bare:
        actor_name = bare.group("name")
        desc = (bare.group("rest") or "").strip()

    if actor_name is None:
        if require_actor:
            raise _ParseFailure(line, "STEP missing actor reference")
        raise _ParseFailure(line, "missing actor reference")

    return actor_name, desc, binds_feature


def _parse_step(token: _Token) -> _AstStep:
    actor_name, desc, binds_feature = _split_actor_and_desc(token.body, token.line, require_actor=True)
    return _AstStep(
        line=token.line,
        displayId=token.raw_id,
        actorName=actor_name,
        name=desc,
        bindsFeature=binds_feature,
    )


def _parse_decision(token: _Token) -> _AstDecision:
    return _AstDecision(line=token.line, displayId=token.raw_id, condition=token.body.strip())


def _parse_branch_header(token: _Token, expected_decision_id: str) -> _AstBranch:
    if token.body:
        raise _ParseFailure(
            token.line,
            "Legacy BRANCH inline payload not allowed: move work to nested STEP/FINAL",
        )
    decision_id, sep, rest = token.raw_id.partition(":")
    if not sep or decision_id != expected_decision_id:
        raise _ParseFailure(token.line, f"BRANCH references unknown DECISION: {decision_id or token.raw_id}")
    guard = rest
    loop_back = None
    if " -> " in rest:
        guard, _, loop_back = rest.partition(" -> ")
        guard = guard.strip()
        loop_back = loop_back.strip() or None
    return _AstBranch(line=token.line, guard=guard, loopTarget=loop_back)


def _parse_parallel_header(token: _Token, expected_fork_id: str) -> _AstParallel:
    if token.body:
        raise _ParseFailure(
            token.line,
            "Legacy PARALLEL inline payload not allowed: move work to nested STEP/FINAL",
        )
    if token.raw_id != expected_fork_id:
        raise _ParseFailure(token.line, f"PARALLEL references unknown FORK: {token.raw_id}")
    return _AstParallel(line=token.line)


def _parse_body(tokens: list[_Token], idx: int, parent_indent: int) -> tuple[list[AstNode], int]:
    nodes: list[AstNode] = []
    saw_top_final = False
    while idx < len(tokens):
        token = tokens[idx]
        if token.indent <= parent_indent:
            break

        # Top-level only: after first [FINAL], only more [FINAL] tokens are legal.
        if parent_indent == -1 and saw_top_final and token.tag != "FINAL":
            raise _ParseFailure(token.line, "Content after [FINAL]")

        if token.tag == "INITIAL":
            # `[INITIAL]` is a source-only marker — only legal at top-level (parent_indent == -1).
            # The lower phase always synthesizes `initial:0`, so no AST node needed here.
            if parent_indent != -1:
                raise _ParseFailure(token.line, f"Unexpected [{token.tag}]")
            idx += 1
        elif token.tag == "STEP":
            nodes.append(_parse_step(token))
            idx += 1
        elif token.tag == "FINAL":
            nodes.append(_AstFinal(line=token.line))
            if parent_indent == -1:
                saw_top_final = True
            idx += 1
        elif token.tag == "DECISION":
            decision = _parse_decision(token)
            idx += 1
            seen_guards: set[str] = set()
            while idx < len(tokens) and tokens[idx].indent > token.indent:
                branch_token = tokens[idx]
                if branch_token.tag != "BRANCH":
                    raise _ParseFailure(branch_token.line, f"Expected [BRANCH] inside DECISION:{decision.displayId}")
                branch = _parse_branch_header(branch_token, decision.displayId)
                if branch.guard in seen_guards:
                    raise _ParseFailure(
                        branch_token.line,
                        f"Duplicate guard '{branch.guard}' in decision '{decision.displayId}'",
                    )
                seen_guards.add(branch.guard)
                idx += 1
                branch.body, idx = _parse_body(tokens, idx, branch_token.indent)
                decision.branches.append(branch)
            if idx >= len(tokens) or tokens[idx].tag != "MERGE" or tokens[idx].raw_id != decision.displayId:
                raise _ParseFailure(token.line, f"Unclosed decision: '{decision.displayId}'")
            nodes.append(decision)
            idx += 1
        elif token.tag == "FORK":
            fork = _AstFork(line=token.line, displayId=token.raw_id)
            idx += 1
            while idx < len(tokens) and tokens[idx].indent > token.indent:
                parallel_token = tokens[idx]
                if parallel_token.tag != "PARALLEL":
                    raise _ParseFailure(parallel_token.line, f"Expected [PARALLEL] inside FORK:{fork.displayId}")
                parallel = _parse_parallel_header(parallel_token, fork.displayId)
                idx += 1
                parallel.body, idx = _parse_body(tokens, idx, parallel_token.indent)
                fork.parallels.append(parallel)
            if idx >= len(tokens) or tokens[idx].tag != "JOIN" or tokens[idx].raw_id != fork.displayId:
                raise _ParseFailure(token.line, f"Unclosed fork: '{fork.displayId}'")
            nodes.append(fork)
            idx += 1
        elif token.tag == "BRANCH":
            decision_id = token.raw_id.partition(":")[0]
            raise _ParseFailure(token.line, f"Unmatched branch: no DECISION '{decision_id}'")
        elif token.tag == "MERGE":
            raise _ParseFailure(token.line, f"Unmatched merge: no DECISION '{token.raw_id}'")
        elif token.tag == "PARALLEL":
            raise _ParseFailure(token.line, f"Unmatched parallel: no FORK '{token.raw_id}'")
        elif token.tag == "JOIN":
            raise _ParseFailure(token.line, f"Unmatched join: no FORK '{token.raw_id}'")
        else:
            raise _ParseFailure(token.line, f"Unexpected [{token.tag}]")
    return nodes, idx


def _walk_ast(nodes: list[AstNode]):
    for node in nodes:
        yield node
        if isinstance(node, _AstDecision):
            for branch in node.branches:
                yield branch
                yield from _walk_ast(branch.body)
        elif isinstance(node, _AstFork):
            for parallel in node.parallels:
                yield parallel
                yield from _walk_ast(parallel.body)


def _validate_ast(nodes: list[AstNode], actors: list[_ActorDecl]) -> None:
    actor_names = {actor.name for actor in actors}
    display_ids: set[str] = set()
    seen_step_ids: set[str] = set()
    seen_decision_ids: set[str] = set()
    seen_fork_ids: set[str] = set()

    for item in _walk_ast(nodes):
        if isinstance(item, _AstStep):
            if item.actorName not in actor_names:
                raise _ParseFailure(item.line, f"Unknown actor reference: {item.actorName}")
            if item.displayId in seen_step_ids:
                raise _ParseFailure(item.line, f"Duplicate STEP id: '{item.displayId}'")
            seen_step_ids.add(item.displayId)
            display_ids.add(item.displayId)
        elif isinstance(item, _AstDecision):
            if item.displayId in seen_decision_ids:
                raise _ParseFailure(item.line, f"Duplicate DECISION id: '{item.displayId}'")
            seen_decision_ids.add(item.displayId)
            display_ids.add(item.displayId)
        elif isinstance(item, _AstFork):
            if item.displayId in seen_fork_ids:
                raise _ParseFailure(item.line, f"Duplicate FORK id: '{item.displayId}'")
            seen_fork_ids.add(item.displayId)
            display_ids.add(item.displayId)

    for item in _walk_ast(nodes):
        if isinstance(item, _AstDecision):
            display_ids.add(item.displayId)  # merge displayId
        elif isinstance(item, _AstFork):
            display_ids.add(item.displayId)  # join displayId

    for item in _walk_ast(nodes):
        if isinstance(item, _AstBranch) and item.loopTarget is not None and item.loopTarget not in display_ids:
            raise _ParseFailure(item.line, f"BRANCH target does not exist: {item.loopTarget}")
        if isinstance(item, _AstBranch) and item.loopTarget is not None and item.body:
            raise _ParseFailure(item.line, "BRANCH loopBackTarget must not have body")


def _lower(activity_name: str, actor_decls: list[_ActorDecl], ast_nodes: list[AstNode]) -> Activity:
    actors = [
        Actor(id=f"actor:{actor.name}", name=actor.name, binding=actor.binding)
        for actor in actor_decls
    ]
    actor_id_by_name = {actor.name: actor.id for actor in actors}

    top_level_finals = [node for node in ast_nodes if isinstance(node, _AstFinal)]
    top_level_ids = {id(node) for node in top_level_finals}
    nested_finals = [
        node for node in _walk_ast(ast_nodes)
        if isinstance(node, _AstFinal) and id(node) not in top_level_ids
    ]
    explicit_finals = top_level_finals + nested_finals
    final_nodes_src = explicit_finals if explicit_finals else [_AstFinal(line=0)]
    final_id_by_obj = {id(node): f"final:{idx}" for idx, node in enumerate(final_nodes_src)}
    final_nodes = [FinalNode(id=final_id_by_obj[id(node)]) for node in final_nodes_src]

    node_id_by_obj: dict[int, str] = {}
    merge_id_by_decision: dict[int, str] = {}
    join_id_by_fork: dict[int, str] = {}
    display_id_to_node_id: dict[str, str] = {}

    for node in _walk_ast(ast_nodes):
        if isinstance(node, _AstStep):
            node_id = f"node:ui_step:{node.displayId}"
            node_id_by_obj[id(node)] = node_id
            display_id_to_node_id.setdefault(node.displayId, node_id)
        elif isinstance(node, _AstDecision):
            decision_id = f"node:decision:{node.displayId}"
            merge_id = f"node:merge:{node.displayId}"
            node_id_by_obj[id(node)] = decision_id
            merge_id_by_decision[id(node)] = merge_id
            display_id_to_node_id.setdefault(node.displayId, decision_id)
        elif isinstance(node, _AstFork):
            fork_id = f"node:fork:{node.displayId}"
            join_id = f"node:join:{node.displayId}"
            node_id_by_obj[id(node)] = fork_id
            join_id_by_fork[id(node)] = join_id
            display_id_to_node_id.setdefault(node.displayId, fork_id)

    if explicit_finals:
        terminal_fallthrough = None
    else:
        terminal_fallthrough = final_nodes[0].id

    out_nodes: list[Node] = []

    def first_id_of_sequence(seq: list[AstNode], fallback: str | None) -> str | None:
        if not seq:
            return fallback
        first = seq[0]
        if isinstance(first, _AstFinal):
            return final_id_by_obj[id(first)]
        return node_id_by_obj[id(first)]

    def lower_sequence(seq: list[AstNode], fallthrough_id: str | None) -> str | None:
        if not seq:
            return fallthrough_id
        for idx, item in enumerate(seq):
            successor = first_id_of_sequence(seq[idx + 1 :], fallthrough_id)
            lower_node(item, successor)
        return first_id_of_sequence(seq, fallthrough_id)

    def lower_node(node: AstNode, successor_id: str | None) -> None:
        if isinstance(node, _AstFinal):
            return
        if isinstance(node, _AstStep):
            out_nodes.append(
                UiStep(
                    id=node_id_by_obj[id(node)],
                    displayId=node.displayId,
                    actorId=actor_id_by_name[node.actorName],
                    name=node.name,
                    bindsFeature=node.bindsFeature,
                    next=successor_id,
                )
            )
            return
        if isinstance(node, _AstDecision):
            merge_id = merge_id_by_decision[id(node)]
            decision_obj = Decision(
                id=node_id_by_obj[id(node)],
                displayId=node.displayId,
                condition=node.condition,
                paths=[],
            )
            out_nodes.append(decision_obj)
            for branch in node.branches:
                if branch.loopTarget is not None:
                    branch_first = None
                else:
                    branch_first = lower_sequence(branch.body, merge_id)
                decision_obj.paths.append(
                    BranchPath(
                        guard=branch.guard,
                        firstNodeId=branch_first,
                        loopBackTarget=display_id_to_node_id.get(branch.loopTarget) if branch.loopTarget else None,
                    )
                )
            out_nodes.append(Merge(id=merge_id, displayId=node.displayId, next=successor_id))
            return
        if isinstance(node, _AstFork):
            join_id = join_id_by_fork[id(node)]
            fork_obj = Fork(
                id=node_id_by_obj[id(node)],
                displayId=node.displayId,
                paths=[],
            )
            out_nodes.append(fork_obj)
            for parallel in node.parallels:
                parallel_first = lower_sequence(parallel.body, join_id)
                fork_obj.paths.append(ForkPath(firstNodeId=parallel_first or join_id))
            out_nodes.append(Join(id=join_id, displayId=node.displayId, next=successor_id))
            return

    first_top_id = lower_sequence(ast_nodes, terminal_fallthrough)
    initial = InitialNode(id="initial:0", next=first_top_id)
    return Activity(
        name=activity_name,
        id=f"activity:{activity_name}",
        initialNode=initial,
        finalNodes=final_nodes,
        actors=actors,
        nodes=out_nodes,
    )


# ──────────────────────────────────────────────────────────────────────────
# CLI — backwards-compatible wrapper for SKILL.md Phase 4 invocation
# ──────────────────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(description="Decode .activity DSL (BDD-driven)")
    p.add_argument("activity_file", type=Path)
    args = p.parse_args()

    if not args.activity_file.is_file():
        print(f"error: file not found: {args.activity_file}", file=sys.stderr)
        return 2

    try:
        result = parse(args.activity_file.read_text(encoding="utf-8"))
    except NotImplementedError as e:
        print(json.dumps({
            "ok": False,
            "skeleton": True,
            "message": str(e),
            "hint": "scripts/tests/activity-decode.feature is the spec SSOT; implement parse()",
        }, ensure_ascii=False, indent=2))
        return 3  # 3 = skeleton stub, not a real validation result

    print(json.dumps({
        "ok": result.ok,
        "errors": [asdict(e) for e in result.errors],
        "activity": asdict(result.activity) if result.activity else None,
    }, ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
