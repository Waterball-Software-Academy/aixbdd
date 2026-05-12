# Verb Whitelist — §5 of 規章 速查表

> 純 declarative lookup table。每個 step 的開頭動詞**必為**以下三個閉集之一。
> Cognitive type **由 verb 名字直接推得** —— 作者不需要在 step 標 `[D]/[S]/[I]`。
> 詳見規章 §5（taxonomy）/ §23（SSA binding）/ §24（scope sigils）/ §25（control flow）。

---

## D-verbs — Deterministic（無 LLM 判斷；future scripting candidate）

| Verb | 意思 | 範例 step |
|---|---|---|
| `READ` | 讀檔 / 取得 raw data | `$cfg = READ .specify/memory/bdd-constitution.md` |
| `WRITE` | 寫檔 / 落地 artifact（內容已備好） | `WRITE ${FEATURE_DIR}/tasks.md ← $rendered` |
| `CREATE` | 建立目錄 / 空檔 | `CREATE $skill_dir/references/` |
| `DELETE` | 刪檔 / rollback | `DELETE $skill_dir` |
| `COMPUTE` | 純 deterministic 運算 / 推導 | `$skill_dir = COMPUTE ${HOME}/.claude/skills/${$$name}` |
| `DERIVE` | 從既有資料按既定規則推算 | `$bucket = DERIVE from refs/lookup.md, key=$resource.kind` |
| `PARSE` | 結構化字串為 in-memory 物件 | `$$axes = PARSE $cfg, schema=axes` |
| `RENDER` | 用 template 填值產 string | `$msg = RENDER refs/templates/commit.md, vars={...}` |
| `ASSERT` | 斷言 invariant（fail-stop） | `ASSERT $axes.todo == []` |
| `MATCH` | regex / pattern 比對 | `$ok = MATCH $name, /^[a-z][a-z0-9-]*$/` |
| `TRIGGER` | 啟動 process / subagent / tool / script（output 可 bind） | `$out = TRIGGER \`pnpm exec biome check\`` |
| `DELEGATE` | 呼叫其他 skill | `DELEGATE /aibdd-red with payload={...}` |
| `MARK` | 紀錄狀態（譬如 TodoWrite） | `MARK Phase 1 completed` |
| `BRANCH` | 顯式控制流分支（吃 `$check` 或 `$kind` binding） | `BRANCH $clean ? GOTO #4.1 : GOTO #2.1` |
| `GOTO` | 跳 phase / step（target 必為 `#phase.step`） | `GOTO #3.2.1` |
| `IF` / `ELSE` / `END IF` | 條件 sub-step（簡單情形；複雜分支用 BRANCH） | `IF $kind == "unsure": ...` |
| `LOOP` / `END LOOP` | 迴圈（必標 budget + exit） | `LOOP per $err in $errs (max 50)` |
| `RETURN` | 提前結束 phase | `RETURN to caller with payload` |
| `STOP` | 終止整個 skill | `STOP — return to /clarify-loop` |
| `EMIT` | 輸出**已生成**的資料（D — 不重新生成） | `EMIT $summary to user` |
| `WAIT` | 等待已 spawn 的 process / 同步點 | `WAIT for $pid` |

---

## S-verbs — Semantic（LLM-only reasoning，不可被 script 取代）

| Verb | 意思 | 範例 step |
|---|---|---|
| `THINK` | 內部判斷 / 一般 reasoning（thinking message — **不印 user**） | `$bucket = THINK per refs/buckets.md → classify $resource` |
| `CLASSIFY` | 多類別分類（fuzzy 輸入 → enum 之一） | `$kind = CLASSIFY $err, refs=[a, b, c, unsure]` |
| `JUDGE` | 二元語意判斷（合格 / 不合格） | `$verdict = JUDGE $artifact against refs/criteria.md` |
| `DECIDE` | 路由 / 取捨（從 user reply 或 context 推結論） | `$kind = DECIDE $reply` |
| `DRAFT` | 生成 prose / 文件 / 訊息 | `$msg = DRAFT commit-message ← $$touched_files, refs/conv.md` |
| `EDIT` | 修改既有檔案內容（LLM 推 patch） | `EDIT $err.file ← $ctx, fix=$err.message` |
| `PARAPHRASE` | 改寫 / 翻譯 prose | `$tw = PARAPHRASE $en, lang=zh-TW` |
| `CRITIQUE` | 對 artifact 提批評 / 建議 | `$notes = CRITIQUE $patch against refs/style.md` |
| `SUMMARIZE` | 抽取重點生摘要 | `$abstract = SUMMARIZE $tickets, len=3-sentences` |
| `EXPLAIN` | 對 user 解釋 why（教學性 prose） | `EXPLAIN $error to user, audience=junior-dev` |

---

## I-verbs — Interactive（yields turn to user）

