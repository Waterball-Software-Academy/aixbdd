# SKILL.md 骨架樣板（v1 — program-like）

> 純 declarative 樣板。Phase 4 LOAD 此檔取 placeholder，依 user intake 填值。
>
> 規範來源：[`spec.md`](spec.md) §1 Layout / §2 Frontmatter / §3 REFERENCES / §4 SOP / §5 Verb taxonomy / §10 Failure handling in SOP / §23 SSA / §24 Scope / §25 Control flow / §26 Cognitive-type audit

---

## Template

~~~markdown
---
name: <SKILL-NAME>
description: <DESCRIPTION>
metadata:
  user-invocable: <true|false>
  source: <user-scope | project-level | plugin extension>
---

# <SKILL-NAME>

<ONE-LINE-IMPERATIVE-ROLE-SENTENCE>

<!-- VERB-GLOSSARY:BEGIN — auto-rendered from programlike-skill-creator/references/verb-cheatsheet.md by render_verb_glossary.py; do not hand-edit -->
<!-- placeholder — Phase 4 / 6 SOP step TRIGGERs render_verb_glossary.py to fill canonical block here -->
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES

```yaml
references:
  - path: <path>
    purpose: <purpose>
```

(若無 global ref，留 `references: []`；step-local refs 在 SOP body inline cite)

## §2 SOP

### Phase 1 — <IMPERATIVE-NAME>
> produces: `$$<var1>`, `$$<var2>`

1. `$<local>` = <D-VERB> <args>
2. `$$<global>` = <S-VERB> <args> per refs/<ref>.md
3. `$<rp_out>` = THINK per [`reasoning/<context>/00-<rp>.md`](reasoning/<context>/00-<rp>.md), input=`$<local>`
4. <D-VERB> <target> ← `$<payload>`              # 寫入用 ← 箭頭
5. ASSERT <invariant on `$<local>`>
6. BRANCH `$<check>` ? GOTO #2.1 : GOTO #1.6

### Phase 2 — <IMPERATIVE-NAME>
> produces: `$$<var3>`

1. LOOP per `$item` in `$$<collection>` (max <N>)
   1.1 `$<x>` = READ `$item.path`
   1.2 `$<kind>` = CLASSIFY `$<x>`, refs=[a, b, c, unsure]
   1.3 IF `$<kind> == "unsure"`:
       1.3.1 `$<reply>` = ASK "..."
       1.3.2 `$<kind>`  = DECIDE `$<reply>`
   1.4 EDIT `$item.path` ← `$<x>`, kind=`$<kind>`
   END LOOP

...

### Phase N — REPORT
> produces: (none)

1. `$<summary>` = DRAFT report ← `$$<var1>`, `$$<var2>`, `$$<var3>`
2. EMIT `$<summary>` to user

## §3 CROSS-REFERENCES

(optional)

- `/related-skill` — <one-line role>
~~~

---

## 填值規則

- `<SKILL-NAME>`：kebab-case, ≤64 chars（per spec.md §2.1）
- `<DESCRIPTION>`：≤1024 chars 無尖括號（per spec.md §2.2）
- `<ONE-LINE-IMPERATIVE-ROLE-SENTENCE>`：一行 imperative 句，描述 skill 主功能
- `<IMPERATIVE-NAME>`：phase 名稱，imperative form（`LOAD constitution` / `EMIT REPORT`）
- `<D-VERB>`：D-verbs whitelist 之一（per [`verb-whitelist.md`](verb-whitelist.md) §D-verbs）
- `<S-VERB>`：S-verbs whitelist 之一（per `verb-whitelist.md` §S-verbs）
- `$<var>` / `$$<var>`：snake_case 英文 binding 名（per spec.md §23.3）
- `<args>`：動詞參數，可含 inline reference link `[label](path)` 或 `${VAR}` placeholder
- `reasoning/<context>/<rp>.md`：只在 SOP step inline cite；不得新增 `## §1.5 REASONING INDEX`，也不得列進 `## §1 REFERENCES`

## SSA 與 scope 範例

```markdown
### Phase 1 — INTAKE
> produces: `$$name`, `$$desc`, `$$lang`

1. $$name = ASK "skill name?"
2. $$desc = ASK "description?"
3. $$lang = ASK "language?"

### Phase 2 — VALIDATE
> produces: (none — pure check)

1. $ok = MATCH $$name, /^[a-z][a-z0-9-]*$/
2. BRANCH $ok ? GOTO #2.3 : (STOP, EMIT "name 格式錯誤")
3. ASSERT length($$desc) ≤ 1024
```

## Reference cite grammar

step body 內 inline cite reference 用 markdown link：

```markdown
1. $axes = PARSE $cfg, schema=[`refs/axes.md`](references/axes.md)
```

step body 不可用 `R1` / `R2` ID 簡寫 — §1 REFERENCES 不提供 ID；請直接用真實 path。

## Reasoning cite grammar

RP 只在會呼叫該 micro-protocol 的 SOP step inline cite：

```markdown
1. $rp1 = THINK per [`reasoning/default/01-classify-axis.md`](reasoning/default/01-classify-axis.md), input=$rp0
```

`reasoning/` 不列入 `## §1 REFERENCES`；variant selector 由 `SKILL.md` 決定後，只 lazy-load 被選中的 variant path。

## Cognitive-type 自動推導

不需在 step 標 `[D]/[S]/[I]`：

| Step | Verb | Type |
|---|---|---|
| `$cfg = READ ...` | READ | D |
| `$kind = CLASSIFY ...` | CLASSIFY | S |
| `$reply = ASK ...` | ASK | I |

Validator 從 verb 名字直接推 D/S/I，產出 S-density 與 SCRIPT-CANDIDATE block 報告（per spec.md §26）。
