# promote-dsl

Python CLI backing the `/speckit.aibdd.promote-dsl` command. Scans boundary `dsl.md`
entries across spec packages, emits promotion proposals, and applies approved
promotions by merging entries into `.specify/memory/dsl.md` and moving corresponding step
definitions per the project's BDD Constitution.

Part of the `spec-kit-aibdd` extension.

## CLI

```bash
promote-dsl scan    --specs-root specs/                      # report reuseability stats per boundary dsl.md entry
promote-dsl propose --specs-root specs/ --threshold 20       # emit promotion-proposal.md when gate fires
promote-dsl apply   --proposal <path> --dsl-core .specify/memory/dsl.md
```

`promote-dsl.sh` / `promote-dsl.ps1` thin wrappers live under
`extension/scripts/{bash,powershell}/`.

## Status (MVP)

| Module | Status |
|---|---|
| `cli.py` | Scaffold (click group wired) |
| `scanner.py` | Scaffold (data-class contract, no canonicalize algorithm yet) |
| `proposal.py` | Scaffold (schema emitter, no infra-utility judgement) |
| `applier.py` | Scaffold (move plan builder, no actual file move) |

Algorithmic details are tracked in `docs/sub-proposals/01-dsl-promotion-detail.md`.

## License

MIT — see root `LICENSE`.