| Verb | 意思 | 範例 step |
|---|---|---|
| `ASK` | 問 user 一個問題並等回應 | `$reply = ASK "skill name?"` |

I-step 仍須加 `[USER INTERACTION]` tag 以維持向後相容（per §8.3）：

```markdown
3. [USER INTERACTION] $reply = ASK "確認啟動 archive？"
```

---

## Yield discipline（執行鐵律）

executor 跑 SKILL.md 時必須嚴格遵守下列收斂規則。違反任一條都視為 skill 缺陷。

### Yield matrix

| Verb class | Yields turn to user? | 備註 |
|---|---|---|
| D | NO | fire-and-forget；side effect 完繼續走 |
| S | NO | 純內部 reasoning，不印 user |
| I | YES | 唯一允許入口：`ASK` step 配 `[USER INTERACTION]` tag |

### 具體禁則

1. **`EMIT $x to user` 是 fire-and-forget**。EMIT 完立即進下一個 step，不等使用者回應、不等使用者 ack。EMIT 後若沒有下一個 step，是因為 STOP / RETURN 終止，而不是 yield。
2. **`WRITE` / `CREATE` / `DELETE` 都不是 phase 邊界**。WRITE 完繼續走下一個 sub-step；不得在 WRITE 後 emit「要繼續嗎」。
3. **Phase transition 不 yield**：Phase N 走完進 Phase N+1 是無縫接續；sub-step n.k 走完進 n.k+1 也是無縫接續。
4. **禁止 mid-SOP yielding 句型**。下列訊息形式皆禁，不論是否在 EMIT 內：
   - 「要我繼續嗎？」/「需要我繼續嗎？」/「要繼續下一階段嗎？」
   - 「先 review 一下？」/「review 後再繼續？」
   - 「先 checkpoint？」/「先停下來確認？」/「先停一下？」
   - 「Want me to proceed?」/「Should I continue?」/「Pause for review?」
5. **要詢問使用者，唯一合法手段是 `[USER INTERACTION] $reply = ASK ...` 的 ASK step**。skill 作者必須事先在 SOP 裡寫明 ASK 的位置；executor 不得自行新增 ASK。
6. **`STOP` / `RETURN` 是終止，不是 yield**。終止後不再有 next step；executor 等於跳出 skill。

### 為什麼要明文寫死

executor（包括人類與 LLM）面對「WRITE 完成」、「Phase 結束」、「EMIT 給使用者」這三個 natural 邊界，本能會插入「要繼續嗎」這類 checkpoint。skill 作者若沒在 SOP 寫明，executor 會 default 進「禮貌徵詢」模式，導致 truth artifact 落不下來。Yield discipline 把這個 default 反過來：**沒寫 ASK 就不准 yield**。

---

## 變更說明（vs v0）

- 移除 `LOAD` → 拆成 `READ + PARSE`（避免「讀進來 + 內化」混同步驟）
- 移除 `VALIDATE` → 拆成 `ASSERT`（D，invariant 檢查）或 `JUDGE`（S，語意合格性）
- 收緊 `EMIT` → 純輸出（D）；若需先生成再 emit，先 `DRAFT $x` 後 `EMIT $x`
- 移除 `REPORT` → 拆成 `DRAFT $msg`（S） + `EMIT $msg to user`（D）
- 移除 CAPTURE / STAGE / RECORD / FORMULATE / EXPAND 等模糊 verb，用 SSA `$x = TRIGGER ...` 等更精確形式取代
- 新增 `EDIT` / `CLASSIFY` / `JUDGE` / `DECIDE` / `DRAFT` / `CRITIQUE` / `SUMMARIZE` / `EXPLAIN` 為 S-verb
- 新增 `BRANCH` / `MATCH` / `PARSE` / `RENDER` / `DERIVE` 為 D-verb

## 中英規則

- **動詞永遠英文 capital**（避免「讀」/「寫」/「分析」這類中文歧義）
- **prose 部分跟隨 INTAKE §3 chosen language**（`zh-TW` / `en` / `ja` ...）
- **保留英文不在地化**：reference path、`#phase.step` literal、frontmatter 鍵名、verb 本身、`$var` / `$$var` binding

## GOTO 額外規則（per 規章 §4.8）

- target 必為 `#phase.step` literal（`#3.2.1` / `#5.1`）
- 禁止 prose target（`GOTO 上面那一步`）
- backward GOTO 必在外層 LOOP 內（避免 silent infinite loop）

## SSA / scope / branch 額外規則

- 凡是會產出值的 step 必有 `$var = ` 在前（per §23）
- `$var` = phase-local；`$$var` = skill-global，跨 phase 流（per §24）
- 寫入用 `←` 箭頭，讀出用 `=`（per §25.1）
- 多分支用 `BRANCH`，二元用 `BRANCH $check ? then : else`，多 arm 用縮排清單（per §25.2）
