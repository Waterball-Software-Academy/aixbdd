# Flow-Oriented Gherkin Rules

**Normative source**: `test-plan-rules.md` in the plugin repo root.

This file is a **pointer** to the authoritative rules — the test-plan-rules.md
document in `spec-kit-aibdd` root is kept in sync with plan.md Chapter 1
decisions (Q20 A chose the four-layer mapping schema; §3.3 rewritten
accordingly).

If you are reading this inside a running AIBDD / spec-kit-aibdd pipeline,
load `test-plan-rules.md` from:

- `${PLUGIN_ROOT}/test-plan-rules.md` — preferred (authoritative within the
  release you have installed)
- Failing that: the copy bundled in this skill's `references/rules/cached/`
  subdirectory (TBD — populated on plugin release by `build-release.sh`)
