# nn-prefix-then-title

## Rules

- Feature filenames MUST use this shape: `<NN>-<title>.feature`.
- `<NN>` MUST be a two-digit sequence number local to the package feature set.
- `<title>` MUST describe the operation-wise feature in the configured title language.
- The title language MUST be read from `FILENAME_AXES_TITLE_LANGUAGE_REF`.
- The title MAY keep technical English tokens when the language asset permits it.
- Filename ordering MUST be stable across reruns unless the feature set itself changes.
- The filename title MUST not include boundary id as a substitute for a feature title.
- The target directory MUST be the resolved package feature directory (`FEATURE_SPECS_DIR`), not the boundary root.
- Deterministic validation SHOULD reject filenames that do not match `^[0-9]{2}-.+\.feature$`.
- Semantic validation SHOULD reject titles that describe a component, boundary, handler, test type, scenario kind, or implementation layer instead of an operation-wise feature.
- Do not infer title language from path basename when `FILENAME_AXES_TITLE_LANGUAGE_REF` is configured.
- Do not use `README.md` or a directory as a feature filename target.
- Do not put examples, scenario kind, handler names, or test runner names into the filename unless they are part of the user-facing operation title.

### Numbering Guards

- IF this is the first feature in the package:
  - USE prefix `01`.
- IF existing package features already use `NN` prefixes:
  - USE the next unused two-digit number.
- IF a feature is regenerated for the same operation-wise unit:
  - KEEP the existing prefix.
- IF inserting a new feature between existing files would require renumbering stable files:
  - DO NOT renumber automatically.
  - USE the next unused suffix unless the user explicitly approves renumbering.
- IF the feature count exceeds `99`:
  - STOP and ask for a package split or explicit numbering policy.

### Title Language Guards

- IF `FILENAME_AXES_TITLE_LANGUAGE_REF` points to `zh-hant.md`:
  - WRITE the title in Traditional Chinese unless a technical token is clearer in English.
- IF `FILENAME_AXES_TITLE_LANGUAGE_REF` points to `zh-hans.md`:
  - WRITE the title in Simplified Chinese unless a technical token is clearer in English.
- IF `FILENAME_AXES_TITLE_LANGUAGE_REF` points to `en-us.md`:
  - WRITE the title in American English.
- IF the title needs an API field, DSL token, operationId, or domain acronym:
  - KEEP that token in its original spelling.
- IF translation makes the operation title ambiguous:
  - KEEP the precise original token and write the rest in the configured language.

### Target Directory Guards

- IF target path is under `${FEATURE_SPECS_DIR}`:
  - ALLOW feature file creation.
- IF target path is under `${TRUTH_BOUNDARY_ROOT}` directly:
  - STOP because boundary root is not a feature package.
- IF target path is under `${CURRENT_PLAN_PACKAGE}`:
  - STOP because plan package is evidence/report space, not accepted behavior truth.
- IF target path is outside the resolved backend root:
  - STOP because the feature would escape project truth.

## Examples

### Good: Traditional Chinese operation title

```text
01-維護CRM旅程與階段SOP.feature
02-指派學員至旅程階段.feature
03-檢視當前階段SOP.feature
```

Why good:

- Each filename starts with a two-digit package-local order.
- Each title describes one operation-wise feature.
- Technical token `CRM` / `SOP` stays in English because it is a domain token.

### Good: English operation title

```text
01-maintain-crm-journey.feature
02-assign-student-to-journey-stage.feature
03-view-current-stage-sop.feature
```

Why good:

- The title language follows `en-us`.
- The title names the operation, not a component or handler.

### Good: stable numbering on regeneration

Existing file:

```text
02-指派學員至旅程階段.feature
```

Regenerated same operation:

```text
02-指派學員至旅程階段.feature
```

Why good:

- Stable operation-wise unit keeps its existing prefix.
- Rerun does not churn filenames.

### Bad: missing numeric prefix

```text
指派學員至旅程階段.feature
```

Why bad:

- It does not match `<NN>-<title>.feature`.

Better:

```text
02-指派學員至旅程階段.feature
```

### Bad: boundary name as title

```text
01-backend.feature
```

Why bad:

- `backend` is a boundary id, not an operation-wise feature.

Better:

```text
01-建立課程預約.feature
```

### Bad: handler name as title

```text
04-http-operation.feature
```

Why bad:

- `http-operation` is a preset handler, not user-facing behavior.

Better:

```text
04-安排預約並通知管理者排課.feature
```

### Bad: scenario kind in filename

```text
05-安排預約-happy-path.feature
06-安排預約-error-case.feature
```

Why bad:

- Scenario kind belongs inside Examples / Scenarios, not in an operation-wise feature filename.

Better:

```text
05-安排預約並通知管理者排課.feature
```

### Bad: wrong directory

```text
specs/backend/features/01-指派學員至旅程階段.feature
```

Why bad:

- Boundary root `features/` is not the accepted feature location.
- Feature files must be written under the resolved package `FEATURE_SPECS_DIR`.

Better:

```text
specs/backend/packages/01-crm-student-journey/features/02-指派學員至旅程階段.feature
```
