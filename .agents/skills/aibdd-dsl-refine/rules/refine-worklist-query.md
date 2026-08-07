# Refine 範圍查詢（worklist 暫存區）

FP / Features / Examples 三層「找出需要 refine 的對象」是**同一個掃描的不同 roll-up**。
本規則定義「什麼叫未完成」「查詢語意」「worklist 暫存區」；偵測本身由腳本決定性完成。

## 使用流程（執行腳本 → 看結構 → 下一步）

1. **執行 py 腳本** 產出 worklist（先刪舊檔再產；對 specs read-only，只寫 worklist 本身）：
   ```bash
   python3 .claude/skills/aibdd-dsl-refine/scripts/cli/build_worklist.py --packages-dir ${TRUTH_BOUNDARY_PACKAGES_DIR} --out DSL_REFINE_PLAN.yml
   ```
2. **看結構**：READ 產出的 `DSL_REFINE_PLAN.yml`。
3. **下一步**：依當前主流程步驟，讀 worklist 對應層級（FP / features / examples）取選項或進 loop（見下方「三層查詢」）。

## 定義：未完成定義的 dsl step

一個業務 step（feature example 的一行 GWT）算「已完成定義」需：

1. 在該 feature 的 `{feature}.dsl.yml`、或 FP 層 `{FP}/dsl.yml`（跨 feature 共用）有一條 dsl_step，其 `format` 對得上該句（`{name}` 佔位或 `^…$` regex 皆可）；**且**
2. 該定義已「安定」——下列任一成立即可：
   - name 上方註解一行 `# done`（使用者於 batch review 核可的持久真相）；或
   - `isa_steps` 已填、非空。

第 2 點的第二個判準是 SKILL-GAPS #48 的修法：red-execute 階段對 `.dsl.yml` 做機械修補時，新增／拆分出來的定義不會補標 `# done`，只看註解會讓已 green-evaluate PASS 的模組**永久假陽性**。之所以敢放寬，是因為 `.dsl.yml` 本尊已由「草稿態」保證只收核可過的定義（見下節）——推導中的定義住 `.draft`，不在掃描範圍。

不滿足即「未完成」：找不到對應 dsl_step、或找到了但 `isa_steps` 空且未標 `# done`。

## 草稿態：`.dsl.yml.draft` 不算數

- 推導期（主 SOP step 8/9、sub-SOP c/e）產出的 dsl_step 一律寫進 **`{feature}.dsl.yml.draft`／`{FP}/dsl.yml.draft`**；step 10.d 使用者逐項核可後才 MERGE 進本尊並刪草稿。
- `build_worklist.py` 與 `detect_shared_dsl.py` 都只掃 `*.dsl.yml`（glob 不匹配 `*.dsl.yml.draft`），故**草稿一律不算已完成**，中斷後重掃會正確回到 pending。
- 下游 red-execute 的 `archive_specs.py` 同樣以「有同名 `.dsl.yml`」判定該 feature 已 refine；草稿態即是讓「dsl-refine 的中間狀態」變成可安全交接的狀態（SKILL-GAPS #46）。
- `expand_isa.py` 例外：它對每個 `--dsl` 會自動一併載入同名 `.draft`，讓推導期的預覽算得出來。

## worklist 暫存區

掃描的產物寫成 worklist 暫存檔，三層查詢都讀它（不各自重掃）。

- 落點：**專案根目錄** `DSL_REFINE_PLAN.yml`（比照 kickoff 的 `KICKOFF_PLAN.md` File-First）。
- 生命週期：**每次 skill 啟動 → 刪除舊檔 + 重新掃描重建**；中途被中斷也一樣刪掉重建，不從舊 worklist 續。
- **只由腳本產出／刷新**：`DSL_REFINE_PLAN.yml` 一律由 `build_worklist.py` 寫，**AI 不得手動修改**。查看＝READ，刷新＝重跑腳本。
- SSOT 分工：dsl.yml 的 `# done` 是**持久真相**；worklist 是**衍生的 session 暫存**，可隨時丟棄重建。
- session 內進度：refine 完成一個 → 只寫 dsl.yml 的 `# done`；要讓後續層級反映進度就**重跑腳本刷新 worklist**（dsl.yml 是 SSOT，重建即反映，無需也不得手改 worklist）。

### schema（消費端唯一權威的鍵表，勿猜鍵）

