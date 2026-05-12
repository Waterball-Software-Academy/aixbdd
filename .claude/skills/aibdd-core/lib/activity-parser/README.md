# activity-parser

Python CLI + library for Phase 5a of the `spec-kit-aibdd` workflow. Parses
Activity diagrams (the flat event-flow Mermaid dialect defined by
`sf-desktop-app-electron/To-Be-整合/README.md`) into an AST, extracts paths
using coverage Policy 1 (every Action Node at least once), and emits Gherkin
skeleton files suitable for step-fill in Phase 5b.

Part of the `spec-kit-aibdd` extension.

## CLI

```bash
activity-parser parse    <activity-file>.mmd                         # dump AST
activity-parser paths    --specs-root specs/<feature>/               # list Paths per activity (Policy 1)
activity-parser skeleton --specs-root specs/<feature>/ \
                         --policy node-once --out specs/<feature>/test-plan/
```

`activity-parser.sh` / `activity-parser.ps1` thin wrappers live under
`extension/scripts/{bash,powershell}/`.

## Status (MVP)

| Module | Status |
|---|---|
| `cli.py` | Scaffold (click group wired) |
| `parser.py` | Minimal regex-based parser for the flat event-flow dialect |
| `path.py` | Policy 1 (node-once) path extractor |
| `gherkin_skeleton.py` | Path → Gherkin Scenario with comment-only steps |

Policy 2 (branch-exhaustive) is out of MVP; see `docs/sub-proposals/`.
