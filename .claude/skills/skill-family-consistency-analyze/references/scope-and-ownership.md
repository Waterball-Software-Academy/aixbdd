# Scope And Ownership

## Rules

- A skill family is one or more directories that contain `SKILL.md` files and their local `references/`, `assets/`, `scripts/`, `reasoning/`, and template files.
- The analyzer must accept any skill-set path; it must not assume AIBDD naming, `.claude/skills`, or a fixed parent folder.
- A file is in scope when it is under a discovered skill directory and is not ignored by the analyzer.
- A discovered skill owns every file below its directory unless a reference explicitly points to a stable external hub.
- `references/` files define rules, contracts, schemas, or guidance.
- `assets/` files are loaded or copied by skills but are not rule owners unless a reference says so.
- `scripts/` files enforce checks or perform deterministic transforms.
- `reasoning/` files are lazy-loaded reasoning protocols and should not be treated as global references unless cited.
- External stable hubs may be referenced by `hub::name.md` syntax; they are checked as declared links, not as local files.
- Research drafts, proposal files, and temporary plans are not acceptable runtime contract dependencies unless the user explicitly includes them as analysis targets.

## Ownership Signals

- Strong ownership: `SKILL.md` references YAML, explicit "Owned by" line, or direct path under the skill directory.
- Medium ownership: repeated local links from the same skill to the same artifact.
- Weak ownership: filename similarity only.
- Unknown ownership: file is present but no skill, reference, or script links to it.

## Ignore Defaults

- `.git/`, `node_modules/`, `__pycache__/`, `.DS_Store`, binary files, images, and generated caches are ignored.
- `.tests/` is scanned for broken links only when explicitly requested; it is not part of the default problem taxonomy.
