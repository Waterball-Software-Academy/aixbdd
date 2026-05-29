#!/usr/bin/env python3
"""Class diagram (.class.mmd) evaluator.

Strict-subset parser + validator for the Mermaid `classDiagram` dialect
that this skill emits. The BDD suite under `scripts/tests/` is the
executable spec.

Public surface:
- `parse(source: str) -> ClassDiagramData` — raises `DiagramParseError`
- CLI: `python3 evaluate.py <file>` — emits JSON, exit 0 ok / 1 invalid / 2 missing.

Output JSON shape:

    {
      "ok": <bool>,
      "errors": [{"line": <int|null>, "message": "<reason>"}, ...],
      "data": {
        "classes":    [<class>...],
        "relations":  [<relation>...],
        "namespaces": [{"id","classIds":[...]}, ...],
        "notes":      [{"className","text"}, ...]
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
# Enums — mirror RelationType / LineType in @specformula/class-editor
# ──────────────────────────────────────────────────────────────────────────


class RelationType(IntEnum):
    AGGREGATION = 0
    EXTENSION = 1
    COMPOSITION = 2
    DEPENDENCY = 3
    LOLLIPOP = 4


class LineType(IntEnum):
    LINE = 0
    DOTTED_LINE = 1


# Glyph → (type1 numeric or "none", lineType, type2 numeric or "none")
# Order matters: longest glyph first so `<|--` is not eaten by `--`.
GLYPH_MAP: list[tuple[str, Any, LineType, Any]] = [
    ("<|--", RelationType.EXTENSION, LineType.LINE, "none"),
    ("--|>", "none", LineType.LINE, RelationType.EXTENSION),
    ("..|>", "none", LineType.DOTTED_LINE, RelationType.EXTENSION),
    ("*--", RelationType.COMPOSITION, LineType.LINE, "none"),
    ("o--", RelationType.AGGREGATION, LineType.LINE, "none"),
    ("..>", "none", LineType.DOTTED_LINE, "none"),
    ("()--", RelationType.LOLLIPOP, LineType.LINE, "none"),
    ("--()", "none", LineType.LINE, RelationType.LOLLIPOP),
    ("-->", "none", LineType.LINE, "none"),
    ("..", "none", LineType.DOTTED_LINE, "none"),
    ("--", "none", LineType.LINE, "none"),
]


# ──────────────────────────────────────────────────────────────────────────
# Data classes — mirror ClassDiagramData
# ──────────────────────────────────────────────────────────────────────────


@dataclass
class Member:
    name: str
    visibility: str = ""
    memberType: str = "attribute"  # "attribute" | "method"
    classifier: str | None = None  # "static" | "abstract" | None


@dataclass
class ClassEntry:
    name: str
    label: str | None = None
    type: str = ""  # generic parameter, e.g. "T"
    annotations: list[str] = field(default_factory=list)
    members: list[Member] = field(default_factory=list)
    methods: list[Member] = field(default_factory=list)
    namespace: str | None = None
    cssClasses: list[str] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)


@dataclass
class RelationCore:
    type1: Any  # int or "none"
    type2: Any  # int or "none"
    lineType: int


@dataclass
class Relation:
    id1: str
    id2: str
    relation: RelationCore
    relationTitle1: str = ""
    relationTitle2: str = ""
    title: str = ""


@dataclass
class Namespace:
    id: str
    classIds: list[str] = field(default_factory=list)


@dataclass
class Note:
    className: str | None
    text: str


@dataclass
class ClassDiagramData:
    classes: list[ClassEntry] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    namespaces: list[Namespace] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)


class DiagramParseError(Exception):
    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


# ──────────────────────────────────────────────────────────────────────────
# Preprocessing
# ──────────────────────────────────────────────────────────────────────────


HEADER_RE = re.compile(r"^\s*classDiagram(?:-v2)?\s*$")
COMMENT_RE = re.compile(r"^\s*%%.*$")
TITLE_RE = re.compile(r"^\s*title\b.*$")
ACC_TITLE_RE = re.compile(r"^\s*accTitle\s*:?.*$")
ACC_DESCR_RE = re.compile(r"^\s*accDescr\s*:?.*$")
DIRECTION_RE = re.compile(r"^\s*direction\s+(TB|BT|LR|RL)\s*$")


CLASS_KEYWORD_RE = re.compile(r"^\s*class\s+(?P<rest>.+?)\s*$")
NAMESPACE_RE = re.compile(r"^\s*namespace\s+(?P<id>\S+)\s*\{?\s*$")
NOTE_FOR_RE = re.compile(
    r"^\s*note\s+for\s+(?P<class>\S+)\s+\"(?P<text>.*)\"\s*$"
)
NOTE_FLOATING_RE = re.compile(r"^\s*note\s+\"(?P<text>.*)\"\s*$")
CSS_CLASS_RE = re.compile(
    r"^\s*cssClass\s+\"(?P<class>[^\"]+)\"\s+(?P<value>.+?)\s*$"
)
STYLE_RE = re.compile(r"^\s*style\s+(?P<class>\S+)\s+(?P<rules>.+?)\s*$")
END_BRACE_RE = re.compile(r"^\s*\}\s*$")


CLASS_LABEL_RE = re.compile(
    r"^(?P<name>[A-Za-z_][\w]*)\s*\[\"(?P<label>.*)\"\]\s*$"
)
CLASS_GENERIC_RE = re.compile(r"^(?P<name>[A-Za-z_][\w]*)~(?P<type>[^~]+)~$")
# Mermaid `<<...>>` 內容只接受單一 alphaNumToken（實務上等同 [A-Za-z0-9_]+）。
# 連字符（-）會被 lex 拆成額外 token、產生 parse error。
ANNOTATION_RE = re.compile(r"^\s*<<(?P<text>[A-Za-z0-9_]+)>>\s*$")


# member-line patterns inside class body
VISIBILITY_CHARS = ("+", "-", "#", "~")


def _id(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][\w]*$", s))


def _parse_class_header(rest: str, entry: ClassEntry) -> str:
    """`rest` is the text after `class `. Returns the resolved class name."""
    rest = rest.strip()
    m = CLASS_LABEL_RE.match(rest)
    if m:
        entry.name = m.group("name")
        entry.label = m.group("label")
        return entry.name
    m = CLASS_GENERIC_RE.match(rest)
    if m:
        entry.name = m.group("name")
        entry.type = m.group("type")
        return entry.name
    # strip trailing { if present
    rest_no_brace = rest.rstrip("{").rstrip()
    # strip optional cardinality / annotation suffix — keep just the name
    if _id(rest_no_brace):
        entry.name = rest_no_brace
        return entry.name
    # last resort: take first identifier-ish token
    m = re.match(r"^([A-Za-z_][\w]*)", rest_no_brace)
    if not m:
        raise DiagramParseError(f"Invalid class declaration: {rest!r}")
    entry.name = m.group(1)
    return entry.name


def _parse_member_line(raw: str) -> Member:
    text = raw.strip()
    visibility = ""
    if text and text[0] in VISIBILITY_CHARS:
        visibility = text[0]
        text = text[1:]
    classifier: str | None = None
    if text.endswith("$"):
        classifier = "static"
        text = text[:-1]
    elif text.endswith("*"):
        classifier = "abstract"
        text = text[:-1]
    member_type = "method" if "(" in text and ")" in text else "attribute"
    return Member(name=text.strip(), visibility=visibility, memberType=member_type, classifier=classifier)


def _strip_title_directives(source: str) -> str:
    """Remove `title …` / `accTitle …` / `accDescr …` lines (regex pre-pass)."""
    out: list[str] = []
    for raw in source.splitlines():
        if TITLE_RE.match(raw) or ACC_TITLE_RE.match(raw) or ACC_DESCR_RE.match(raw):
            continue
        out.append(raw)
    return "\n".join(out)


def _unescape_note(text: str) -> str:
    """Mirror upstream behaviour: literal `\\n` becomes a real newline."""
    return text.replace("\\n", "\n")


def _parse_relation_line(line: str, data: ClassDiagramData) -> bool:
    """If `line` is a relation, append it and return True. Else return False.

    Handles cardinality quoting: `A "1" --> "*" B : label`.
    """
    stripped = line.strip()
    for glyph, t1, lt, t2 in GLYPH_MAP:
        token = " " + glyph + " "
        idx = stripped.find(token)
        if idx == -1:
            continue
        left = stripped[:idx].strip()
        right = stripped[idx + len(token):].strip()
        # left: <Id> ["title1"]?
        title1, id1 = _split_id_and_cardinality(left, "left")
        if not id1 or not _id(id1):
            continue
        # right: <Id|"title2"> rest with optional ": label"
        title2, id2_and_rest = _split_id_and_cardinality(right, "right")
        # right after cardinality stripping should be Id [ : label ]
        if ":" in id2_and_rest:
            id2, title = id2_and_rest.split(":", 1)
            id2 = id2.strip()
            title = title.strip()
        else:
            id2 = id2_and_rest.strip()
            title = ""
        if not _id(id2):
            continue
        relation = Relation(
            id1=id1,
            id2=id2,
            relation=RelationCore(
                type1=int(t1) if isinstance(t1, IntEnum) else t1,
                type2=int(t2) if isinstance(t2, IntEnum) else t2,
                lineType=int(lt),
            ),
            relationTitle1=title1,
            relationTitle2=title2,
            title=title,
        )
        data.relations.append(relation)
        _ensure_class(data, id1)
        _ensure_class(data, id2)
        return True
    return False


def _split_id_and_cardinality(side: str, side_kind: str) -> tuple[str, str]:
    """Split `<Id>` from a single `"cardinality"` token, on the named side.

    Returns (cardinality_text, remaining_side_text). For the left side the
    cardinality (if present) comes right before the arrow (i.e. trailing). For
    the right side it comes right after the arrow (i.e. leading).
    """
    text = side.strip()
    if side_kind == "left":
        # Patterns: `A "1"` or `A` (cardinality is trailing quoted token)
        m = re.match(r'^(?P<id>\S+)\s+"(?P<title>[^"]*)"$', text)
        if m:
            return m.group("title"), m.group("id")
        return "", text
    else:
        # Right side may carry leading `"*"` cardinality then class id.
        m = re.match(r'^"(?P<title>[^"]*)"\s+(?P<rest>.*)$', text)
        if m:
            return m.group("title"), m.group("rest").strip()
        return "", text


def _ensure_class(data: ClassDiagramData, name: str) -> ClassEntry:
    for c in data.classes:
        if c.name == name:
            return c
    entry = ClassEntry(name=name)
    data.classes.append(entry)
    return entry


# ──────────────────────────────────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────────────────────────────────


def parse(source: str) -> ClassDiagramData:
    data = ClassDiagramData()

    src = _strip_title_directives(source)
    raw_lines = src.splitlines()

    # Strip leading blank lines + optional header
    started = False
    body: list[tuple[int, str]] = []
    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip("\r")
        if not started:
            if not line.strip():
                continue
            started = True
            if HEADER_RE.match(line):
                continue  # header consumed
        body.append((idx, line))

    if not any(line.strip() for _, line in body) and started:
        # header-only body — illegal per feature file
        raise DiagramParseError(
            "Empty body — minimum legal input is one statement", line=None
        )

    # state for multi-line constructs
    current_class_block: ClassEntry | None = None
    current_namespace: Namespace | None = None
    pending_class_decl: str | None = None  # class header awaiting `{` continuation

    i = 0
    while i < len(body):
        lineno, raw = body[i]
        line = raw.strip()
        i += 1
        if not line:
            continue
        if COMMENT_RE.match(raw):
            continue
        if DIRECTION_RE.match(raw):
            continue

        # inside class body — slurp members
        if current_class_block is not None:
            if END_BRACE_RE.match(raw):
                current_class_block = None
                continue
            ann = ANNOTATION_RE.match(line)
            if ann:
                current_class_block.annotations.append(ann.group("text"))
                continue
            # 任何 <<…>> 沒過嚴格 annotation 規則一律當語法錯，避免靜默吞掉非法 stereotype
            if line.lstrip().startswith("<<") or line.rstrip().endswith(">>"):
                raise DiagramParseError(
                    f"Invalid annotation: {line.strip()!r}（內容只允許 [A-Za-z0-9_]+）",
                    line=lineno,
                )
            member = _parse_member_line(line)
            if "(" in member.name and ")" in member.name:
                current_class_block.methods.append(member)
            else:
                current_class_block.members.append(member)
            continue

        # inside namespace block — slurp class declarations only
        if current_namespace is not None:
            if END_BRACE_RE.match(raw):
                current_namespace = None
                continue
            m = CLASS_KEYWORD_RE.match(raw)
            if m:
                rest = m.group("rest")
                entry = _ensure_class(data, "")
                _parse_class_header(rest, entry)
                # ensure not duplicated
                if all(c.name != entry.name for c in data.classes):
                    data.classes.append(entry)
                entry.namespace = current_namespace.id
                current_namespace.classIds.append(entry.name)
                continue
            continue

        # namespace start
        m = NAMESPACE_RE.match(raw)
        if m:
            ns = Namespace(id=m.group("id"))
            data.namespaces.append(ns)
            current_namespace = ns
            continue

        # class declaration
        m = CLASS_KEYWORD_RE.match(raw)
        if m:
            rest = m.group("rest")
            stripped_rest = rest.strip()
            opens_block = stripped_rest.endswith("{")
            if opens_block:
                stripped_rest = stripped_rest[:-1].strip()
            entry = ClassEntry(name="")
            _parse_class_header(stripped_rest, entry)
            existing = next((c for c in data.classes if c.name == entry.name), None)
            if existing is not None:
                # merge label / type onto existing entry
                if entry.label is not None:
                    existing.label = entry.label
                if entry.type:
                    existing.type = entry.type
                entry = existing
            else:
                data.classes.append(entry)
            if opens_block:
                current_class_block = entry
            continue

        # note for X "text"
        m = NOTE_FOR_RE.match(raw)
        if m:
            cls_name = m.group("class")
            text = _unescape_note(m.group("text"))
            exists = any(c.name == cls_name for c in data.classes)
            data.notes.append(Note(className=cls_name if exists else None, text=text))
            continue

        # floating note
        m = NOTE_FLOATING_RE.match(raw)
        if m:
            data.notes.append(Note(className=None, text=_unescape_note(m.group("text"))))
            continue

        # cssClass "ClassName" identifier
        m = CSS_CLASS_RE.match(raw)
        if m:
            cls = _ensure_class(data, m.group("class"))
            cls.cssClasses.append(m.group("value").strip())
            continue

        # style ClassName fill:#abc,stroke:#def
        m = STYLE_RE.match(raw)
        if m:
            cls = _ensure_class(data, m.group("class"))
            parts = [p.strip() for p in m.group("rules").split(",") if p.strip()]
            cls.styles.extend(parts)
            continue

        # relation
        if _parse_relation_line(line, data):
            continue

        raise DiagramParseError(f"Parse error on line {lineno}: {line!r}", line=lineno)

    if current_class_block is not None or current_namespace is not None:
        raise DiagramParseError("Unterminated block", line=None)

    if started and not (data.classes or data.relations or data.notes or data.namespaces):
        raise DiagramParseError(
            "Empty body — minimum legal input is one statement", line=None
        )

    return data


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────


def _to_json(data: ClassDiagramData) -> dict[str, Any]:
    def member_dict(m: Member) -> dict[str, Any]:
        return asdict(m)

    return {
        "classes": [
            {
                **{k: v for k, v in asdict(c).items() if k not in {"members", "methods"}},
                "members": [member_dict(m) for m in c.members],
                "methods": [member_dict(m) for m in c.methods],
            }
            for c in data.classes
        ],
        "relations": [
            {
                "id1": r.id1,
                "id2": r.id2,
                "relation": asdict(r.relation),
                "relationTitle1": r.relationTitle1,
                "relationTitle2": r.relationTitle2,
                "title": r.title,
            }
            for r in data.relations
        ],
        "namespaces": [asdict(n) for n in data.namespaces],
        "notes": [asdict(n) for n in data.notes],
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Evaluate .class.mmd syntax")
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
