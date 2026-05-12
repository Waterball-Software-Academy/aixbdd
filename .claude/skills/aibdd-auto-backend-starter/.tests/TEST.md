# aibdd-auto-backend-starter fixture tests

## Contract

Each scenario uses this structure:

```text
.tests/<scenario>/
  before/
  after/
```

The runner must:

1. Create an isolated sandbox outside `.tests/`.
2. Copy `before/` into the sandbox as the working directory.
3. Invoke `/aibdd-auto-backend-starter` with:
   - `project_dir=<sandbox>`
   - `project_name=AIxBDD Test Backend`
   - `arguments_path=<sandbox>/.aibdd/arguments.yml`
4. Compare the final sandbox filesystem with `after/`.
5. Write any execution reports outside scenario fixture directories.

## Oracle Rules

- `before/` represents the output of `/aibdd-kickoff`.
- `after/` represents the expected output after starter skeleton generation.
- `after/` is an oracle only; the target skill must not read it while executing.
- Scenario fixtures must not contain runner reports, gap reports, issue reports, scenario metadata, or README files.
- The runner must treat missing files, unexpected files, and content differences as failures.

## Scenario: python-e2e-from-kickoff

This scenario verifies that the starter consumes a kickoff-generated `.aibdd/arguments.yml` and produces a Python E2E walking skeleton without mutating `specs/`.

The oracle should encode not only "can boot" skeleton files, but also the
minimum runtime infrastructure needed so future
`/aibdd-red-execute -> /aibdd-green-execute -> /aibdd-refactor-execute`
runs do not spend their first iteration patching predictable starter gaps.
