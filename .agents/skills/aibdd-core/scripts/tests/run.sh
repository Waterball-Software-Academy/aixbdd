#!/usr/bin/env sh
# Run every Behave suite under tests/. Each suite is self-contained (own
# behave.ini + environment.py) and shares tests/_support/. Suites mirror lib/:
#   shared/spec_parsers  -> lib/shared/spec_parsers
#   shared/resolve_args  -> lib/shared/arguments_resolver (via cli/resolve_args.py)
#   dsl_cli              -> lib/dsl_cli
set -e
cd "$(dirname "$0")"

for suite in shared/spec_parsers shared/resolve_args dsl_cli; do
  printf '\n=== %s ===\n' "$suite"
  ( cd "$suite" && behave "$@" )
done
