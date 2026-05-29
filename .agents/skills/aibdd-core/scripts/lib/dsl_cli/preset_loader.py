"""Dynamic, path-based loader for boundary preset plugins.

Each preset lives at `<boundaries_root>/<preset_name>/scripts/part_to_dsl.py`
and must expose `generate_templates(parts, context)`. We load it via
`importlib.util.spec_from_file_location` so:

  - we don't pollute sys.path (plugins must be fully self-contained — no
    relative or sibling imports);
  - sys.modules cache is defeated per call by suffixing the module name with a
    uuid hex, which lets tests load multiple variants of the same preset name
    in a row without observing each other's state;
  - syntax errors surface as PluginLoadError with the plugin path, not raw
    SyntaxError;
  - a plugin missing the contract entry function fails as PluginContractError
    at load time, not deep inside orchestrator.
"""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path
from types import ModuleType


class PluginLoadError(Exception):
    """Raised when the plugin source cannot be loaded (syntax errors, etc.)."""


class PluginContractError(Exception):
    """Raised when the loaded plugin module fails the entry-function contract."""


_PLUGIN_FILENAME = "part_to_dsl.py"
_ENTRY_FUNCTION = "generate_templates"


def load_preset_plugin(preset_name: str, boundaries_root: Path) -> ModuleType:
    plugin_path = boundaries_root / preset_name / "scripts" / _PLUGIN_FILENAME
    if not plugin_path.is_file():
        raise PluginLoadError(
            f"preset plugin not found at {plugin_path}; expected `{_PLUGIN_FILENAME}` "
            f"inside `<boundaries_root>/{preset_name}/scripts/`"
        )
    unique_mod_name = f"_dsl_cli_preset_{preset_name}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(unique_mod_name, plugin_path)
    if spec is None or spec.loader is None:
        raise PluginLoadError(f"failed to build module spec for {plugin_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise PluginLoadError(
            f"failed to load plugin at {plugin_path}: {type(exc).__name__}: {exc}"
        ) from exc
    if not hasattr(module, _ENTRY_FUNCTION):
        raise PluginContractError(
            f"plugin at {plugin_path} does not expose `{_ENTRY_FUNCTION}`; "
            f"every part-derived plugin must define `def {_ENTRY_FUNCTION}(parts, context)`."
        )
    return module
