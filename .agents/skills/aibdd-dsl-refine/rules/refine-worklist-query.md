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

一個業務 step（feature example 的一行 GWT）算「已完成定義」需同時：
1. 在該 feature 的 `{feature}.dsl.yml`、或 FP 層 `{FP}/dsl.yml`（跨 feature 共用）有一條 dsl_step，其 `format` 對得上該句（`{name}` 佔位或 `^…$` regex 皆可）；
2. 該 dsl_step 標記為 done（name 上方註解一行 `# done`）；
3. isa_steps 已填、非空。

不滿足即「未完成」：未建立（找不到對應 dsl_step）、或已建立未標 `# done`。

## worklist 暫存區

掃描的產物寫成 worklist 暫存檔，三層查詢都讀它（不各自重掃）。

- 落點：**專案根目錄** `DSL_REFINE_PLAN.yml`（比照 kickoff 的 `KICKOFF_PLAN.md` File-First）。
- 生命週期：**每次 skill 啟動 → 刪除舊檔 + 重新掃描重建**；中途被中斷也一樣刪掉重建，不從舊 worklist 續。
- **只由腳本產出／刷新**：`DSL_REFINE_PLAN.yml` 一律由 `build_worklist.py` 寫，**AI 不得手動修改**。查看＝READ，刷新＝重跑腳本。
- SSOT 分工：dsl.yml 的 `# done` 是**持久真相**；worklist 是**衍生的 session 暫存**，可隨時丟棄重建。
- session 內進度：refine 完成一個 → 只寫 dsl.yml 的 `# done`；要讓後續層級反映進度就**重跑腳本刷新 worklist**（dsl.yml 是 SSOT，重建即反映，無需也不得手改 worklist）。

結構（示意）：
```yaml
# DSL_REFINE_PLAN.yml — session worklist（衍生、非 SSOT）
fps:
  - slug: 01-授信申請與審核
    pending_examples: 35
    features:
      - name: 01-提交新客授信審核單
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
| FP 查詢 | `fps[]` | `pending_examples > 0` |
| Features 查詢 | 選定 FP 的 `features[]` | 含 `status: pending` 的 example |
| Examples 查詢 | 選定 features 的 `examples[]` | `status: pending` |

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
已收斂 → exit 0。主 SOP step 10 須重跑到 exit 0 才得宣告完成（不可只憑自我回報；曾發生 agent 謊報無重複
而實際 16 條未上移）。
