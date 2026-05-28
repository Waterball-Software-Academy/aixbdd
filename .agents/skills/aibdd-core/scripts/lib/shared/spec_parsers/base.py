"""Abstract base for format-specific spec parsers.

Each concrete parser converts a single spec file (OpenAPI YAML / DBML / ...)
into a flat list of `Part` instances. The `Part` is the diff identity used by
later phases (dsl_reader / diff / preset plugin).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from shared.spec_parts import Part


class SpecParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> list[Part]:
        """Read the spec at `path` and emit all parts found in it.

        `path` is also used (verbatim, via `Path.as_posix()`) as the prefix of
        every emitted Part's `target_part_path`. Callers that want a stable
        project-relative form should pass a relative Path (e.g. by chdir'ing
        into the spec root first).
        """
