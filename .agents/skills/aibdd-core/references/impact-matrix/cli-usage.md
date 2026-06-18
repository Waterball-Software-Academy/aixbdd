# Impact Matrix CLI 使用手冊

impact matrix（`${IMPACT_MATRIX_YML}`）是本輪 plan「哪段需求原文（quote）衍生哪些 spec 檔」的機讀 SSOT。它以 impact 為單位：每個 impact 把一組 `quotes`（需求原文）連到一組 `specs`（衍生的規格檔），由單一 `owner`（plan phase）維護。

`impact_matrix_cli.py` 是維護這份 matrix 的 CLI，提供 `init`、`write`、`add-spec`、`transit-status`、`remove`、`read` 六個 verb。

## 資料模型

```yaml
version: 2
impacts:
  - id: <uuid>                      # 全域唯一，create 時自動產生
    owner: <OWNERS 之一>            # 維護這些 spec 的 plan phase
    quotes: [<需求原文>, ...]       # 至少一句，指回 spec.md 原文；累積歷來驅動該 impact 的原句，非僅最新一輪
    rationale: <一句話>             # 整合全部 quote，說明此 impact 在該 owner 下為何衍生這些 spec
    status: pending | resolved      # resolved 等價於「每個 spec 都 consistent」
    specs:
      - path: <相對 spec 檔路徑>     # 同一 impact 內唯一（跨 impact 可重複）
        status: inconsistent | consistent
```

`OWNERS`：`aibdd-flows-specify`、`aibdd-rules-specify`、`aibdd-spec-by-example`、`aibdd-plan`、`aibdd-api-plan`、`aibdd-data-plan`。

`specs` 可為空：owner 已認領該組 quote、但對應 spec 尚待建立（path 由該 owner 屆時決定）時，impact 為 `pending` 且 `specs: []`，spec 之後由 owner 以 `add-spec` 補上。

## 通用規則

1. 輸出恆為單一 JSON envelope：`{ ok, violations, impacts }`；`ok` 為 true 時 exit 0，否則 exit 1，絕不靜默。
2. `violations` 是唯一的錯誤通道，每筆為 `{ location, type, message }`；`type` 為大寫錯誤類別（`INVALID_VALUE`、`MISSING`、`DUPLICATE`、`NOT_FOUND`、`INCONSISTENT`、`ALREADY_EXISTS`）。arg 級錯誤的 `location` 用 `args.<flag>`，matrix 狀態錯誤用 `impacts[i].<field>`。
3. 每個 mutating verb 落地前都會驗證整份 matrix；違規即丟回 `violations` 並不寫檔（沒有獨立 validate verb）。
4. spec path 一律相對 `${TRUTH_BOUNDARY_ROOT}`。
5. `--matrix` 可省略：依序 fallback 到 `${IMPACT_MATRIX_YML}`、`${PLAN_REPORTS_DIR}/impact-matrix.yml`。整合場景建議一律明示 `--matrix`。

## status 語意

- spec.status：`inconsistent`＝檔尚未落地／不符 quote，待 owner 處理；`consistent`＝檔已符合其 quote。
- impact.status：`pending`＝owner 尚有未結工作；`resolved`＝已明確結案（且每個 spec 都 consistent）。
- 引入不一致會自動降級：把某 spec 設為 `inconsistent`、或 `add-spec` 一個 `inconsistent` spec，會把該 impact 自動轉回 `pending`。
- 達到一致不會自動結案：把所有 spec 設為 `consistent` 不會自動 resolved；resolve 必須明示。
- 移除 spec 不會自動 prune impact；要刪整個 impact 用 impact 級 `remove`。

## 各 verb 應用

init——matrix 不存在時建立空檔；**已存在則拒絕**（回 `ALREADY_EXISTS`，不覆蓋）。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/impact_matrix_cli.py \
  --matrix ${IMPACT_MATRIX_YML} init
```

write——create 或 replace 一個 impact。不帶 `--id` → 新建並自動產生 uuid；帶 `--id` → 以本次提供的欄位整個取代該 impact（要保留的既有 `quotes`／`specs` 必須一併重新提供，未列入者會被覆蓋掉；只想新增單一 spec 改用 `add-spec`）。`--quote` 必填可重複；`--spec` 可重複，亦可省略——省略則建立一個沒有 spec 的 `pending` impact（quote 已歸 owner、spec 待該 owner 之後以 `add-spec` 補上並定 path）。新 spec 一律以 `inconsistent` 落地。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/impact_matrix_cli.py \
  --matrix ${IMPACT_MATRIX_YML} write \
  [--id <uuid>] --owner <owner> --quote "<需求原文>" [--quote ...] \
  --rationale "<一句話>" [--spec <path> ...]
```

add-spec——對既有 impact 加一個新 spec（不重寫整個 impact）。`--status` 必填；加 `inconsistent` 會把 impact 自動降級為 `pending`。

```bash
python3 .claude/skills/aibdd-core/scripts/cli/impact_matrix_cli.py \
  --matrix ${IMPACT_MATRIX_YML} add-spec \
  --id <uuid> --spec <path> --status <inconsistent|consistent>
```

transit-status——帶 `--spec` 設「該 spec」狀態（引入 inconsistent 會自動降級 impact）；不帶 `--spec` 設「impact」狀態（resolve 需所有 spec 皆 consistent，否則回 `INCONSISTENT`）。`--status` 依顆粒度驗證。

```bash
# spec 級
python3 ... transit-status --id <uuid> --spec <path> --status <inconsistent|consistent>
# impact 級（明示結案／重開）
python3 ... transit-status --id <uuid> --status <pending|resolved>
```

remove——帶 `--spec` 移除該 spec（移到最後一個也不刪 impact）；不帶 `--spec` 刪整個 impact。對已不存在者為冪等 no-op。CLI 僅改 matrix 紀錄，不刪磁碟檔。

```bash
python3 ... remove --id <uuid> [--spec <path>]
```

read——讀出 impacts（spec 級 filter 會把不符的 spec 濾掉、再丟掉空 impact）。filter 皆選用、可組合（AND）。

```bash
python3 ... read \
  [--id <uuid>] [--owner <owner> ...] \
  [--impact-status <pending|resolved>] [--spec-status <inconsistent|consistent>] \
  [--spec-path <regex>]
```

`--spec-path` 是對 spec path 做 `re.search` 的 regex（例：`'\.feature$'` 抓所有 feature 檔；`'^packages/01-room/'` 抓某 package）。
