"""Resolve project arguments from CWD-relative `.aibdd/arguments.yml`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shared.arguments_resolver import (
    DEFAULT_ARGS_REL,
    ResolveError,
    format_cyclic_stderr,
    format_missing_keys_stderr,
    load_arguments_data,
    resolve_placeholders,
)


@dataclass(frozen=True)
class ResolveResult:
    ok: bool
    text: str
    exit_code: int
    stderr: str


def _args_path(cwd: Path | None) -> Path:
    return (cwd or Path.cwd()) / DEFAULT_ARGS_REL


def resolve_text(text: str, *, cwd: Path | None = None) -> ResolveResult:
    args_path = _args_path(cwd)
    try:
        data = load_arguments_data(args_path)
    except ResolveError as exc:
        return ResolveResult(ok=False, text="", exit_code=exc.exit_code, stderr=exc.message)

    resolved, missing, fatal_exit = resolve_placeholders(text, data, args_path=args_path)
    if fatal_exit == 3:
        return ResolveResult(
            ok=False,
            text="",
            exit_code=3,
            stderr=format_cyclic_stderr(args_path),
        )
    if missing:
        return ResolveResult(
            ok=False,
            text="",
            exit_code=2,
            stderr=format_missing_keys_stderr(missing),
        )
    return ResolveResult(ok=True, text=resolved, exit_code=0, stderr="")


def resolve_key(key: str, *, cwd: Path | None = None) -> str | None:
    result = resolve_text(f"{key}=${{{key}}}", cwd=cwd)
    if not result.ok or result.exit_code != 0:
        return None
    line = result.text.strip()
    if "=" not in line:
        return None
    _, val = line.split("=", 1)
    if "<<" in val or val.strip() == "":
        return None
    return val
