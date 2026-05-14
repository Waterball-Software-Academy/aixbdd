#!/usr/bin/env python3
"""Static check: every `route.fulfill(...)` in fixture(s) has a paired `.parse(...)` upstream.

Enforces web-frontend boundary invariant I2 (OpenAPI schema auto-gate). Each mock
dispatch branch in the Playwright fixture MUST Zod-validate its outgoing payload
before calling `route.fulfill`. Missing parses mean schema drift can ship
silently.

Scope (v0 — regex-based):
  - Scans `.ts` / `.tsx` files (default: `features/steps/fixtures.ts`).
  - For each `route.fulfill(` call site, looks UPSTREAM within the enclosing
    `await page.route(...)` dispatch handler body for a `.parse(` call.
  - "Enclosing handler" is approximated by walking up to the nearest line
    matching `await page.route(` or function/arrow boundary; brace counting is
    intentionally simple, not a TypeScript AST.

Out of scope (deferred to v1):
  - Verifying the Zod schema name matches the operationId.
  - Verifying request-body `.parse(req.postDataJSON())` is present for write ops.
  - Verifying response shape matches OpenAPI when present.

Exit codes:
  0 — clean (all `route.fulfill` paired with upstream `.parse`).
  2 — at least one violation; non-zero count reported on stderr.
  3 — usage error or unreadable input.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


FULFILL_RE = re.compile(r"\broute\.fulfill\s*\(")
PARSE_RE = re.compile(r"\.(?:safe)?[Pp]arse\s*\(")  # matches .parse( and .safeParse(
ROUTE_OPEN_RE = re.compile(r"\bpage\.route\s*\(")
# 501 = "unmapped route" pre-dispatch fallback; no operation schema available → exempt
EXEMPT_STATUS_RE = re.compile(r"status\s*:\s*501\b")


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return list of (line_number, reason) for unparsed fulfill sites."""
    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [(0, f"unreadable: {exc}")]

    for idx, line in enumerate(lines):
        if not FULFILL_RE.search(line):
            continue
        # Exempt pre-dispatch 501 fulfills (unmapped route fallback; no op schema).
        lookahead = " ".join(lines[idx : min(idx + 4, len(lines))])
        if EXEMPT_STATUS_RE.search(lookahead):
            continue
        # Walk upstream until we hit the enclosing `page.route(` or the file top.
        upstream_has_parse = False
        for back in range(idx - 1, -1, -1):
            prev = lines[back]
            if PARSE_RE.search(prev):
                upstream_has_parse = True
                break
            if ROUTE_OPEN_RE.search(prev):
                break  # Reached the dispatcher boundary without finding a parse.
        if not upstream_has_parse:
            violations.append(
                (idx + 1, f"`route.fulfill(` at L{idx + 1} has no upstream `.parse(` within its dispatch branch")
            )
    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "usage: check_mock_schema_gate.py <fixture-or-dir> [<more>...]\n"
            "  default scan: features/steps/fixtures.ts",
            file=sys.stderr,
        )
        return 3

    targets: list[Path] = []
    for arg in argv[1:]:
        p = Path(arg)
        if p.is_dir():
            targets.extend(p.rglob("fixtures.ts"))
            targets.extend(p.rglob("fixtures.tsx"))
        elif p.is_file():
            targets.append(p)
        else:
            print(f"check_mock_schema_gate: not found: {arg}", file=sys.stderr)
            return 3

    if not targets:
        print("check_mock_schema_gate: no fixture files to scan", file=sys.stderr)
        return 3

    total = 0
    for path in targets:
        findings = scan_file(path)
        for line_no, reason in findings:
            print(f"{path}:{line_no}: I2 violation — {reason}", file=sys.stderr)
            total += 1

    if total:
        print(f"check_mock_schema_gate: {total} violation(s) across {len(targets)} file(s)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
