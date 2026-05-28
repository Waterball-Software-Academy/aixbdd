# Green Oscillation Detection

Oscillation means Green keeps trading one first failure for another instead of
monotonically moving the same target feature-file set toward green.

## Stable Signature

Each runner iteration records the first failure as:

- feature file
- scenario name
- failing step keyword and prose, when the runner reports them
- normalized failure type
- normalized message fingerprint

Full stack traces are not part of the signature because line numbers and frames
can change without changing the behavioral failure.

## Strict Two-Signature Ping-Pong

The first version detects strict two-signature alternation:

- A then B then A then B is one repeated pair pattern.
- A complete round trip is counted after both directions are observed.
- Default threshold is `GREEN_OSCILLATION_THRESHOLD = 3`.
- A runtime or eval policy may lower or replace the threshold, but the skill does
  not silently raise it.

## Stop Payload

When the threshold is reached, Green stops with `oscillation_detected` and emits:

- threshold and observed round-trip count
- the two signatures involved
- ordered loop history
- product files modified in the recent loop
- summarized diff fingerprints for the recent loop
- the last runner-native behavior report

Green must not continue the same product-code strategy after this STOP.
