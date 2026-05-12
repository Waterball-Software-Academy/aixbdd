# RCA 程序宣告性規則

## 追蹤輸出格式

```
追蹤路徑：
  {program_counter_or_legacy_step}: {步驟名稱} — {輸入} → {輸出}
  ✓ 輸入正確
  ✗ 輸出錯誤：{具體描述}
  根因位置: {program_counter_or_legacy_step}
```

每個追蹤節點都必須引用 skill artifact 的具體位置：

| 欄位 | 要求 |
|---|---|
| `path` | 目標 skill 內的相對路徑，或可定位的絕對路徑 |
| `line_range` | 可定位的行號範圍 |
| `input_state` | 此節點接收到的前置資訊是否正確 |
| `output_state` | 此節點產出的內容是否出現缺陷 |
| `root_cause_marker` | 只標在最早造成缺陷的位置 |

---

## Program-like 偵測契約

目標 skill 視為「尚未 Program-like」只要命中任一條：

| 訊號 | 判定 |
|---|---|
| `missing_sections` | `SKILL.md` 沒有 `## §1 REFERENCES` 或 `## §2 SOP` |
| `missing_glossary` | `SKILL.md` 沒有 canonical `VERB-GLOSSARY` block |
| `legacy_phase_shape` | SOP 不是 `### Phase N — <imperative-name>` 格式 |
| `missing_ssa` | 產出值的 step 沒有 `$var = VERB ...` / `$$var = VERB ...` binding |
| `reasoning_inline_drift` | 複雜語意推理裸寫在 SOP，且沒有 inline cite `reasoning/.../*.md` |
| `reference_flow_drift` | 流程、gate 或分支決策藏在 `references/` / `assets/` / `scripts/` 說明檔 |
| `artifact_lifecycle_drift` | artifact graph 顯示孤兒資產、雙重真值來源、過胖模板、錯層資產或 deprecated 仍被引用 |

RCA 修復後若命中任一訊號，提案或報告必須明示 Program-like migration 狀態。

---

## Artifact lifecycle detection contract

Phase 2 建立 artifact graph 時，至少產出下列結構：

| 結構 | 欄位 | 說明 |
|---|---|---|
| `ArtifactNode` | `path`, `bucket`, `role_guess`, `line_range` | 目標 skill 內每個可讀 artifact；bucket 為 `skill`, `references`, `assets`, `reasoning`, `scripts`, `manifest`, `other` |
| `ArtifactEdge` | `from_path`, `to_path`, `edge_kind`, `evidence` | consumer / producer / reference 關係；`evidence` 必須能回指 markdown link、inline RP cite、manifest entry 或 path literal |
| `LifecycleSignal` | `signal`, `path`, `evidence`, `suggested_fix_kind` | graph 中可被 RCA trace 的資產生命週期問題 |

`LifecycleSignal.signal` 閉集：

| Signal | 判定 | 預設修復方向 |
|---|---|---|
| `orphan_asset` | `assets/`、`references/`、`reasoning/` 或 `scripts/` artifact 無 inbound consumer edge，且沒有 `human-aid` / `deprecated` / manifest 保留理由 | delete / deprecate / add-consumer |
| `duplicate_ssot_candidate` | 兩個以上 artifact 對同一概念使用 `SSOT`、`contract`、`required format`、`template source` 等權威語氣 | choose-ssot-and-link |
| `monolith_template_candidate` | template 含多個 H2 或多個 phase/RP 專屬區塊，且 consumer 只需要其中一段 | split-lazy-load |
| `misbucketed_runtime_flow` | `references/` 或 `assets/` 內含 Step/SOP/gate/branching 程序，或 `reasoning/` 內承載固定輸出模板 | move-to-owner-bucket |
| `deprecated_still_referenced` | 已標 deprecated / legacy 的 artifact 仍被 runtime SOP、RP 或 script 作為 active input 引用 | remove-reference-or-restore-active-owner |

Artifact graph 可以從 `artifact-manifest.yml` 讀取 expected edges；若 manifest 不存在，必須從 `SKILL.md`、RP frontmatter、markdown links、path literal 與 script path usage 推導 best-effort graph。無法判定時標 `unknown`，不得臆測為 safe。

---

## 委派 payload schema

委派 `/programlike-skill-creator` 時，payload 必須包含：

| 欄位 | 內容 |
|---|---|
| `target_skill_path` | 目標 skill 目錄 |
| `rca_root_cause` | RCA 找到的最早出錯位置 |
| `defect_types` | 缺陷類型稱呼 |
| `required_behavior_to_preserve` | name / trigger / user-invocable / downstream contract |
| `artifact_changes_already_made` | 已修改的檔案清單 |
| `migration_goal` | `convert-to-program-like` 或 `repair-existing-program-like` |

---

## 重組偏好

| 優先序 | 偏好 |
|---|---|
| 1 | 保留既有 frontmatter `name`、trigger、外部可見行為與 backward-compatible 入口 |
| 2 | 將流程收斂到 `SKILL.md ## §2 SOP`，每步使用 verb whitelist 與 SSA binding |
| 3 | 將宣告式規則、分類表、案例與整合說明移到 `references/` |
| 4 | 將固定輸出骨架移到 `assets/templates/` |
| 5 | 將複雜語意推理拆成 `reasoning/` RP，並在 `SKILL.md` 以 inline path cite |
| 6 | 使用 `validate_skill_spec.py` 與 reasoning eval scripts 作為驗證依據 |

---

## 與 consistency analyzer 整合

| 情境 | 契約 |
|---|---|
| issue 被 `+A` 後收到覆盤請求 | 觸發 `skill-rca`，分析 skill 層級根因 |
| RCA 已完成 | 回到 consistency analyzer 迴圈，繼續處理下一個 issue |
| 根因不是 skill artifact | 交回 consistency analyzer 或上游流程處理產物修復 |

---

## 核心規則

- **只改 skill，不改產物。** 產物修復由 consistency analyzer 或上游流程負責。
- **追蹤必須具體。** 引用路徑 + 行號。
- **分類不可含糊。** 必須選定至少一個缺陷類型稱呼，不可用「多方面原因」帶過。
- **向後驗證必做。** 見 `defect-types.md`。
