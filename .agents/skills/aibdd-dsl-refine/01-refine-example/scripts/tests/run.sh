#!/usr/bin/env bash
# expand_isa 展開 lint 的 fixture 級紅綠測試。
# 用法：bash 01-refine-example/scripts/tests/run.sh
set -euo pipefail
cd "$(dirname "$0")"
uv run --with behave --with pyyaml behave "$@"
