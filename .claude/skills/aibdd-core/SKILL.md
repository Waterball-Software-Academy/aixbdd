---
name: aibdd-core
description: 跨 skill 共用 reference hub。包含 atomic rule 定義、report contract、authentication binding、spec package paths、physical-first principle、artifact partitioning、feature granularity 等共用 reference。LOAD-only — 由其他 sibling skill 透過 `aibdd-core::FILENAME.md` 載入；禁止重抄內容至自身 references。SKIP when caller 試圖直接 invoke 本 skill 而非 LOAD reference 檔。
metadata:
  user-invocable: false
  skill-type: reference-hub
  source: project-level dogfooding
---

# aibdd-core

跨 skill 共用 reference hub — LOAD-only，不執行任何流程。Sibling skill 透過 `aibdd-core::FILENAME.md` 形式 LOAD references；禁止複製本檔內容至自身 references/。

## §1 REFERENCES（Hub Exports）

下表是 sibling skill 透過 `aibdd-core::FILENAME.md` 可載入的 reference manifest。新增 / 移動 reference 必同步更新此表（YAML 區塊供 analyzer 機械審計，table 供人類閱讀）。

```yaml
references:
  - path: references/atomic-rule-definition.md
    purpose: Atomic rule semantic 判定
  - path: references/report-contract.md
    purpose: Planner 匯報格式 + user-facing message style
  - path: references/authentication-binding.md
    purpose: Actor key 為 authentication prerequisite 的跨 skill 慣例
  - path: references/spec-package-paths.md
    purpose: spec 路徑慣例 SSOT（boundary-aware）
  - path: references/physical-first-principle.md
    purpose: new packing DSL physical mapping 規則
  - path: references/artifact-partitioning.md
    purpose: Legacy — 舊 Speckit artifact 分工矩陣
  - path: references/feature-granularity.md
    purpose: feature 粒度 anti-pattern token + 命名規範
  - path: references/diagram-file-naming.md
    purpose: Mermaid 產物 compound extension 規範
  - path: references/boundary-profile-contract.md
    purpose: Boundary type profile 最小契約
  - path: references/dsl-output-contract/red-usable-l1-l4.md
    purpose: DSL L1-L4 必填欄位契約
  - path: references/filename-axes-convention/nn-prefix-then-title.md
    purpose: NN-title 命名軸 SSOT
  - path: references/gherkin-rule-body-prefix-policy/four-rules-prefix.md
    purpose: Rule body 四種 prefix 寫作規範
  - path: references/preset-contract/web-backend.md
    purpose: web-backend boundary preset 規章
  - path: references/i18n/en-us.md
    purpose: en-US locale prose 慣例
  - path: references/i18n/ja-jp.md
    purpose: ja-JP locale prose 慣例
  - path: references/i18n/ko-kr.md
    purpose: ko-KR locale prose 慣例
  - path: references/i18n/zh-hans.md
    purpose: zh-Hans locale prose 慣例
  - path: references/i18n/zh-hant.md
    purpose: zh-Hant locale prose 慣例
```

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/atomic-rule-definition.md` | global | Atomic rule semantic 判定（第一性原則；must / should / shall 不得藏 comment）|
| R2 | `references/report-contract.md` | global | Planner 匯報格式、user-facing message style、scope 欄位慣例 |
| R3 | `references/authentication-binding.md` | global | Actor key 作為 authentication prerequisite 的跨 skill 共用慣例 |
| R4 | `references/spec-package-paths.md` | global | spec 路徑慣例 SSOT — kickoff boundary-aware（`arguments.yml` + `boundary.yml` 解析） |
| R5 | `references/physical-first-principle.md` | global | new packing DSL physical mapping 規則 |
| R6 | `references/artifact-partitioning.md` | legacy | 舊 Speckit artifact 分工矩陣；僅供仍未遷移的 legacy skill 讀取 |
| R7 | `references/feature-granularity.md` | global | feature 粒度 anti-pattern token 篩檢 + 命名規範（`/aibdd-form-feature-spec` 寫檔守門用）|
| R8 | `references/diagram-file-naming.md` | global | Mermaid 產物 compound extension：`*.class.mmd` / `*.sequence.mmd`（IDE routing） |
| R9 | `references/boundary-profile-contract.md` | global | Boundary type profile 最小契約（type → operation contract / state / DSL handler 對應）|
| R10 | `references/dsl-output-contract/red-usable-l1-l4.md` | global | DSL L1-L4 必填欄位契約：`/aibdd-red` 可機械吃下的最低 schema |
| R11 | `references/filename-axes-convention/nn-prefix-then-title.md` | global | spec package 與 feature 檔的 `NN-title` 命名軸 SSOT |
| R12 | `references/gherkin-rule-body-prefix-policy/four-rules-prefix.md` | global | Rule body 四種 prefix（must/should/shall/may）寫作規範 |
| R13 | `references/preset-contract/web-backend.md` | global | `web-backend` boundary preset 規章（handler-routing / handlers / variants 對應） |
| R14 | `references/i18n/en-us.md` | global | en-US locale prose 慣例 |
| R15 | `references/i18n/ja-jp.md` | global | ja-JP locale prose 慣例 |
| R16 | `references/i18n/ko-kr.md` | global | ko-KR locale prose 慣例 |
| R17 | `references/i18n/zh-hans.md` | global | zh-Hans locale prose 慣例 |
| R18 | `references/i18n/zh-hant.md` | global | zh-Hant locale prose 慣例 |

## §2 ASSETS（Hub Exports）

| Path | Purpose |
|---|---|
| `assets/boundaries/` | Boundary preset SSOT — `<preset.name>/{handler-routing.yml, handlers/, variants/, shared-dsl-template.yml}`；`/aibdd-red` 透過此處解析 `L4.preset.{name, handler, variant}` |
| `assets/boundaries/schemas/` | Boundary asset schema（如 `handler-routing.schema.yml`） |

## §4 CROSS-REFERENCES

- `/aibdd-discovery`、`/aibdd-form-activity`、`/aibdd-form-feature-spec`、`/aibdd-plan`、legacy `/speckit.aibdd.bdd-analyze`、legacy `/speckit.aibdd.test-plan`、`/clarify-loop` — sibling skills LOAD 本 hub references
