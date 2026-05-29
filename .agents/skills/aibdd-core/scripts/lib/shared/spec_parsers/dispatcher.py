"""Route a spec file to its concrete `SpecParser` by filename suffix.

Currently recognized suffixes:
  - `*.api.yml`     → OpenAPISpecParser
  - `*.openapi.yml` → OpenAPISpecParser
  - `*.dbml`        → DBMLSpecParser

Unrecognized suffix raises ValueError. Adding a new format means: add a parser
file under `spec_parsers/`, then add a suffix branch here.
"""

from __future__ import annotations

from pathlib import Path

from shared.spec_parsers.base import SpecParser
from shared.spec_parsers.dbml import DBMLSpecParser
from shared.spec_parsers.openapi import OpenAPISpecParser


def dispatch_spec_parser(path: Path) -> SpecParser:
    name = path.name.lower()
    if name.endswith(".api.yml") or name.endswith(".openapi.yml"):
        return OpenAPISpecParser()
    if name.endswith(".dbml"):
        return DBMLSpecParser()
    raise ValueError(
        f"no spec parser registered for {path.name!r} "
        f"(supported suffixes: .api.yml, .openapi.yml, .dbml)"
    )
