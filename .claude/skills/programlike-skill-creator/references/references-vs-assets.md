# references/ vs assets/ 抉擇參考表

> 純 declarative 比對表 + 決策樹。Phase 3 step 7 (THINK CLASSIFY) LOAD 此檔，
> per identified resource 判斷該放 `references/`、`reasoning/`、`scripts/`、
> `assets/templates/` 還是 `assets/<其他>/`。

## 核心判準（一句話）

- **`references/`** = agent **讀完內化**的知識（規則 / 規範 / lookup / schema / 規章）。讀進 context window 後變成決策依據，不直接出現在 output。
- **`reasoning/`** = agent **lazy-load 後執行的 RP-local semantic micro-protocol**。它描述 semantic transformation 的取材、分類、推理、reducer contract；不列入 `## §1 REFERENCES`。
- **`scripts/`** = deterministic executable logic（解析、格式轉換、驗證、報表產生）。適合可重複、可機械驗證的 computation。
- **`assets/`** = 被 **output 引用 / 複製 / 填值** 的檔案（template / boilerplate / 圖 / 字型 / sample）。可以不進 context window — agent 直接 copy 或 instantiate。
  - **`assets/templates/`** = 子集合：含 placeholder + inline instruction 的範本，agent 透過填值產生最終 output。

## 決策表

| 資源類型 | 適合 | 理由 / 範例 |
|---|---|---|
| Verb whitelist / lookup table | `references/` | declarative 知識；agent 讀完直接 enforcement |
| 規章 / 規範 / 規則集 | `references/` | 例 `spec.md`、`legal-red-rules.md`、`compliance-checklist.md` |
| Schema definition / IO contract | `references/` | declarative；agent 讀完知道格式約束 |
| 訪談題庫 / Q&A 集 | `references/` | 純 declarative；step 本身不寫題目，只 LOAD § 引用 |
| 抉擇樹 / 比對表（本檔本身；**跨多 step 反覆查**） | `references/` | 決策知識，agent 讀完內化後做判斷 |
| **Quality gate rubric**（rule_id checklist / script→check 表 / pass criteria，由**單一** SOP step 之 TRIGGER / DELEGATE / ASSERT 消費） | **inline 於 SKILL.md SOP**（禁止 `references/contracts/quality.md` 之類） | rubric 與 gate step 共生；抽出後 SKILL.md 失語意，reader 不 LOAD ref 不知 gate 在驗什麼。詳見 spec.md §4.7.6 |
| Skill runtime gate / rubric / contract 的外部 research/eval/plan 草稿 | **禁止引用；必須收進本 skill 或 stable hub** | 產出的 skill 必須 self-contained。`research/**`、`.cursor/plans/**`、`*-outcome-eval.md`、臨時 `eval.md` / `proposal.md` 不能成為 runtime SSOT；詳見 spec.md §4.7.7 |
| RP-local 推理 micro-protocol | `reasoning/` | 例 `reasoning/bdd/01-classify-scenario-intent.md`；含 Material Sourcing / Reasoning SOP / Reducer |
| Polymorphic reasoning slot | `reasoning/<context>/<slot>/POLYMORPHISM.md` | 宣告 selector、variants、shared consumes/produces |
| Parser / renderer / validator | `scripts/` | deterministic computation；例 `eval_reasoning_graph.py` |
| **Template with placeholders + inline instructions** | `assets/templates/` | 例 `feature.template.md` 含 `<!-- INSTRUCT: 寫 Background -->` 區塊註解 |
| Boilerplate file（直接 copy 不填值） | `assets/` | 例 `tsconfig.template.json`、`gitignore.template` |
| Sample document（範例完整 output） | `assets/samples/` | 跑過一次的 example，給 agent 看格式 |
| 圖 / 字型 / binary | `assets/` | non-text 直接 copy |
| 在地化文案 | `assets/i18n/` | 字串資源；不被 agent 解析 |

## Inline-instruction template 模式（assets/templates/ 推薦做法）