| 層級 | 鍵 | 型別 | 語意 |
|------|----|------|------|
| 根 | `fps` | list | 含待處理 example 的 FP；全部完成時為空 list |
| `fps[]` | `slug` | str | FP 目錄名（`NN-<slug>`），即主 SOP 的 `$FP_SLUG` |
| `fps[]` | `pending_examples` | int | 該 FP 底下 pending example 總數 |
| `fps[]` | `features` | list | 含 pending example 的 feature |
| `features[]` | `feature` | str | feature 檔名去副檔名（`01-提交新客授信審核單`），即 `$TARGET_FEATURES` 的值 |
| `features[]` | `pending_examples` | int | 該 feature 底下 pending example 數 |
| `features[]` | `examples` | list | pending example |
| `examples[]` | `title` | str | Example 標題原文 |
| `examples[]` | `status` | str | `pending`（worklist 只收 pending，此鍵供人閱讀） |
| `examples[]` | `undone_steps` | list[str] | 未完成的 GWT 原句 |
| `examples[]` | `reuse` | list | 選填；該 step 在 FP 內別處已有定義 |
| `reuse[]` | `step` / `defined_in` / `dsl_step` | str | 原句／既有定義位置（`dsl.yml`＝FP 層）／既有 dsl_step name |

結構（示意）：
```yaml
# DSL_REFINE_PLAN.yml — session worklist（衍生、非 SSOT）
fps:
  - slug: 01-授信申請與審核
    pending_examples: 35
    features:
      - feature: 01-提交新客授信審核單
        pending_examples: 12
        examples:
          - title: '"王業務" 提交新客授信審核單但沒填客戶名稱，提交沒成功'
            status: pending          # pending | done
            undone_steps:
              - '"王業務" 提交新客授信審核單，但沒填客戶名稱'   # 未完成的 GWT 原句
            reuse:                   # 選填：此 step 在 FP 內已有定義 → c 步引用/hoist，勿重建
              - step: '系統提示 "請填寫客戶名稱"'
                defined_in: features/02-xxx.dsl.yml   # 既有定義位置（dsl.yml＝FP 層）
                dsl_step: 系統提示訊息
```

## 三層查詢（讀 worklist 的某一層）

| 主流程步驟 | 讀 worklist | 列為選項的條件 |
|------------|-------------|----------------|
| FP 查詢 | `fps[]` | `pending_examples > 0`（選項文字取 `slug`） |
| Features 查詢 | 選定 FP 的 `features[]` | `pending_examples > 0`（選項文字取 `feature`） |
| Examples 查詢 | 選定 features 的 `examples[]` | `status: pending`（選項文字取 `title`） |

## 腳本職責

- 掃 `packages/*/features/*.feature` ＋ 各 `{feature}.dsl.yml` ＋ FP 層 `{FP}/dsl.yml`（共用）→ 產出 `DSL_REFINE_PLAN.yml`。
- 偵測純機械：example 每行 GWT 參數化 → `format_matcher` 比對「該 FP 的 `{FP}/dsl.yml` ＋ 該 feature 的 `{feature}.dsl.yml`」裡標 `# done` 的 dsl_step → 比不到即未完成。
- **先找後建標註**：對每個未完成 step，再比對「FP 內所有 dsl_step 定義（不分 done）」；命中**別處**已定義者 → 在該 example 寫 `reuse` 提示（供 c 步引用/hoist，避免重建重複條）。
- read-only 對 specs（只寫 worklist 本身）。
- 合規性檢查、DSL→ISA、變更建議等語意工作不在腳本範圍（屬 AI/其他 rule）。

## FP 級去重 / name 唯一性偵測（loop 收尾，read-only 決定性 gate）

`scripts/cli/detect_shared_dsl.py` 掃一個 FP 內各 `{feature}.dsl.yml`，回報未上移到 `{FP}/dsl.yml` 的
跨 feature 重複：

- **name 跨 ≥2 feature 重複（阻斷級）**：dsl.yml 規則 —— `name` 在同一 FP 解析範圍（祖先鏈）內必須唯一；
  重複會在展開時 `DSL_DEFINITION_DUPLICATE_NAME` 阻斷。**必須**上移。
- **format 跨 ≥2 feature 重複（收斂級）**：應上移收斂、避免 ambiguous match。

只偵測回報、不改檔；hoist／刪重複由 AI（保留 `# done`）執行。**exit code 即 gate**：有重複 → exit 3、
已收斂 → exit 0。主 SOP step 11 須重跑到 exit 0 才得宣告完成（不可只憑自我回報；曾發生 agent 謊報無重複
而實際 16 條未上移）。
