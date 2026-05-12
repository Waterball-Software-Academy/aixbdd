"""Parser — Activity DSL (flat event-flow Mermaid dialect) → AST.

Recognised tokens per ``sf-desktop-app-electron/To-Be-整合/README.md``::

    [STEP:N]                  ← sequential action
    [DECISION:Nx]             ← branch point
    [BRANCH:Nx:<guard>]       ← branch edge (optional guard label)
    [FORK:Nx]                 ← parallel split
    [PARALLEL:Nx]             ← parallel fragment body
    [END]                     ← terminal marker

MVP — regex-based; a proper Mermaid parser is deferred. Good enough for the
dialect actually used in fixture test data.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

TOKEN_RE = re.compile(
    r"\[(?P<kind>STEP|DECISION|BRANCH|FORK|PARALLEL|END)(?::(?P<id>[\w\.]+))?(?::(?P<guard>[^\]]+))?\]"
    r"\s*(?P<label>.*)"
)


@dataclass(slots=True)
class Node:
    kind: str                     # STEP | DECISION | BRANCH | FORK | PARALLEL | END
    id: str | None = None
    guard: str | None = None
    label: str = ""
    children: list["Node"] = field(default_factory=list)

    @property
    def is_action(self) -> bool:
        """Action nodes are what Policy 1 requires to be covered at least once."""
        return self.kind in ("STEP", "PARALLEL")


@dataclass(slots=True)
class ActivityAst:
    source_file: Path
    title: str | None
    actors: list[str] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)


def parse_file(path: Path) -> ActivityAst:
    """Parse a single activity file into an AST."""
    text = path.read_text(encoding="utf-8")
    return parse_text(text, source_file=path)


def parse_text(text: str, *, source_file: Path | None = None) -> ActivityAst:
    ast = ActivityAst(
        source_file=source_file or Path("<memory>"),
        title=None,
    )
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("%% title:"):
            ast.title = stripped.split(":", 1)[1].strip()
            continue
        if stripped.startswith("%% actor:"):
            ast.actors.append(stripped.split(":", 1)[1].strip())
            continue
        if stripped.startswith("%%"):
            continue  # other comments
        match = TOKEN_RE.search(stripped)
        if not match:
            continue  # ignore non-token lines (edge arrows, layout hints, etc.)
        node = Node(
            kind=match["kind"],
            id=match["id"],
            guard=match["guard"],
            label=match["label"].strip(),
        )
        ast.nodes.append(node)
    return ast


def format_ast(ast: ActivityAst) -> str:
    lines = [f"# {ast.source_file.name}", f"title: {ast.title or '(none)'}", f"actors: {ast.actors or []}", ""]
    for n in ast.nodes:
        bits = [n.kind]
        if n.id:
            bits.append(f"id={n.id}")
        if n.guard:
            bits.append(f"guard={n.guard}")
        if n.label:
            bits.append(f"label={n.label!r}")
        lines.append("- " + "  ".join(bits))
    return "\n".join(lines)
