"""Boundary-agnostic YAML helpers for the DSL corpus.

The DSL flow-map brace fix, round-trip load, and byte-stable serialization are
the same for every boundary — every boundary's ``dsl.yml`` uses the
``{ target: path/{param} }`` shorthand and must round-trip byte-stably so the
translator can detect idempotent rewrites. This lives in ``shared/`` so the
boundary-agnostic orchestrator and each boundary adapter share one
implementation rather than each re-deriving it.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

from ruamel.yaml import YAML

_yaml_rt = YAML()  # round-trip: load + in-place merge + byte-stable dump
_yaml_rt.preserve_quotes = True
_yaml_rt.default_flow_style = False


def fix_flow_map_values(text: str) -> str:
    """Quote unquoted values in single-key flow maps that contain { or }.

    DSL fixture files use the pattern:
        key: { target: some/path/{param}/end }
    which is invalid YAML because { inside a flow-map value starts a nested map.
    This function transforms such lines to:
        key: { target: "some/path/{param}/end" }

    Only affects lines matching `{ word: <unquoted-value-with-braces> }` at EOL.
    Block scalars, already-quoted values, and multi-key flow maps are untouched.
    """
    def fix_line(line: str) -> str:
        m = re.match(
            r'^(.*\{[^:\{]+:\s+)'   # prefix: indent + outer_key: { field:
            r'([^"\'][^\n]*?)'       # value: unquoted, non-greedy
            r'(\s*\}\s*)$',          # suffix: closing } at EOL
            line,
        )
        if m:
            prefix, value, suffix = m.group(1), m.group(2), m.group(3)
            if '{' in value or '}' in value:
                return f'{prefix}"{value}"{suffix}'
        return line

    return '\n'.join(fix_line(ln) for ln in text.split('\n'))


def load_dsl_yaml(path: Path):
    """Round-trip load a DSL/spec YAML file with the flow-map brace fix applied."""
    raw = Path(path).read_text(encoding="utf-8")
    return _yaml_rt.load(fix_flow_map_values(raw))


def serialize_to_bytes(data) -> bytes:
    """Serialize round-trip data to YAML bytes for byte-equality comparison."""
    buf = io.BytesIO()
    _yaml_rt.dump(data, buf)
    return buf.getvalue()
