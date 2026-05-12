# dsl.md（boundary / per-spec-package）

> Per-spec-package DSL registry（boundary tier）。由 `/speckit.aibdd.bdd-analyze` Step 3 等流程填入。
> 候選 entry 經 `/speckit.aibdd.promote-dsl` 升到專案級 `.specify/memory/dsl.md`
>（shared tier，檔名同為 `dsl.md`）。

---

## Entries

<!--
  Follow the four-layer mapping schema（見 shared tier `dsl.md` §Schema reminder）。
  Each entry id must be globally unique within this feature package.
-->

- id: <placeholder-entry-id>
  L1:
    given: "<Given 句型，留 {param} 佔位>"
    when:  "<When 句型>"
    then:
      - "<Then 句型 1>"
  L2:
    context: "<user state / boundary context>"
    role:    "<executor role>"
    scope:   "<page | component | boundary | system>"
  L3:
    type: "<mock | direct-call | state-check | state-setup | ui-interaction | ...>"
  L4:
    # Mock:
    #   channel_type / channel_name / (payload_schema OR reference)
    # Non-mock:
    summary: "<one-liner pointer back to feature behaviour>"