當 template 區塊多到 SKILL.md 步驟難以條列每個區塊該寫什麼，用 inline instruction：

~~~markdown
<!-- INSTRUCT: 寫一行 imperative 句說明這支 skill 主功能 -->

# {{SKILL-NAME}}

<ONE-LINE-IMPERATIVE>

## §1 REFERENCES

<!-- INSTRUCT: 列出全局 references；每筆只含 path / purpose -->

```yaml
references:
  - path: <path>
    purpose: <purpose>
```
~~~

優點：

- **Cohesion** — 樣板內每個區塊的填值指引就在區塊旁邊，不必跨檔對照
- **SKILL.md 瘦身** — Phase 4 只需一行 `WRITE per assets/templates/skill-md.template.md instructions`
- **Maintain locality** — 改 template 區塊規則不必同步改 SKILL.md
- **Less drift** — 樣板結構與 instructions 同檔，不會脫鉤

## 何時 prefer assets/templates/ > 純 SKILL.md 步驟

- 區塊數 ≥ 5 且結構固定
- 區塊內格式 verbose（表格 / 多層 list）
- 區塊間有 strong dependencies（前一區塊輸出影響下一區塊）
- 同一支 skill 內樣板 reuse > 1 次（per phase / per artifact）
- 結構規則化、能用 placeholder 表達

不適合 template 的場景：

- 區塊極少（≤ 2）— SKILL.md 直接寫
- 結構動態（依 user input 改變區塊組成）— 純 SKILL.md 步驟反而清楚
- 內容是「規則 / 規範」而非「填值樣板」— 該屬 references/

## 決策樹（Phase 3 step 7 THINK 流程）

```
START per resource (from intake §6 list)
  資源是 binary (圖 / 字型 / pdf)?
    → assets/
  資源是 deterministic computation（parser / renderer / validator）?
    → scripts/
  資源要被 instantiated（填 placeholder 產生 output）?
    → assets/templates/
  資源是被 copy 進 output 但不需填值?
    → assets/<subdir>/
  資源是 RP-local semantic micro-protocol（如何取材、分類、推理、reduce）?
    → reasoning/
  資源是 runtime gate / rubric / contract，但來源在 research / plan / eval 草稿?
    → 先搬進本 skill（inline SOP 或 skill-local references/reasoning/scripts/assets），不得保留外部路徑
  資源是 agent 讀完內化的規則 / lookup / schema / 規章?
    → references/
  其他 / 模糊
    → references/（保守選擇，避免 step flow 落 assets）
END
```

## 反模式

- ❌ 把純規則 / 規範放 `assets/`（agent 不會 LOAD 它就無法 enforce）
- ❌ 把含 placeholder 的樣板放 `references/`（agent 容易誤解為規範文字而不是樣板）
- ❌ 把樣板的 region instructions 寫回 SKILL.md（破壞 cohesion；template 改了 SKILL.md 也要改）
- ❌ 在 `assets/templates/` 內寫 step flow（assets 不是 SOP，step flow 只能在 SKILL.md，per 規章 §4.7）
- ❌ 把 RP 放進 `## §1 REFERENCES`（RP 是 executable-adjacent reasoning artifact，不是 global declarative reference）
- ❌ 把 deterministic parsing / rendering 寫成 RP（可機械重複的 computation 應進 `scripts/`）
- ❌ 在 `SKILL.md` runtime step 寫 `rubric=research/.../eval.md`、`rubric=.cursor/plans/...`、`rubric=/Users/.../research/...`（破壞 self-contained 封裝）

## Dogfood 案例

- ✅ 本 skill 自身的 SKILL.md 骨架樣板已遷至 `assets/templates/skill-md.template.md`（2026-04-29）。歷史錯放於 `references/skill-md-template.md` 是違反本表決策樹的反面案例 —— template 含 `<SKILL-NAME>` / `<DESCRIPTION>` placeholder + Phase 4 LOAD 後填值產生 output，按決策樹屬於 `assets/templates/`。修正後 skill 對自身規範一致。
