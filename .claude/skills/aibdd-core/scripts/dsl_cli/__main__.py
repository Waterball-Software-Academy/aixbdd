"""Make `python -m dsl_cli ...` invoke cli.main()."""

from __future__ import annotations

import sys

from dsl_cli.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
