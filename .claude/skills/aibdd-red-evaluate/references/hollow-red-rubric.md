# Hollow Red Rubric

Hollow red means the runner is red but the failing test does not establish a
real user-observable behavior gap.

## PASS Signals

A failing Red scenario is meaningful when the evidence shows:

- the failure is an assertion/value difference over user-observable output
- the failure is an expected exception on a declared user-observable operation
- the step definition reaches the public runtime surface rather than direct
  production internals
- the failure message identifies feature, Scenario, step, and observed vs
  expected behavior
- the assertion would pass if product behavior were implemented correctly

## Veto Signals

Veto the Red run when any target failure shows:

- hard-coded failure such as unconditional `assert False`, `raise AssertionError`,
  or equivalent sentinel failure
- assertion over Worker internal state, DSL mapping internals, StepPlan state, or
  implementation-private objects
- step body that never reaches public runtime behavior
- assertion that only proves fixture construction, mock setup, or test harness
  behavior
- failure caused by missing step, import error, syntax error, fixture error,
  environment error, skip, xfail, or deselection
- failure message too vague for Green to know what product behavior must change

## Judgment Standard

The evaluator judges from the landed step definition body plus runner-native
test report. It must not infer hidden Worker intent from the execute skill SOP.
