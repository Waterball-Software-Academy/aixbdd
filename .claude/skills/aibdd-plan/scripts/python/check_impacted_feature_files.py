#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import emit, read_args, resolve_arg_path, specs_root, violation


SECTION_RE = re.compile(
    r"^## Impacted Feature Files\s*$\n(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
BULLET_RE = re.compile(r"^- (?P<body>.+?)\s*$")
PATH_RE = re.compile(r"`(?P<path>[^`]+\.feature)`|(?P<plain>[^\s`]+\.feature)")


def repo_relative(path: Path, workspace_root: Path) -> str:
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return path.as_posix()


def extract_section(text: str) -> str | None:
    match = SECTION_RE.search(text)
    if not match:
        return None
    return match.group("body").strip()


def extract_bullet_path(line: str) -> str | None:
    bullet = BULLET_RE.match(line.strip())
    if not bullet:
        return None
    match = PATH_RE.search(bullet.group("body"))
    if not match:
        return None
    return (match.group("path") or match.group("plain") or "").strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_impacted_feature_files.py <arguments.yml>", file=sys.stderr)
        return 2

    args_path = Path(sys.argv[1]).resolve()
    args = read_args(args_path)
    violations: list[dict[str, object]] = []

    plan_md = resolve_arg_path(args_path, args, "PLAN_MD")
    feature_dir = resolve_arg_path(args_path, args, "FEATURE_SPECS_DIR")
    workspace_root = specs_root(args_path, args).parent

    if plan_md is None:
        violations.append(violation("MISSING_PLAN_MD", str(args_path), "missing PLAN_MD"))
        return emit(False, "impacted feature files check", violations)
    if feature_dir is None:
        violations.append(
            violation("MISSING_FEATURE_SPECS_DIR", str(args_path), "missing FEATURE_SPECS_DIR")
        )
        return emit(False, "impacted feature files check", violations)
    if not plan_md.exists():
        violations.append(violation("PLAN_MD_NOT_FOUND", str(plan_md), "plan.md does not exist"))
        return emit(False, "impacted feature files check", violations)

    text = plan_md.read_text(encoding="utf-8")
    section = extract_section(text)
    if section is None:
        violations.append(
            violation(
                "IMPACTED_FEATURE_SECTION_MISSING",
                str(plan_md),
                "plan.md must contain a `## Impacted Feature Files` section",
            )
        )
        return emit(False, "impacted feature files check", violations)

    lines = [line for line in section.splitlines() if line.strip()]
    bullet_lines = [line for line in lines if line.lstrip().startswith("- ")]
    if not bullet_lines:
        violations.append(
            violation(
                "IMPACTED_FEATURE_LIST_EMPTY",
                str(plan_md),
                "`## Impacted Feature Files` must contain at least one bullet path",
            )
        )
        return emit(False, "impacted feature files check", violations)

    seen: set[str] = set()
    feature_dir = feature_dir.resolve()
    for idx, line in enumerate(bullet_lines, start=1):
        rel_path = extract_bullet_path(line)
        if not rel_path:
            violations.append(
                violation(
                    "IMPACTED_FEATURE_LINE_MALFORMED",
                    str(plan_md),
                    f"line {idx} must contain one canonical feature path bullet",
                )
            )
            continue
        if rel_path.startswith("/"):
            violations.append(
                violation(
                    "IMPACTED_FEATURE_NOT_REPO_RELATIVE",
                    str(plan_md),
                    f"{rel_path} must be repo-relative, not absolute",
                )
            )
            continue

        abs_path = (workspace_root / rel_path).resolve()
        if feature_dir not in abs_path.parents:
            violations.append(
                violation(
                    "IMPACTED_FEATURE_OUTSIDE_SCOPE",
                    str(plan_md),
                    f"{rel_path} is not under {repo_relative(feature_dir, workspace_root)}",
                )
            )
        if abs_path.suffix != ".feature":
            violations.append(
                violation(
                    "IMPACTED_FEATURE_WRONG_SUFFIX",
                    str(plan_md),
                    f"{rel_path} must point to a .feature file",
                )
            )
        if not abs_path.exists():
            violations.append(
                violation(
                    "IMPACTED_FEATURE_NOT_FOUND",
                    str(plan_md),
                    f"{rel_path} does not exist on disk",
                )
            )
        if rel_path in seen:
            violations.append(
                violation(
                    "IMPACTED_FEATURE_DUPLICATE",
                    str(plan_md),
                    f"duplicate impacted feature path: {rel_path}",
                )
            )
        seen.add(rel_path)

    return emit(not violations, "impacted feature files check", violations)


if __name__ == "__main__":
    raise SystemExit(main())
