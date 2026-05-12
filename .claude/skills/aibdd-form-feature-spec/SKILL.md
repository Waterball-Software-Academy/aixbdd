---
name: aibdd-form-feature-spec
description: 從推理包翻譯為 Gherkin .feature。負責 Gherkin 規章 + 歸檔。不做 step pattern / Spec-by-Example 句型分析（該職責屬 form-bdd-analysis）。`target_path` 必須由 caller（例如 `/aibdd-discovery`）依 kickoff 展開後的 `${FEATURE_SPECS_DIR}` 指定；本 skill 不推測路徑。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-form-feature-spec

Formulation skill — 把 Planner 推理包翻譯成 Gherkin `.feature` 檔；強制兩層檔名守門（語意 + schema）。

## §1 REFERENCES

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `aibdd-core::spec-package-paths.md` | global | kickoff boundary-aware path SSOT |
| R2 | `aibdd-core::feature-granularity.md` | Phase 2 | feature 粒度 anti-pattern token 守門 |
| R3 | `aibdd-core::authentication-binding.md` | Phase 3 | actor key 認證豁免規則 |
| R4 | `aibdd-core::report-contract.md` | Phase 5 | DELEGATE REPORT 規範 |
| R5 | `references/role-and-contract.md` | Phase 1 | 推理包入口 schema + 角色定位 |
| R6 | `references/format-reference.md` | Phase 3 | Gherkin 標準語法 + 決策樹 |
| R7 | `references/dsl-best-practice.md` | Phase 3 | Rule 命名 / Example / Background 規則 |
| R8 | `references/patterns/rule-only-format.md` | Phase 3 | rule-only 模式格式（無 Background、4-rules pattern）|
| R9 | `references/patterns/bdd-examples.md` | Phase 3 | Example 表撰寫最佳實踐 |

## §2 SOP

### Phase 1 — VALIDATE intake

1. READ payload from caller per [`references/role-and-contract.md`](references/role-and-contract.md) §2
2. ASSERT payload 完整 + `target_path` 已指定 + `mode ∈ {rule-only, example-fill}`
   2.1 IF 缺項:
       2.1.1 RETURN 「推理包不完整」to caller
       2.1.2 STOP
3. ASSERT caller payload for one `target_path` 對應單一 operation surface（caller 已完成 operation partition；本 skill 不負責替 caller 做 semantic split）
   3.1 IF caller payload 明示或可直接看出同一 `target_path` 聚合多個可獨立命名／獨立驗收／獨立觸發的 operation:
       3.1.1 RETURN 「MULTI_OPERATION_AGGREGATE；請 caller 先 split operation 再 formulation」to caller
       3.1.2 STOP

### Phase 2 — GUARD filename (兩層守門)

1. EXTRACT stem from `target_path`（去 `.feature` 副檔名）
2. VALIDATE stem against `aibdd-core::feature-granularity.md` §2 anti-pattern token list
   2.1 IF token hit:
       2.1.1 STOP
       2.1.2 REPORT to caller "ANTI_PATTERN_TOKEN; rerun Discovery Operation Partition or 重命名"
3. VALIDATE stem schema against `${BDD_CONSTITUTION_PATH}` §5.1 declared `filename.convention` × `filename.title_language`
   3.1 IF schema 違反:
       3.1.1 STOP
       3.1.2 REPORT to caller "FILENAME_CONVENTION_VIOLATION; check Discovery Step 0/1 axes binding"

### Phase 3 — FORMULATE Gherkin

1. READ [`references/format-reference.md`](references/format-reference.md) §Gherkin 標準語法
2. IF mode == "rule-only":
   2.1 EXPAND Feature header + Rule 層 per [`references/patterns/rule-only-format.md`](references/patterns/rule-only-format.md)
   2.2 PRESERVE `@ignore` tag
   2.3 SKIP Background + Examples（rule-only 不寫）
   2.4 ASSERT Feature 描述段首句述及 operation trigger（UI click / HTTP call / worker event / domain-service method / utilities function）
   2.5 ASSERT rule-only mode 的整個 Feature 仍只服務於 caller 已切好的單一 operation surface；若需要同時描述多個 command / event / action type，應由 caller 先拆成多個 `.feature`
3. ELSE IF mode == "example-fill":
   3.1 FORMULATE Scenario / Scenario Outline + Examples per [`references/patterns/bdd-examples.md`](references/patterns/bdd-examples.md)
   3.2 REMOVE `@ignore` tag
   3.3 ASSERT 所有 Example 繫於同一 operation
4. APPLY Rule 命名 per [`references/dsl-best-practice.md`](references/dsl-best-practice.md) §2
5. APPLY authentication 豁免 per `aibdd-core::authentication-binding.md`
6. DO NOT persist analyzer-only metadata inline 至 `.feature`（包含 reducer 註解、merge trace、CiC / setup notes）；`.feature` 僅保留業務可讀且可執行的 Gherkin 本體與必要 tag（如 `@ignore`）

### Phase 4 — WRITE artifact

1. WRITE Gherkin to `${target_path}`
2. ASSERT 寫檔成功
   2.1 IF IO 失敗:
       2.1.1 RETURN to caller with IO error
       2.1.2 STOP

### Phase 5 — REPORT to caller

1. EMIT REPORT to caller（白話文 1-3 句，**非 user-facing**，per `aibdd-core::report-contract.md` §REPORT）：
   "Form Feature Spec 完成。產出 N 個 .feature 檔案。{若有便條紙則加「尚有 N 張便條紙待釐清」；無則省略}"

## §3 FAILURE & FALLBACK

### Phase 1 fail handling
- IF payload 完全空: STOP + REPORT "empty payload — caller misuse"
- IF `target_path` 未指定: RETURN 「target_path 缺項」to caller + STOP
- IF mode 非 enum: RETURN 「mode 不支援」+ STOP
- IF caller payload 聚合多個 operation 到同一 `target_path`: RETURN 「MULTI_OPERATION_AGGREGATE」to caller + STOP

### Phase 2 fail handling
- IF anti-pattern token 命中: STOP + REPORT 退回 caller (caller 重命名後重 DELEGATE)
- IF schema 違反: STOP + REPORT 退回 caller (caller 重跑 Discovery Step 0/1)
- 本 skill **不**對檔名做推測性修正

### Phase 3 fail handling
- IF rule-only 模式但 Feature 描述段缺 operation trigger: REPORT specific section, GOTO #3.2.4
- IF rule-only 模式需要同時承載多個可獨立驗收的 operation: STOP + REPORT「caller must split operation before formulation」
- IF example-fill 模式但 Examples 跨多 operation: STOP + REPORT「examples must bind to single operation」

### Phase 4 fail handling
- IF WRITE IO 失敗: RETURN IO error + STOP
- IF `target_path` 已存在且 mode != overwrite: RETURN 「path 衝突」+ STOP

### Phase 5 fail handling
- IF EMIT 失敗（caller 已斷線）: WRITE summary to `${target_path}.report` + STOP

## §4 CROSS-REFERENCES

- 由 `/aibdd-discovery` Phase 4 DELEGATE（rule-only 模式）
- 由 `/speckit.aibdd.bdd-analyze` DELEGATE（example-fill 模式）
- Plan DSL L1：example-fill 的 Gherkin step 句型由 caller（`/speckit.aibdd.bdd-analyze`）依 `BOUNDARY_PACKAGE_DSL` / `BOUNDARY_SHARED_DSL` 提供；本 skill 不鏡像句型目錄、不維護獨立 preset markdown。
