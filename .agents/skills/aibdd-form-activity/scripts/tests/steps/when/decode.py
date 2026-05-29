"""Step: invoke decoder.parse() against captured activity text.

Catches NotImplementedError from skeleton-state decoder so Then steps can
fail with a clear red-signal message rather than an opaque traceback.
"""

from __future__ import annotations

from behave import when  # type: ignore[import-not-found]

import decoder as decoder_mod  # available via environment.py sys.path manip


@when("執行 decode")
def step_run_decode(context):
    assert context.activity_text is not None, "Given step did not set activity_text"
    try:
        context.parse_result = decoder_mod.parse(context.activity_text)
        context.parse_exception = None
    except NotImplementedError as e:
        # Skeleton state — record so Then steps can fail with clear message
        context.parse_result = None
        context.parse_exception = e
