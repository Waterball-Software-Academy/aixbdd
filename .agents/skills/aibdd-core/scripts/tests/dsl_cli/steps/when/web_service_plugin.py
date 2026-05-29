"""When step that loads the real web-service plugin and calls generate_templates.

Per Principle 4 (and confirmed by the plan) L3 tests run the full pipeline:
real spec_parser → real plugin (loaded via preset_loader exactly the way
production does). The boundaries root is the actual on-disk
`assets/boundaries/` directory, not a tempdir fixture.
"""

from __future__ import annotations

from pathlib import Path

from behave import when

from dsl_cli.preset_loader import load_preset_plugin

# This file lives at:
#   .claude/skills/aibdd-core/scripts/tests/dsl_cli/steps/when/web_service_plugin.py
# parents indexing:
#   [0] when/  [1] steps/  [2] dsl_cli/  [3] tests/  [4] scripts/  [5] aibdd-core/
# The on-disk boundaries root is .claude/skills/aibdd-core/assets/boundaries/
_BOUNDARIES_ROOT = Path(__file__).resolve().parents[5] / "assets" / "boundaries"


@when("the web-service plugin generates templates from the parsed parts")
def step_generate_templates_via_real_plugin(context):
    plugin = load_preset_plugin("web-service", _BOUNDARIES_ROOT)
    context.templates = plugin.generate_templates(context.parts, {})
