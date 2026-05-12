"""Shared guards for step modules — not a step file itself.

No `@given/@when/@then` decorators here.
"""


def require_result(context):
    """Fail-stop guard for Then steps that depend on a captured ParseResult."""
    if context.parse_exception is not None:
        raise AssertionError(
            f"decoder skeleton — parse() raised NotImplementedError: {context.parse_exception}. "
            "Implement decoder.parse() to drive this scenario green."
        )
    assert context.parse_result is not None, "parse_result missing"
