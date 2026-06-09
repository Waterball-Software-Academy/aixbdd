"""Shared sys.path bootstrap for all Behave suites under tests/.

Replaces the per-suite ``Path(__file__).parents[N]`` magic with a marker walk
that locates the ``scripts/`` root (the directory holding both ``lib/`` and
``cli/``), so suites stay correct regardless of how deeply they are nested.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_scripts_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / "lib").is_dir() and (parent / "cli").is_dir():
            return parent
    raise FileNotFoundError("cannot locate scripts root containing lib/ and cli/")


def setup_sys_path() -> None:
    scripts = find_scripts_root()
    for path in (scripts / "lib", scripts):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
