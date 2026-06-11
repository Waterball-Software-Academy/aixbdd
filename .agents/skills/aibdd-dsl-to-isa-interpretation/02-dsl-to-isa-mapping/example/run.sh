#!/usr/bin/env bash
# Self-contained dsl_to_isa demo. Copies pristine input/ -> .work/, runs the
# translator on the copy (it mutates dsl.yml in place), and prints before/after.
# Re-runnable: .work/ is recreated each time, input/ is never touched.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$HERE/../scripts/cli/dsl_to_isa.py"
WORK="$HERE/.work"

rm -rf "$WORK"
cp -R "$HERE/input" "$WORK"

echo "================= INPUT: specs/p1/dsl.yml ================="
cat "$WORK/specs/p1/dsl.yml"

echo ""
echo "================= RUN translator ========================="
CONTRACTS_DIR="$WORK/contracts" \
DATA_DIR="$WORK/data" \
BOUNDARY_SHARED_DSL="$WORK/specs/p1/dsl.yml" \
uv run "$CLI"

echo ""
echo "========== OUTPUT: specs/p1/dsl.yml (ISA-augmented) =========="
cat "$WORK/specs/p1/dsl.yml"
