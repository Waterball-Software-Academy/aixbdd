### q2-project-spec-language
- prompt: 專案規格主要用哪一種語言撰寫？
- kind: CON
- options: zh-hant | zh-hans | en-us | ja-jp | ko-kr
- recommendation: zh-hant
- answer.raw: {{Q2_ANSWER}}
- resolved_decision: { key: project_spec_language, value: {{PROJECT_SPEC_LANGUAGE}} }
- status: {{Q2_STATUS}}

<!-- @guideline -->
BCP-47 五選一。此值決定 Gherkin executable step prose 與 feature filename title 採用的 language asset。
DSL key 預設**跟隨規格語言**（`DSL_KEY_LOCALE = prefer_spec_language`）——選了 `ja-jp` 就別把 DSL key 留在 `zh-hant`，兩者要一致。
落地時只改 `arguments.yml` 的 `PROJECT_SPEC_LANGUAGE` 一處（語系單一來源，見 `rules/language-single-source.md`）。
reply token：`Q2: zh-hant | zh-hans | en-us | ja-jp | ko-kr`
