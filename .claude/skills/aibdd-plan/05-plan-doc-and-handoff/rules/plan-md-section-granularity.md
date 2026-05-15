# plan.md／research.md 章節顆粒度

## plan.md 必含章節（順序與標題照寫）

- **`## Discovery Sourcing Summary`**：一句話 pointer 指 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 `${PLAN_SPEC}` 之需求全文；**不重複貼**全文。
- **`## Boundary Delta`**：列 `modules`／`dispatch_overrides`／`provider_edges`／`persistence_ownership`／`components` 之變更摘要，每筆**一行**；細節落 `boundary-map.yml`，本節**不重複貼** YAML。
- **`## External Surface Model`**：每條 consumer→provider edge **一行**（含 contract ref／test double policy／failure mode）。
- **`## Implementation Paths`**：每張 sequence diagram **一行 bullet**，含 happy／alt／err 分類與 `<scenario_slug>`；指向 sequence 檔之 repo-relative path。
- **`## DSL Delta`**：local entries／shared entries **計數** + readability gate 警示 + 任何寫入 `${BOUNDARY_PACKAGE_DSL}`／`${BOUNDARY_SHARED_DSL}` 之 high-level 摘要；entries 全文**落 `dsl.yml`**，本節不貼。
- **`## Impacted Feature Files`**：依 `impacted-feature-files-granularity.md` 之 bullet list。
- **`## Reconciliation Context`**（**僅當** caller 為 `/aibdd-reconcile`）：含 `session_id`／`earliest_planner`／`cascade_chain`／`archive_path` 四欄。
- **`## Quality Gate Verdict`**：step 3 deterministic verdict（PASS／SOFT_FAIL／VETO）＋ step 4 dimension scores + actual script evidence + fix_hints。

## research.md 必含章節

- **`## Decisions`**：本輪做了哪些決策（譬如 boundary 拆法、entity 邊界、DSL key locale、preset 變體選擇）。
- **`## Trade-offs`**：每個 decision 對應之取捨（為何選 A 而非 B）。
- **`## Blocked Reasons`**：合流 `$IMPLEMENTATION_MODEL.blocked_reasons[]`（任一 implementation target 找不到 traceability 來源者於此標）。
- **`## Open Questions`**：留給 `/clarify-loop` 或下次 plan 處理之懸而未決點。

# 反例

- `plan.md` 把 `dsl.yml` 全文貼進來——本檔為計畫敘事與 pointer，**不**做 SSOT shadow copy；下游讀 `dsl.yml` 真相，不讀 plan.md 內 mirror。
- 缺 `## Impacted Feature Files` 章節——`check_impacted_feature_files.py` 必 fail；下游 task 規劃將被迫 fallback。
- `## Quality Gate Verdict` 自寫 `PASS` 但無 dimension scores 或 evidence——gate 報告必須含 actual script verdict evidence；自填等於弱化 gate。
- `research.md` 把 `## Decisions` 寫成 commit log（含日期／PR #／ticket id）——`research.md` 是技術決策紀錄，不是 audit trail；違反註解規則之 as-is 原則。
- 在 plan.md 多開 `## Background`／`## Motivation`／`## Risks` 章節——本節 list 為**封閉集合**，自加章節即偏離 SSOT。

# 禁止自生

- **不得**為「篇幅美觀」自加上述列表以外之章節；只列明文章節。
- **不得**自加未經 deterministic／semantic gate 計算之 verdict——`## Quality Gate Verdict` 必由 step 3／4 計算後寫回，**不得**手填。
- **不得**在 `## Decisions` 自加 raw 未做之決策；只記本輪實際發生之 decision。
