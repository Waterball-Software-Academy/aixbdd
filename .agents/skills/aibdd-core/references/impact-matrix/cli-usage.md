# Impact Matrix CLI 使用手冊

impact matrix（`${IMPACT_MATRIX_YML}`）是本輪 plan「哪些 boundary 規格檔會被 impact、怎麼 impact」的機讀 SSOT，逐檔記錄 path 與 change_type。

`manage_impact_matrix.py` 是維護這份 matrix 的 CLI，提供 `init`、`list`、`upsert`、`delete`、`validate`、`query` 子命令讀寫 entries。

## CLI 通用規則

1. 一檔一 entry: 每次 upsert 只寫一個 path，同一 path 再 upsert 會覆寫既有 entry（改判 change_type 即藉此覆寫），不會新增第二列。
2. 讀 stdout JSON: ok、questions、entries 是是否繼續的唯一依據；validate 的 ok 為 false 時，依 questions 修正後重跑 upsert／validate，不得改寫 YAML 本體繞過 validator。
3. path 一律相對 ${TRUTH_BOUNDARY_ROOT}，不含 repo 外路徑。
4. impact_summary 用現在式一句話說明本輪對該檔的規格增量或對照目的，供 human review 與後續 reconcile，不寫 implementation 步驟。

## change_type Enum 語意

語意基準是「本 plan 對該檔的影響，相對於 plan 開始前的 boundary truth baseline」，不是當下 filesystem 狀態。

- read_only_compare: 檔在 plan 前已存在；本輪只 READ／對照既有規格界定邊界，不改寫該檔內容。impact_summary 寫「對照什麼、用來界定哪個邊界」。
- update: 檔在 plan 前已存在；本輪確定要更新該檔（feature rule、dbml 欄位、dsl 語彙等）。impact_summary 寫「確定要補／改什麼規格增量」。
- add: 該 path 的規格內容由本 plan 新增（檔可能尚不存在）；path 必須是將來要落地的 explicit 路徑。impact_summary 寫「新增什麼規格責任」。
- conditional_update: 是否改動取決於尚未鎖定的 sourcing／變更決策（常見：contracts 是否因 UI／API 外顯而必改）。impact_summary 必須寫清條件與兩側後果；決策一旦在 discovery-sourcing.md 的 Resolved sourcing decisions 拍板，應改判為 update 或 read_only_compare，不要留模糊 conditional。
- remove: 檔在 plan 前已存在；本輪明文淘汰該既存規格檔。impact_summary 寫「淘汰什麼、依據哪段需求原文」。檔案刪除動作不在 CLI，由各 skill 依其明文 DELETE 授權執行。

## 使用情境

init——matrix 尚不存在時建立空檔，已存在則略過。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} init
```

list——讀出全量 entries，常用於收斂前後的 SNAPSHOT 快照。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} list
```

upsert——建立或覆寫一筆 entry；change_type 依 enum 選定，一次只寫一個 path。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} upsert \
  --path <path> --change-type <change_type> --impact-summary "<summary>"
```

delete——移除一筆 entry；僅及 matrix entry，不刪任何規格檔。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} delete --path <path>
```

validate——全部 upsert／delete 完成後執行一次；ok 為 false 則依 questions 回 upsert 修正。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} validate
```

query——依條件篩 entries，stdout JSON 之 entries 即結果集。filter flag 可組合：

- --suffix <ext>: 比對 entry path 後綴，例 .feature。
- --change-type <value>: 比對 change_type，可重複多次（OR 語意）。
- --path-prefix <prefix>: 比對 boundary-root 相對前綴。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
  --matrix ${IMPACT_MATRIX_YML} query \
  [--suffix <ext>] [--change-type <value> ...] [--path-prefix <prefix>]
```
