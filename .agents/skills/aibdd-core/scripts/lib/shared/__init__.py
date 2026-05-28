"""Cross-skill shared libraries for aibdd-core scripts."""

from shared.arguments_resolver import (
    DEFAULT_ARGS_REL,
    MAX_DEPTH,
    ResolveError,
    load_arguments_data,
    resolve_placeholders,
)
from shared.project_args import ResolveResult, resolve_key, resolve_text
from shared.repo_root import repo_root_from_module

__all__ = [
    "DEFAULT_ARGS_REL",
    "MAX_DEPTH",
    "ResolveError",
    "ResolveResult",
    "load_arguments_data",
    "repo_root_from_module",
    "resolve_key",
    "resolve_placeholders",
    "resolve_text",
]
