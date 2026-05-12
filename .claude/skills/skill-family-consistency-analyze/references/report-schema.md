# Report Schema

## JSON Shape

```json
{
  "status": "ok | warn | fail",
  "skill_roots": ["<path>"],
  "skills": [
    {
      "name": "<skill-name>",
      "path": "<path-to-skill-dir>",
      "skill_md": "<path-to-SKILL.md>"
    }
  ],
  "findings": [
    {
      "severity": "FAIL | WARN | INFO",
      "problem": "<problem-taxonomy-id>",
      "file": "<path>",
      "target": "<optional-target>",
      "message": "<human-readable-message>",
      "evidence": "<quoted-line-or-derived-fact>"
    }
  ],
  "summary": {
    "fail": 0,
    "warn": 0,
    "info": 0
  }
}
```

## Markdown Report Sections

- `# Skill Family Consistency Report`
- `## Summary`
- `## Findings`
- `## Skill Inventory`
- `## Analyzer Coverage`

## Status Rules

- `fail` when at least one `FAIL` finding exists.
- `warn` when no `FAIL` exists and at least one `WARN` exists.
- `ok` when no `FAIL` or `WARN` finding exists.

## Evidence Rules

- Every finding must cite one concrete file.
- Path findings must include the unresolved target path.
- Semantic findings should quote the smallest relevant line or phrase.
- Do not emit duplicate findings with the same `problem`, `file`, and `target`.
