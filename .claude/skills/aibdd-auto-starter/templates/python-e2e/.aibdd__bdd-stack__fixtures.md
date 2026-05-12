# Fixtures Runtime

## fixture shape

Python E2E fixtures are primarily runtime context objects initialized by Behave `environment.py`.

## data source

- PostgreSQL Testcontainer for acceptance runs.
- SQLAlchemy session exposed as `context.db_session`.
- Natural-key and generated-id memoization exposed as `context.ids`.
- Scenario-local scratch state exposed as `context.memo`.
- Product entrypoints and aggregate setup should share a test-overridable visibility seam instead of using isolated writes that the target operation cannot observe.

## reset policy

- Each scenario starts with a fresh DB session and FastAPI TestClient.
- Each scenario ends with rollback / truncate cleanup controlled by `environment.py`.
- Reset must also clear identifier drift (for example auto-increment / sequence state) when acceptance assertions rely on deterministic IDs.
- Cross-scenario state sharing is forbidden.

## fallback instruction

If a required fixture source is missing, stop before red generation and report the missing fixture/testability gap. Do not replace missing fixture truth with permissive mocks.

## known limitations

- File upload fixtures are not scaffolded by default.
- External resource fixtures must be declared in test strategy or provider contract truth before use.
