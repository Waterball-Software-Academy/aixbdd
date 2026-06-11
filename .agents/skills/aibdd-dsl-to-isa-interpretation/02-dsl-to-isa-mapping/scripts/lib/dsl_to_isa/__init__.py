"""dsl_to_isa translator package (skill-resident).

On import, wire aibdd-core's shared modules onto sys.path so submodules can
`import shared.spec_parsers.*`. This runs before any submodule's top-level
imports, so the order is always correct.
"""

from ._bootstrap import ensure_core_on_path

ensure_core_on_path()
