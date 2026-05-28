#!/usr/bin/env python3
"""Sequence diagram (.sequence.mmd) evaluator.

Strict-subset parser + validator for the Mermaid `sequenceDiagram` dialect
that this skill emits. The BDD suite under `scripts/tests/` is the
executable spec.

Public surface:
- `parse(source: str) -> SequenceDiagramData` — raises `DiagramParseError`
- `normalize_br_tags(s: str) -> str` — `<br>` / `<br/>` → real newline
- CLI: `python3 evaluate.py <file>` — emits JSON, exit 0 ok / 1 invalid / 2 missing.

Output JSON shape:

    {
      "ok": <bool>,
      "errors": [{"line": <int|null>, "message": "<reason>"}, ...],
      "data": {
        "actors":   [{"name","type","description"}, ...],
        "messages": [{"type","from","to","message","activate"?,"consolidatedNames"?}, ...],
        "notes":    [{"placement","actor","message"}, ...],
        "boxes":    [{"name","fill","actors":[...]}, ...]
      }
    }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from pathlib import Path
from typing import Any


# ──────────────────────────────────────────────────────────────────────────
# Enums — mirror MessageLineType / Placement in @specformula/sequence-editor
# ──────────────────────────────────────────────────────────────────────────


class MessageLineType(IntEnum):
    SOLID_OPEN = 0
    DOTTED_OPEN = 1
    SOLID = 2
    DOTTED = 3
    SOLID_CROSS = 4
    DOTTED_CROSS = 5
    SOLID_POINT = 6
    DOTTED_POINT = 7
    BIDIRECTIONAL_SOLID = 8
    BIDIRECTIONAL_DOTTED = 9
    NOTE = 10
    LOOP_START = 11
    LOOP_END = 12
    ALT_START = 13
    ALT_ELSE = 14
    ALT_END = 15
    OPT_START = 16
    OPT_END = 17
    PAR_START = 18
    PAR_AND = 19
    PAR_END = 20
    CRITICAL_START = 21
    CRITICAL_OPTION = 22
    CRITICAL_END = 23
    BREAK_START = 24
    BREAK_END = 25
    RECT_START = 26
    RECT_END = 27
    ACTIVE_START = 28
    ACTIVE_END = 29
    AUTONUMBER = 30


class Placement(IntEnum):
    LEFTOF = 0
    RIGHTOF = 1
    OVER = 2


ARROW_TO_TYPE: dict[str, MessageLineType] = {
    "->": MessageLineType.SOLID_OPEN,
    "->>": MessageLineType.SOLID,
    "-->": MessageLineType.DOTTED_OPEN,
    "-->>": MessageLineType.DOTTED,
    "-x": MessageLineType.SOLID_CROSS,
    "--x": MessageLineType.DOTTED_CROSS,
    "-)": MessageLineType.SOLID_POINT,
    "--)": MessageLineType.DOTTED_POINT,
    "<<->>": MessageLineType.BIDIRECTIONAL_SOLID,
    "<<-->>": MessageLineType.BIDIRECTIONAL_DOTTED,
}

# Longest-first so `-->>` is not eaten by `-->`
ARROW_GLYPHS = sorted(ARROW_TO_TYPE.keys(), key=len, reverse=True)


# ──────────────────────────────────────────────────────────────────────────
# Data classes — mirror SequenceDiagramData
# ──────────────────────────────────────────────────────────────────────────


@dataclass
class Actor:
    name: str
    type: str = "participant"  # "participant" | "actor"
    description: str = ""


@dataclass
class Message:
    type: int  # MessageLineType
    from_: str | None = None
    to: str | None = None
    message: str = ""
    activate: bool | None = None
    consolidatedNames: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": int(self.type), "message": self.message}
        if self.from_ is not None:
            d["from"] = self.from_
        if self.to is not None:
            d["to"] = self.to
        if self.activate is not None:
            d["activate"] = self.activate
        if self.consolidatedNames is not None:
            d["consolidatedNames"] = self.consolidatedNames
        return d


@dataclass
class Note:
    placement: int  # Placement
    actor: Any  # str | list (multi-actor) | [undefined, undefined] frozen bug
    message: str


@dataclass
class Box:
    name: str
    fill: str | None
    actors: list[str] = field(default_factory=list)


@dataclass
class SequenceDiagramData:
    actors: list[Actor] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    boxes: list[Box] = field(default_factory=list)


class DiagramParseError(Exception):
    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


# ──────────────────────────────────────────────────────────────────────────
# Preprocessing helpers
# ──────────────────────────────────────────────────────────────────────────


BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def normalize_br_tags(s: str) -> str:
    return BR_RE.sub("\n", s)


def strip_wrap_prefix(text: str) -> str:
    stripped = text.lstrip()
    for prefix in (":wrap:", ":nowrap:"):
        if stripped.startswith(prefix):
            return stripped[len(prefix):].lstrip()
    return text


# ──────────────────────────────────────────────────────────────────────────
# Tokeniser — split source into directives line by line
# ──────────────────────────────────────────────────────────────────────────


HEADER_RE = re.compile(r"^\s*sequenceDiagram\s*$")
COMMENT_RE = re.compile(r"^\s*%%.*$")
PARTICIPANT_RE = re.compile(
    r"^\s*participant\s+(?P<id>\S+?)(?:\s+as\s+(?P<alias>.+?))?\s*$"
)
ACTOR_DECL_RE = re.compile(
    r"^\s*actor\s+(?P<id>\S+?)(?:\s+as\s+(?P<alias>.+?))?\s*$"
)
CREATE_PARTICIPANT_RE = re.compile(
    r"^\s*create\s+participant\s+(?P<id>\S+?)(?:\s+as\s+(?P<alias>.+?))?\s*$"
)
DESTROY_RE = re.compile(r"^\s*destroy\s+(?P<id>\S+)\s*$")
ACTIVATE_RE = re.compile(r"^\s*activate\s+(?P<id>\S+)\s*$")
DEACTIVATE_RE = re.compile(r"^\s*deactivate\s+(?P<id>\S+)\s*$")
NOTE_RE = re.compile(
    r"^\s*note\s+(?P<placement>right of|left of|over)\s+(?P<actors>[^:]+?)\s*:\s*(?P<text>.+?)\s*$"
)
AUTONUMBER_RE = re.compile(r"^\s*autonumber\b.*$")
TITLE_RE = re.compile(r"^\s*title\s*:?\s+.*$")
ACC_TITLE_RE = re.compile(r"^\s*accTitle\s*:?\s+.*$|^\s*accTitle\s*:\s*.*$")
ACC_DESCR_RE = re.compile(r"^\s*accDescr\s*:?\s+.*$|^\s*accDescr\s*:\s*.*$")
BOX_START_RE = re.compile(
    r"^\s*box\s+(?:(?P<fill>rgb\([^)]*\))\s+)?(?P<name>.+?)\s*$"
)
END_RE = re.compile(r"^\s*end\s*$")
BLOCK_KEYWORDS = {
    "loop": (MessageLineType.LOOP_START, MessageLineType.LOOP_END, None, None),
    "alt": (MessageLineType.ALT_START, MessageLineType.ALT_END, "else", MessageLineType.ALT_ELSE),
    "opt": (MessageLineType.OPT_START, MessageLineType.OPT_END, None, None),
    "par": (MessageLineType.PAR_START, MessageLineType.PAR_END, "and", MessageLineType.PAR_AND),
    "critical": (
        MessageLineType.CRITICAL_START,
        MessageLineType.CRITICAL_END,
        "option",
        MessageLineType.CRITICAL_OPTION,
    ),
    "break": (MessageLineType.BREAK_START, MessageLineType.BREAK_END, None, None),
    "rect": (MessageLineType.RECT_START, MessageLineType.RECT_END, None, None),
}
BLOCK_START_RE = re.compile(
    r"^\s*(?P<keyword>loop|alt|opt|par|critical|break|rect)\b(?P<rest>.*)$"
)


def _parse_message_line(line: str) -> tuple[str, str, str, str] | None:
    """Return (from, to, arrow, text) if `line` is a message; else None."""
    stripped = line.strip()
    for glyph in ARROW_GLYPHS:
        # require whitespace on each side OR end-of-token on left, then `to`
        # follows directly (possibly with `+`/`-` activation marker)
        pattern = re.compile(
            r"^(?P<from>\S+?)\s+" + re.escape(glyph) + r"(?P<act>[+\-])?\s+(?P<to>\S+?)\s*:\s*(?P<text>.+?)\s*$"
        )
        m = pattern.match(stripped)
        if m:
            return m.group("from"), m.group("to"), glyph, m.group("text"), m.group("act")  # type: ignore[return-value]
    return None


# ──────────────────────────────────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────────────────────────────────


def parse(source: str) -> SequenceDiagramData:
    data = SequenceDiagramData()
    actor_index: dict[str, int] = {}
    box_actor_to_box: dict[str, int] = {}

    def add_actor(name: str, type_: str = "participant", description: str = "") -> None:
        if name in actor_index:
            return
        actor_index[name] = len(data.actors)
        data.actors.append(Actor(name=name, type=type_, description=description))

    src = normalize_br_tags(source)
    raw_lines = src.splitlines()

    # Strip an optional leading sequenceDiagram header (first non-blank only).
    started = False
    lines: list[tuple[int, str]] = []
    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip("\r")
        if not started:
            if not line.strip():
                continue
            started = True
            if HEADER_RE.match(line):
                continue  # header consumed
        lines.append((idx, line))

    # Detect garbage: any non-empty line that begins with non-identifier and
    # has no recognised keyword — flagged once during the main loop.

    has_any_content = any(t[1].strip() for t in lines)
    if not has_any_content and started is False:
        # truly empty source — just return empty data; not an error
        return data
    if not has_any_content and started is True:
        # header-only — empty diagram
        return data

    # Active box context (for `box ... end`)
    box_stack: list[int] = []
    # Block stack: list of dicts with end_type
    block_stack: list[dict[str, Any]] = []

    consecutive_self_call: list[Message] = []

    def flush_self_call_consolidation() -> None:
        nonlocal consecutive_self_call
        if len(consecutive_self_call) >= 2:
            first = consecutive_self_call[0]
            names = [m.message for m in consecutive_self_call]
            first.consolidatedNames = names
            # remove subsequent ones from data.messages
            for extra in consecutive_self_call[1:]:
                if extra in data.messages:
                    data.messages.remove(extra)
        consecutive_self_call = []

    def append_message(msg: Message) -> None:
        # self-call consolidation only applies to SOLID / DOTTED signals
        consolidatable = msg.type in (MessageLineType.SOLID, MessageLineType.DOTTED)
        if (
            consolidatable
            and msg.from_ is not None
            and msg.from_ == msg.to
        ):
            if (
                consecutive_self_call
                and consecutive_self_call[-1].from_ == msg.from_
                and consecutive_self_call[-1].type == msg.type
            ):
                data.messages.append(msg)
                consecutive_self_call.append(msg)
                return
            flush_self_call_consolidation()
            data.messages.append(msg)
            consecutive_self_call.append(msg)
            return
        flush_self_call_consolidation()
        data.messages.append(msg)

    for lineno, raw in lines:
        line = raw.strip()
        if not line:
            continue
        if COMMENT_RE.match(raw):
            continue
        if TITLE_RE.match(raw) or ACC_TITLE_RE.match(raw) or ACC_DESCR_RE.match(raw):
            continue

        # box ... end — actors inside go into the box
        m = BOX_START_RE.match(raw)
        if m and line.lower().startswith("box "):
            fill = m.group("fill")
            name = m.group("name").strip()
            box = Box(name=name, fill=fill)
            data.boxes.append(box)
            box_stack.append(len(data.boxes) - 1)
            continue
        if END_RE.match(raw):
            if box_stack:
                box_stack.pop()
                continue
            if block_stack:
                blk = block_stack.pop()
                end_type = blk["end_type"]
                if end_type is not None:
                    data.messages.append(Message(type=end_type, message=blk.get("label", "")))
                continue
            raise DiagramParseError(f"Unexpected 'end'", line=lineno)

        # block START / intermediate keywords
        bm = BLOCK_START_RE.match(raw)
        if bm:
            kw = bm.group("keyword")
            rest = bm.group("rest").strip()
            start_t, end_t, inter_kw, inter_t = BLOCK_KEYWORDS[kw]
            data.messages.append(Message(type=start_t, message=rest))
            block_stack.append({"end_type": end_t, "label": rest, "intermediate_kw": inter_kw, "intermediate_t": inter_t})
            continue
        # intermediate keyword (else / and / option)
        if block_stack:
            top = block_stack[-1]
            ikw = top["intermediate_kw"]
            if ikw is not None:
                pat = re.compile(rf"^\s*{ikw}\b(?P<rest>.*)$")
                im = pat.match(raw)
                if im:
                    data.messages.append(Message(type=top["intermediate_t"], message=im.group("rest").strip()))
                    continue

        # participant / actor / create / destroy
        m = CREATE_PARTICIPANT_RE.match(raw)
        if m:
            name = m.group("id")
            alias = m.group("alias") or ""
            add_actor(name, "participant", alias)
            if box_stack:
                data.boxes[box_stack[-1]].actors.append(name)
            continue
        m = PARTICIPANT_RE.match(raw)
        if m:
            name = m.group("id")
            alias = m.group("alias") or ""
            add_actor(name, "participant", alias)
            if box_stack:
                data.boxes[box_stack[-1]].actors.append(name)
            continue
        m = ACTOR_DECL_RE.match(raw)
        if m:
            name = m.group("id")
            alias = m.group("alias") or ""
            add_actor(name, "actor", alias)
            if box_stack:
                data.boxes[box_stack[-1]].actors.append(name)
            continue
        m = DESTROY_RE.match(raw)
        if m:
            continue  # parsed but emits no message
        m = ACTIVATE_RE.match(raw)
        if m:
            data.messages.append(Message(type=MessageLineType.ACTIVE_START, from_=m.group("id")))
            continue
        m = DEACTIVATE_RE.match(raw)
        if m:
            data.messages.append(Message(type=MessageLineType.ACTIVE_END, from_=m.group("id")))
            continue
        if AUTONUMBER_RE.match(raw):
            data.messages.append(Message(type=MessageLineType.AUTONUMBER))
            continue

        # note ... : <text>
        m = NOTE_RE.match(raw)
        if m:
            placement_key = m.group("placement")
            placement = {"right of": Placement.RIGHTOF, "left of": Placement.LEFTOF, "over": Placement.OVER}[placement_key]
            actors_part = m.group("actors").strip()
            text = m.group("text").strip()
            if "," in actors_part:
                # Multi-actor frozen bug — JISON grammar yields [undefined, undefined]
                actor_field: Any = [None, None]
            else:
                actor_field = actors_part
                add_actor(actors_part)
            data.notes.append(Note(placement=int(placement), actor=actor_field, message=text))
            # Also append as NOTE-typed message for layout ordering
            data.messages.append(Message(type=MessageLineType.NOTE, message=text))
            continue

        # message
        parsed = _parse_message_line(raw)
        if parsed is not None:
            from_, to, arrow, text, act_marker = parsed
            arrow_type = ARROW_TO_TYPE.get(arrow)
            if arrow_type is None:
                raise DiagramParseError(f"Unknown arrow glyph: {arrow!r}", line=lineno)
            add_actor(from_)
            add_actor(to)
            text = strip_wrap_prefix(text)
            msg = Message(type=arrow_type, from_=from_, to=to, message=text)
            if act_marker == "+":
                msg.activate = True
                data.messages.append(Message(type=MessageLineType.ACTIVE_START, from_=to))
            elif act_marker == "-":
                msg.activate = False
                data.messages.append(Message(type=MessageLineType.ACTIVE_END, from_=to))
            append_message(msg)
            continue

        raise DiagramParseError(f"Parse error on line {lineno}: {line!r}", line=lineno)

    flush_self_call_consolidation()

    # Unclosed blocks / boxes — treat as syntax error
    if block_stack:
        raise DiagramParseError(
            f"Unterminated block ({len(block_stack)} unclosed)", line=lines[-1][0] if lines else None
        )
    if box_stack:
        raise DiagramParseError("Unterminated box", line=lines[-1][0] if lines else None)

    return data


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────


def _to_json(data: SequenceDiagramData) -> dict[str, Any]:
    return {
        "actors": [asdict(a) for a in data.actors],
        "messages": [m.as_dict() for m in data.messages],
        "notes": [asdict(n) for n in data.notes],
        "boxes": [asdict(b) for b in data.boxes],
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluate .sequence.mmd syntax")
    p.add_argument("target", type=Path)
    args = p.parse_args()

    if not args.target.is_file():
        print(f"error: file not found: {args.target}", file=sys.stderr)
        return 2

    try:
        data = parse(args.target.read_text(encoding="utf-8"))
    except DiagramParseError as e:
        print(json.dumps(
            {"ok": False, "errors": [{"line": e.line, "message": str(e)}], "data": None},
            ensure_ascii=False,
            indent=2,
        ))
        return 1

    print(json.dumps({"ok": True, "errors": [], "data": _to_json(data)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
