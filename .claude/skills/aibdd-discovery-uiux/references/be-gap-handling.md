# BE Gap Handling — FE-side Supplementation Contract

> 純 declarative — 規範當 sibling backend boundary 的 spec truth 對 FE 用途不足時，本 skill 如何在**只讀 BE truth**的前提下做 FE-side 補位。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 2 與 `reasoning/discovery-uiux/01-be-sourcing.md`。

---

## §1 Cross-boundary read-only invariant

| 條目 | 規約 |
|---|---|
| BE truth role | sibling boundary 的 SSOT，本 skill 一律 read-only |
| 修改 BE truth 的合法路徑 | 必須在 BE boundary 端執行 `/aibdd-discovery` / `/aibdd-plan` 等 owner-side skill |
| 本 skill 對 BE truth 的處置 | （a）記 `CiC(BDY: ...)` / `CiC(GAP: ...)` marker（b）寫進 `${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md`（c）採明示 FE-side assumption 繼續往下 |

> **violation**：任何 SOP / RP / clarify-loop 選項建議使用者「回修 BE feature / activity / contract」即視為違反本 invariant；由 `check_no_be_mutation_leak.py` 偵測。

---

## §2 BE gap 偵測規則

每列描述「BE truth 在 FE 視角下的缺口」與「在 FE 側可選的補位選項」。Seam 0' 提問必定從本表挑題；不在本表內的缺口一律先標 `CiC` 不提問。

| Detect ID | BE 缺口偵測 | FE-side supplement options |
|---|---|---|
| `BG-001` | OpenAPI 缺 `operationId` | （fallback `<method>:<path>`，不出題） |
| `BG-002` | BE feature 全 happy-path（無 `Rule` 含 error / 拒絕 / 邊界 keyword）但 OpenAPI 有 4xx 回應 | (A) FE 主動 cover error state UI；BE 4xx schema 為 SSOT (B) FE 暫不 cover，記 GAP forwarded (C) 視為 ux-only flow |
| `BG-003` | BE activity 缺 DECISION 節點但 OpenAPI 有 4xx 回應 | (A) FE 沿 OpenAPI 4xx 列舉分支 (B) FE 只 cover happy + generic-error (C) FE 暫不 cover |
| `BG-004` | BE Background actor 與 activity header actor 不一致 | (A) FE userflow.actor 採 Background (B) FE userflow.actor 採 activity header；衝突原樣記入 GAP forwarded |
| `BG-005` | BE OpenAPI response 缺 schema（`content.schema` 為空 / `$ref` 斷裂） | (A) FE 假設一份 shape 並寫進 FE local DSL (B) FE 顯示 raw JSON 為佔位 (C) FE 暫不顯示該欄位 |
| `BG-006` | BE shared DSL 缺 actor catalog | (A) 採 activity header 出現過的 actor (B) 採 Background 出現過的 actor (C) 採 raw idea 提到的人設 |
| `BG-007` | BE activity 多 source 同一 op_id 但 verb 不一致（CiC(CON)） | (A) FE 採 activity verb；衝突 forwarded (B) FE 採 feature rule verb；衝突 forwarded |
| `BG-008` | OpenAPI `x-uat-flow` 缺，且 activity / feature tag 皆無對應 | (A) FE 暫定獨立 flow（無 cross-op composition）(B) FE 與其他 op 合併為 composite flow（需配合 intent.page_composition） |

> **invariant**：本表 options 欄位**禁止**出現任何「請修改 / 補完 / 回填 BE」字樣；違反即 rubric `UIUX_NO_BE_MUTATION_LEAK` fail。

---

## §3 Forbidden phrase blacklist

下列字串／詞素出現於 clarify-loop options、GAP report 任何欄位、或 clean artifact，均屬 leak：

```
modify BE
patch BE
fix BE
update BE
請修改 BE
請補完 BE
回修 BE
請改 BE
請回填 BE
請更新 BE
ask BE owner to change
ask BE team to patch
```

> 例外：GAP report 的 `forwarded_to_be_owner` 欄位**可**陳述「BE owner 後續可能會自行補完此 gap」，但不得帶任何 imperative 動詞要求修改；偵測時 `forwarded_to_be_owner` section 內僅允許 indicative 語氣，不允許 imperative。

---

## §4 `discovery-uiux-be-gap.md` 形狀

| Section | 階段 | 必含 |
|---|---|---|
| `## BE Gaps Detected` | 任何階段 | 表格：detect_id / be_pointer / fe_impact / chosen_option_id |
| `## Open BE Supplementation Questions` | 草稿（Seam 0' fire 前） | Seam 0' 待澄清題組，schema 同 [`fe-intent-contract.md §2`](fe-intent-contract.md#2-seam-0-question-categories) |
| `## BE Gaps Resolved (FE-side)` | 終稿（Seam 0' 回答併入後） | 每筆 detect_id + chosen_option_id + FE 採用 assumption verbatim |
| `## BE Gaps Forwarded` | 終稿 | 純 BE-owner 後續可看的 GAP 清單；indicative 語氣；附 BE pointer |

> **invariant**：草稿與終稿同檔覆寫；Phase 5 §5.B `UIUX_BE_GAP_REPORT_PRESENT` rubric 檢驗終稿 `## Open BE Supplementation Questions` 必為空。

---

## §5 下游 RP 消費規約

| 下游 RP | 消費欄位 | 用途 |
|---|---|---|
| `02-operation-classify` | `chosen_option_id` per BE op | classification.reasoning 必須引用 `discovery-uiux-be-gap.md` pointer，而不是把 BE 衝突直接寫進 classification 字句 |
| `03-userflow-derive` | `BG-003` / `BG-004` / `BG-007` resolution | 對 actor / decision / verb 衝突採已選 assumption 推 userflow |
| `04-fe-atomic-rules` | `BG-002` / `BG-005` resolution | 對 error state / response shape 採已選 assumption 推 Rule preset |

---

## §6 不在本檔範疇

- 「如何 fire Seam 0'」 — 屬 SKILL.md Phase 2
- 「BE inventory parse 規約」 — 屬 [`backend-input-contract.md`](backend-input-contract.md)
- 「FE intent sourcing」 — 屬 [`fe-intent-contract.md`](fe-intent-contract.md)
- 「has-ui / no-ui rubric」 — 屬 [`be-to-fe-mapping.md`](be-to-fe-mapping.md)
- 「BE owner 端如何補完缺口」 — **不屬本 skill 任何範疇**；BE owner 重跑 BE 端 `/aibdd-discovery`
