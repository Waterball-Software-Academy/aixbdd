"""Placeholder resolution against `.aibdd/arguments.yml`."""

from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}") from exc

DEFAULT_ARGS_REL = Path(".aibdd/arguments.yml")
PLACEHOLDER = re.compile(r"\$\{([^}]+)\}")
MAX_DEPTH = 50


class ResolveError(Exception):
    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message


def lookup(data: dict, dotted_key: str):
    cur = data
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def load_arguments_data(args_path: Path) -> dict:
    if not args_path.is_file():
        raise ResolveError(
            1,
            f"[resolve-args] arguments.yml not found at {args_path.resolve()}\n",
        )
    try:
        data = yaml.safe_load(args_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ResolveError(
            1,
            f"[resolve-args] failed to parse {args_path}: {exc}\n",
        ) from exc
    if not isinstance(data, dict):
        raise ResolveError(1, f"[resolve-args] arguments.yml must be a mapping: {args_path}\n")
    return data


def resolve_placeholders(
    text: str,
    data: dict,
    *,
    args_path: Path,
) -> tuple[str, list[str], int | None]:
    current = text
    missing: list[str] = []

    for _ in range(MAX_DEPTH):
        missing = []

        def sub(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            val = lookup(data, key)
            if val is None:
                missing.append(key)
                return match.group(0)
            return str(val)

        nxt = PLACEHOLDER.sub(sub, current)
        if nxt == current:
            break
        current = nxt
    else:
        return (
            current,
            missing,
            3,
        )

    return current, missing, None


def format_missing_keys_stderr(missing_keys: list[str]) -> str:
    lines = ["[resolve-args] missing keys in .aibdd/arguments.yml:\n"]
    for key in sorted(set(missing_keys)):
        lines.append(f"  - {key}\n")
    return "".join(lines)


def format_cyclic_stderr(args_path: Path) -> str:
    del args_path
    return (
        f"[resolve-args] placeholder resolution did not converge within "
        f"{MAX_DEPTH} passes — likely a cyclic reference in "
        f"{DEFAULT_ARGS_REL.as_posix()}\n"
    )
