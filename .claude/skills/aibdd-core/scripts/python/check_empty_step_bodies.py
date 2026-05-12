#!/usr/bin/env python3
"""
check_empty_step_bodies.py — PF-EMPTY-BODY gate (log 260428-03)

Scan TypeScript / JavaScript step-def files for empty step-def bodies (false-green
hazard) and fail when ratio exceeds threshold.

Empty body patterns (per /aibdd-red references/dsl-mapping-protocol.md §6 R-FB-08):
  - `async () => {}`
  - `async (...args) => {}`
  - `async () => { /* only comments */ }`
  - `async () => {\n  // comment\n}`
  - `async () => {\n   \n}` (whitespace-only)

Why this matters:
  Spec 065 mission-control case had 121/124 (97.6%) empty bodies that bypassed
  PF-12 / PF-15b / PF-18 / PF-19 / PF-23 because all those gates verify
  "exists / matches / no-skip" but none verify "does meaningful work".
  Empty body is more dangerous than `throw new Error('RED-PENDING')` because
  PENDING throw at least makes runtime fail; empty body silently passes the
  step-level check, leading the entire scenario to false-green.

Usage:
  check_empty_step_bodies.py <step_defs_glob> [--threshold 0.10]
                             [--out report.md]
                             [--allow-marked]

Exit codes:
  0 — empty-body ratio <= threshold (or zero step-defs found = vacuous PASS)
  1 — empty-body ratio > threshold; report written; Phase 7 should refuse complete
  2 — usage error / file not readable
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path
from typing import Iterator, NamedTuple


# ---------------------------------------------------------------------------
# Regex strategy: find each step-def call (Given/When/Then/And/But) followed
# by an arrow function. Capture the function body text to inspect emptiness.
# Tolerates multi-line patterns + complex param lists.
# ---------------------------------------------------------------------------
STEP_DEF_RE = re.compile(
    r"""
    \b(?P<keyword>Given|When|Then|And|But)        # step-def keyword
    \s*\(                                          # opening (
    (?:[^()]|\([^)]*\))*?                          # pattern string + maybe options (no nested calls)
    ,\s*                                           # comma before handler
    async\s*\(                                     # async (
    (?P<params>[^)]*)                              # parameters
    \)\s*=>\s*                                     # ) =>
    \{(?P<body>(?:[^{}]|\{[^{}]*\})*)\}            # { body } — single nesting level supported
    """,
    re.VERBOSE | re.DOTALL,
)

# Strip JS line + block comments + whitespace. Anything left = real statements.
LINE_COMMENT_RE = re.compile(r"//[^\n]*")
BLOCK_COMMENT_RE = re.compile(r"/\*[\s\S]*?\*/", re.DOTALL)
ALLOW_MARKER_RE = re.compile(
    r"//\s*@allow-empty-stub\s*[:=]\s*([^\n]*)",  # explicit opt-out marker
    re.IGNORECASE,
)


class StepDef(NamedTuple):
    file: Path
    line: int
    keyword: str
    is_empty: bool
    has_allow_marker: bool
    allow_reason: str  # populated only when has_allow_marker is True


def line_of(text: str, offset: int) -> int:
    """1-based line number for character offset."""
    return text.count("\n", 0, offset) + 1


def body_is_empty(body: str) -> bool:
    """True if body contains no executable statement after stripping comments + whitespace."""
    stripped = BLOCK_COMMENT_RE.sub("", body)
    stripped = LINE_COMMENT_RE.sub("", stripped)
    return stripped.strip() == ""


def scan_file(path: Path) -> Iterator[StepDef]:
    text = path.read_text(encoding="utf-8")
    for match in STEP_DEF_RE.finditer(text):
        body = match.group("body") or ""
        is_empty = body_is_empty(body)
        # Look for allow marker within the body or immediately after the closing brace
        # (one-line tolerance window of 200 chars)
        marker_window = text[match.start(): match.end() + 200]
        marker_match = ALLOW_MARKER_RE.search(marker_window)
        yield StepDef(
            file=path,
            line=line_of(text, match.start()),
            keyword=match.group("keyword"),
            is_empty=is_empty,
            has_allow_marker=marker_match is not None,
            allow_reason=(marker_match.group(1).strip() if marker_match else ""),
        )


def expand_glob(pattern: str) -> list[Path]:
    matches = [Path(p) for p in glob.glob(pattern, recursive=True)]
    return [p for p in matches if p.is_file() and p.suffix in (".ts", ".tsx", ".js", ".mjs")]


def write_report(out_path: Path, total: int, empty: list[StepDef], allowed: list[StepDef], threshold: float) -> None:
    ratio = (len(empty) / total * 100) if total else 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Empty Step Body Report (PF-EMPTY-BODY gate)",
        "",
        f"- Total step-defs scanned: **{total}**",
        f"- Empty bodies (counted): **{len(empty)}**",
        f"- Empty bodies (allowed via `@allow-empty-stub`): **{len(allowed)}**",
        f"- Empty ratio (counted/total): **{ratio:.1f}%**",
        f"- Threshold: **{threshold * 100:.1f}%**",
        f"- Verdict: **{'FAIL' if ratio > threshold * 100 else 'PASS'}**",
        "",
        "## Why this matters",
        "",
        "Empty step-def body silently passes the step-level check; entire scenario can",
        "false-green even though no anchor / assertion was invoked. See log",
        "`260428-03-aibdd-reinforce-stub農場讓feature測試效力歸零的多層gate漏洞.md`.",
        "",
        "## Counted empty-body offenders",
        "",
    ]
    if not empty:
        lines.append("(none)")
    else:
        lines.append("| File | Line | Keyword |")
        lines.append("|---|---|---|")
        for sd in empty:
            lines.append(f"| `{sd.file}` | {sd.line} | `{sd.keyword}` |")
    if allowed:
        lines.extend([
            "",
            "## Allowed via `@allow-empty-stub` marker",
            "",
            "| File | Line | Keyword | Reason |",
            "|---|---|---|---|",
        ])
        for sd in allowed:
            lines.append(f"| `{sd.file}` | {sd.line} | `{sd.keyword}` | {sd.allow_reason or '(no reason given)'} |")
    lines.extend([
        "",
        "## Remediation",
        "",
        "1. Replace each empty body with anchor-bound implementation (per /aibdd-red §3 Step 3).",
        "2. If implementation is genuinely deferred, replace `{}` with `throw new Error('RED-PENDING: <why>')` — at least it fails loudly.",
        "3. Only as last resort, add `// @allow-empty-stub: <PF-11-class>` marker (e.g., `unrelated-domain` / `architecture-veto`). Marker must be within 200 chars of the closing brace.",
        "",
    ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="PF-EMPTY-BODY gate scanner")
    parser.add_argument("step_defs_glob", help="Glob pattern matching step-def files (.ts / .js)")
    parser.add_argument("--threshold", type=float, default=0.10, help="Max allowed empty ratio (default 0.10 = 10%%)")
    parser.add_argument("--out", default=None, help="Output report path; default = stdout summary only")
    parser.add_argument("--allow-marked", action="store_true", default=True, help="Honor @allow-empty-stub markers (default on)")
    args = parser.parse_args()

    files = expand_glob(args.step_defs_glob)
    if not files:
        print(f"warn: no step-def files matched '{args.step_defs_glob}'; vacuous PASS", file=sys.stderr)
        return 0

    all_steps: list[StepDef] = []
    for f in files:
        try:
            all_steps.extend(scan_file(f))
        except OSError as e:
            print(f"error: cannot read {f}: {e}", file=sys.stderr)
            return 2

    total = len(all_steps)
    empty_unmarked = [sd for sd in all_steps if sd.is_empty and not (args.allow_marked and sd.has_allow_marker)]
    empty_allowed = [sd for sd in all_steps if sd.is_empty and args.allow_marked and sd.has_allow_marker]
    ratio = (len(empty_unmarked) / total) if total else 0.0

    summary = (
        f"PF-EMPTY-BODY scan: total={total} empty_counted={len(empty_unmarked)} "
        f"empty_allowed={len(empty_allowed)} ratio={ratio*100:.1f}% threshold={args.threshold*100:.1f}%"
    )
    print(summary, file=sys.stderr)

    if args.out:
        out_path = Path(args.out)
        write_report(out_path, total, empty_unmarked, empty_allowed, args.threshold)
        print(f"report: {out_path}", file=sys.stderr)

    return 1 if ratio > args.threshold else 0


if __name__ == "__main__":
    sys.exit(main())
