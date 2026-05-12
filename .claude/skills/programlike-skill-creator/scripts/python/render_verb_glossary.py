#!/usr/bin/env python3
"""
render_verb_glossary.py — inject canonical verb cheatsheet into a SKILL.md.

The verb glossary blockquote is **canonical and identical across all program-like
SKILL.md files** (per spec.md §27). Rather than have each skill author hand-maintain
their own subset (drift-prone), this script reads the SSOT cheatsheet and renders
it into SKILL.md as a markdown blockquote between auto-managed markers.

Usage:
    render_verb_glossary.py <skill_dir> [--cheatsheet PATH]

Default cheatsheet = `<this_script>/../../references/verb-cheatsheet.md`
(i.e. programlike-skill-creator/references/verb-cheatsheet.md).

Behaviour:
- If `<!-- VERB-GLOSSARY:BEGIN ... -->` / `<!-- VERB-GLOSSARY:END -->` markers exist
  in SKILL.md → replace content between them.
- Else if a legacy `> **Program-like SKILL.md` or `> **Verb glossary` blockquote
  exists between H1 and `## §1 REFERENCES` → replace it.
- Else → insert a fresh block immediately before `## §1 REFERENCES`.

Idempotent: re-running on the same SKILL.md produces the same result.

Exit codes: 0 = OK; 1 = SKILL.md missing `## §1 REFERENCES`; 2 = usage / IO error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DEFAULT_CHEATSHEET = (
    Path(__file__).resolve().parents[2] / "references" / "verb-cheatsheet.md"
)

BEGIN = (
    "<!-- VERB-GLOSSARY:BEGIN — auto-rendered from "
    "programlike-skill-creator/references/verb-cheatsheet.md by "
    "render_verb_glossary.py; do not hand-edit -->"
)
END = "<!-- VERB-GLOSSARY:END -->"


def strip_leading_html_comment(text: str) -> str:
    """Strip a single leading `<!-- ... -->` block (the SSOT file's editor note)."""
    m = re.match(r"\s*<!--.*?-->\s*", text, re.DOTALL)
    return text[m.end():] if m else text


def render_block(cheatsheet_text: str) -> str:
    """Wrap cheatsheet body as markdown blockquote between auto-managed markers."""
    body = strip_leading_html_comment(cheatsheet_text).strip()
    quoted = "\n".join("> " + line if line.strip() else ">" for line in body.splitlines())
    return f"{BEGIN}\n{quoted}\n{END}"


def inject(skill_md: Path, block: str) -> str:
    """Inject block into SKILL.md. Returns one of: replaced-markers / replaced-legacy / inserted."""
    text = skill_md.read_text(encoding="utf-8")

    # Case 1: markers already present → replace between them
    if BEGIN in text and END in text:
        pattern = re.escape(BEGIN) + r".*?" + re.escape(END)
        new = re.sub(pattern, lambda _: block, text, count=1, flags=re.DOTALL)
        skill_md.write_text(new, encoding="utf-8")
        return "replaced-markers"

    # Case 2: legacy hand-written blockquote (no markers) → detect and replace
    legacy = re.compile(
        r"> \*\*(?:Program-like SKILL\.md|Verb glossary)[\s\S]*?(?=\n*## §1 REFERENCES)",
    )
    m = legacy.search(text)
    if m:
        prefix = text[: m.start()].rstrip("\n") + "\n\n"
        suffix = text[m.end():].lstrip("\n")
        new = prefix + block + "\n\n" + suffix
        skill_md.write_text(new, encoding="utf-8")
        return "replaced-legacy"

    # Case 3: nothing there → insert before §1 REFERENCES
    marker = "## §1 REFERENCES"
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"error: '{marker}' not found in {skill_md}")
    prefix = text[:idx].rstrip("\n") + "\n\n"
    suffix = text[idx:]
    new = prefix + block + "\n\n" + suffix
    skill_md.write_text(new, encoding="utf-8")
    return "inserted"


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2

    skill_dir = Path(args[0]).resolve()
    cheatsheet = DEFAULT_CHEATSHEET
    if "--cheatsheet" in args:
        i = args.index("--cheatsheet")
        if i + 1 >= len(args):
            print("error: --cheatsheet needs a path argument", file=sys.stderr)
            return 2
        cheatsheet = Path(args[i + 1]).resolve()

    if not cheatsheet.is_file():
        print(f"error: cheatsheet not found at {cheatsheet}", file=sys.stderr)
        return 2

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"error: SKILL.md not found at {skill_md}", file=sys.stderr)
        return 2

    block = render_block(cheatsheet.read_text(encoding="utf-8"))
    action = inject(skill_md, block)
    print(f"OK [{action}] {skill_md}  ← {cheatsheet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
