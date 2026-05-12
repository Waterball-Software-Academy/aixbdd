# Filename Rename Protocol（Phase 3）

> 純 declarative reference。Phase 3 LOAD 取 rename 流程 + 守門規則。
>
> 來源：原 SKILL.md `## Step 2.5 — Filename Gating + Rename`。

## §1 為什麼要 rename

activity-parser CLI 不認識 BDD 憲法，emit 出來的是英文 kebab-case `<activity-slug>.feature`（`activity-parser/src/activity_parser/cli.py` line 76-90 直接 `target = out / f"{slug}.feature"`）。

本 Phase 在 AI 填 step（Phase 4）前，把每份 skeleton **rename** 成符合 `${BDD_CONSTITUTION_PATH}` §2.4 PF-22 + §5.1 declared axes + §6 Archive 後綴的最終檔名。

## §2 Read declared axes

開啟 `${BDD_CONSTITUTION_PATH}` §5.1，抓三個 axes：

- `filename.convention`（例：`NN-prefix-then-title`）
- `filename.title_language`（例：`zh-Hant`）
- `feature.runtime_path_glob`（例：`apps/electron/tests/**/features/*.feature`，本 Phase 不直接使用，但要確認 §5.1 區塊存在）

## §3 Read archive 後綴

開啟 §6 Archive 目的地表，找 `specs/<feature>/test-plan/*.feature` 對應行，抓出**檔名後綴**（本 plugin 預設 `-acceptance`）。

## §4 對 `${TEST_PLAN_OUT_DIR}/*.feature` 每份檔案逐一改名

### 4.1 抽出當前 stem
例 `open-station`（英文 kebab-case）。

### 4.2 對應 activity 編號
讀 `${ACTIVITIES_DIR}/<same-slug>.activity` 的順序索引（`sorted()` 序），給 `NN`（從 `01` 起，零填充兩位）。

若 activity 自身已有編號前綴（例 `01-open-station.activity`）則沿用之；否則由 sorted index 推。

### 4.3 翻譯 stem 為 `filename.title_language`
依 `<activity-slug>.activity` 的 Activity Title（讀檔內 `[ACTIVITY:title]` 或 `flowchart` 第一行 label，繁中為主）；若 activity 內無顯式 title，由 AI 從 activity 業務語意翻譯（例 `open-station` → `開站指揮站臺`）。

**禁直接音譯**；**禁殘留英文 token**。

### 4.4 套 `filename.convention` schema
例 `NN-prefix-then-title` → `<NN>-<繁中標題>`。

### 4.5 加 §6 後綴
拼 `<NN>-<繁中標題><後綴>.feature`，例 `01-開站指揮站臺-acceptance.feature`。

### 4.6 Rename
用 `mv` 或 `git mv`（若在 git repo 內）把舊檔搬到新檔名；同步 update Phase 2 REPORT 的檔名清單。

## §5 範例 transformation

```
specs/065-tmc-mission-control/test-plan/
  open-station.feature           →  01-開站指揮站臺-acceptance.feature
  worker-runs-goal.feature       →  02-Worker跑Goal-acceptance.feature
  query-state.feature            →  03-查看狀態-acceptance.feature
  view-result.feature            →  04-收尾查看結果-acceptance.feature
```

## §6 守門 last-line check（兩層）

rename 完後對 `${TEST_PLAN_OUT_DIR}/*.feature` 每個檔名做兩層篩檢，任一不通過 → **拒絕進 Phase 4**、以 REPORT 退回 Phase 3 重做（本 skill 不做推測性改名 retry，要求 AI 重讀 §5.1 / §6 後手動再算）：

### 6.1 Anti-pattern token 篩檢（語意層）
對齊 `aibdd-core::feature-granularity.md` §2 anti-pattern token list。命中任一 → 拒絕。

### 6.2 Filename convention 對齊（schema 層）
檔名 schema 違反 §5.1 declared `filename.convention` + `filename.title_language` + §6 後綴任一條 → 拒絕。

例：宣告 `NN-prefix-then-title` + `zh-Hant` + `-acceptance` 但檔名為 `open-station.feature`（無 NN 前綴 + 純英文 + 無後綴）→ 拒絕。

## §7 完成條件

- `${TEST_PLAN_OUT_DIR}/*.feature` 全數通過守門兩層
- 舊英文檔名全數消失
- REPORT 檔名清單已更新為 final 檔名
