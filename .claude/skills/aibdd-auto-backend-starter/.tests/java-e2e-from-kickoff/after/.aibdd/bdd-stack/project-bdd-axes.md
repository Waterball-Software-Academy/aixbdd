# Project BDD 規約軸（`.aibdd/bdd-stack/project-bdd-axes.md`）

> **錨點角色**：本檔為 `arguments.yml` 中 `.aibdd/bdd-stack/project-bdd-axes.md` 指向的檔案。AIBDD Step 0 **必讀 §5.1** 取得 feature 檔名軸；**不得**對未宣告軸補預設值。
>
> **bdd-stack 即憲法本體**：Cucumber 指令、Spring `@CucumberContextConfiguration` hook、step layout、fixture、feature archive、Red pre-hook 的流程與約束拆在 `.aibdd/bdd-stack/*.md`，並由各 `*_RUNTIME_REF` 與 `.aibdd/bdd-stack/prehandling-before-red-phase.md` 綁定。**本檔不重複**運行手冊或 `arguments.yml` 參數表。

**機械讀取順序（摘要）**

1. `.aibdd/bdd-stack/project-bdd-axes.md` §5.1 → `filename.convention` × `filename.title_language`
2. `.aibdd/bdd-stack/` 下各 runtime 說明檔 → runner／step／fixture／archive 細節
3. `.aibdd/bdd-stack/prehandling-before-red-phase.md` → Red Pre-Hook（java-e2e：`schema-analysis`／flyway-migration）；`/aibdd-red-execute` 進 Red 前必讀

---

## §5 Feature 生命週期軸

### §5.1 Feature filename 軸（NORMATIVE — aibdd Step 0）

| axis | 允許 enum | 本專案值 |
|---|---|---|
| `filename.convention` | `NN-prefix-then-title` \| `kebab-all-lower` \| `snake_case` \| `PascalCase` \| `free-form:<regex>` | `NN-prefix-then-title` |
| `filename.title_language` | `zh-Hant` \| `zh-Hans` \| `en` \| `ja` \| `ko` \| `mixed` \| `custom:<iso-code>` | `zh-Hant` |

**NN-prefix**：兩位數字 + `-` + 與 `filename.title_language` 一致之標題，例：`01-新會員建立首筆訂單.feature`。

**例外**：`HealthCheck.feature`（全名 PascalCase、無數字前綴）僅允許作為 **starter smoke**，路徑鎖定 `src/test/resources/features/HealthCheck.feature`；**不得**作為 Discovery rule-only 檔名範本。

### §5.2 Red Pre-Hook 軸（NORMATIVE）

| axis | 允許 enum | 本專案值 |
|---|---|---|
| `red.pre_hook` | `none` \| `enabled` | `enabled` |
| `red.pre_hook.ref` | 必與 `arguments.yml` 中 `RED_PREHANDLING_HOOK_REF` 解析後路徑一致 | `.aibdd/bdd-stack/prehandling-before-red-phase.md` |
| `red.pre_hook.fill` | `schema-analysis` \| `custom:<label>` \| `none` | `schema-analysis` |

**綁定**：

- `red.pre_hook = enabled` 時，進入 Red（對目標 `.feature` 第一次去 `@ignore` 並跑 acceptance）之前必須讀取 `red.pre_hook.ref` 所指檔案並完成其 Pre-Red gate。
- Pre-hook 失敗 → **不啟動** Red 主流程；RGB loop budget **不**視為已消耗於合法紅燈嘗試。
- Hook 內容為 stack-specific；檔名與 §9 鍵維持 stack-neutral。

---

## §6 Archive / 搬遷（本專案宣告）

| Axis | 允許 enum | 本專案值 |
|---|---|---|
| `feature.archive_mechanism` | `physical-move` \| `build-time-copy` \| `symlink` \| `glob-include` \| `hybrid:<spec>` \| `no-archive` | `no-archive` |

**說明**：規格與測試目錄皆在 repo 內固定路徑；預設**不**對 `${FEATURE_SPECS_DIR}` → `src/test/resources/features/` 做自動搬遷。實際 RED／symlink／鏡像流程見 `bdd-stack/feature-archive.md`。若未來改機制，須先修訂本節與 `arguments.yml`。

---

## §7 Project Overrides（必填區塊；可空）

本專案若需豁免任一條上列規則，於此表列；空表表示無豁免。

| Rule ID | Status | Scope | Reason | Deadline (ISO) | Owner |
|---|---|---|---|---|---|
| _(無)_ | | | | | |
