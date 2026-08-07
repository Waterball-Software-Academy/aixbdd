#!/usr/bin/env bash
# build_worklist 的 fixture 級紅綠測試。
# 用法：bash scripts/tests/run.sh
set -euo pipefail
cd "$(dirname "$0")"
uv run --with behave --with pyyaml behave "$@"
