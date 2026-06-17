"""Behave hooks for build-mapping BDD suite."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


def before_scenario(context, scenario):
    context.tmp_root = Path(tempfile.mkdtemp(prefix="build_mapping_test_"))
    context.data_dir = context.tmp_root / "data"
    context.data_dir.mkdir(parents=True, exist_ok=True)
    context.last_result = None


def after_scenario(context, scenario):
    tmp_root = getattr(context, "tmp_root", None)
    if tmp_root and tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)
