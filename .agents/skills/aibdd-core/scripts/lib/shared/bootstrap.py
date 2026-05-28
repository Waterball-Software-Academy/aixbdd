"""Bootstrap ``scripts/lib`` and ``scripts/`` onto ``sys.path``."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_scripts_lib_on_path(*, start: Path | None = None) -> Path:
    anchor = (start or Path(__file__)).resolve()
    for parent in anchor.parents:
        lib_dir = parent / "lib"
        if (lib_dir / "shared" / "project_args.py").is_file():
            lib_str = str(lib_dir)
            if lib_str not in sys.path:
                sys.path.insert(0, lib_str)
            return lib_dir
    raise FileNotFoundError("cannot locate scripts/lib from bootstrap anchor")


def ensure_scripts_root_on_path(*, start: Path | None = None) -> Path:
    lib_dir = ensure_scripts_lib_on_path(start=start)
    scripts_dir = lib_dir.parent
    scripts_str = str(scripts_dir)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    return scripts_dir
