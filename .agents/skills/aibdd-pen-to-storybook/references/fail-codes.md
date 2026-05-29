# Fail codes — caller-return message map

> 純 declarative reference。Phase 7 CLASSIFY 與 DERIVE 從此表查 `failure_kind` → `caller-return message`。
> 任何新加錯誤碼都必須先寫進此表，才能在 Phase N 內 ASSERT / IF 觸發。

## §1 對照表

| failure_kind | trigger condition (Phase) | caller-return message |
|---|---|---|
| `pen-path-invalid` | Phase 1: `$$pen_path` 缺項 / 不存在 / 副檔名非 `.pen` | `pen_path 無效；確認絕對路徑且副檔名為 .pen` |
| `pen-not-parseable` | Phase 2: `file` 結果非 UTF-8 / `jq` 解析失敗 | `.pen 解析失敗（可能是 binary 或舊版 schema）；建議用最新 Pencil 重存後重試` |
| `pen-version-unsupported` | Phase 2: `$$schema_version` 非 `^2\.\d+$` | `不支援的 .pen schema version；本 skill 只接受 v2.x` |
| `pen-no-children` | Phase 2: `$$pen_doc.children` 為空陣列 | `.pen 無 top-level frame；無內容可轉換` |
| `pen-no-tokens` | Phase 3: `Document.variables` 全空或全為 boolean | `.pen 沒有任何 design token；通常代表設計尚未做完，建議回 Pencil 補變數` |
| `screen-id-not-found` | Phase 4: `$$screen_id` 不在 top-level frame 列表 | `screen_id 無效；列出可選清單後請 caller 重指定` |
| `screen-id-missing` | Phase 4: `$$screen_id` 未指定 | _特殊：列 top-level 候選回 caller，等補後重啟 Phase 4，不視為 hard fail_ |
| `no-component-candidates` | Phase 5: `$$component_table.rows` 為空 | `偵測不到任何 component candidate；該 screen 可能無重複結構，建議下游改 page-level scaffold 後手動切` |
| `component-name-collision` | Phase 5: 兩個 candidate 推導出同 PascalCase 名 | `component name 衝突；caller 需在 .pen 改名後重跑` |

## §2 對齊原則

1. 每一行對應 SOP 內一個具名 ASSERT / IF 的失敗模式；新增 ASSERT 必同步加列。
2. `failure_kind` 全為 kebab-case；message 為單行白話文，禁夾 stack trace（stderr 由 caller 自取）。
3. caller 收到 message 後決定上游修復推理包 / 指引 user 修 `.pen` / 視為 hard error；本 skill 在 message 內**不**提供修復步驟（修復 SOP 屬 caller 的事，避免重複 source of truth）。
4. `screen-id-missing` 為非 hard-fail 例外：列候選給 caller、等補後重啟 Phase 4。
5. 本 skill 為 read-only adapter，**不寫任何檔**；因此沒有 `write-io-failed` / `target-dir-conflict` / `npm-install-failed` / `tsc-error` / `storybook-build-failed` / `return-unreachable` 等寫檔 / build / sidecar 報告相關 fail kind（這些已在從 scaffold 模式移除時一併砍除）。

## §3 Phase × 主要 fail kind

| Phase | 主要 fail kind |
|---|---|
| 1 ASSERT intake | `pen-path-invalid` |
| 2 VERIFY .pen | `pen-not-parseable` / `pen-version-unsupported` / `pen-no-children` |
| 3 EXTRACT tokens | `pen-no-tokens` |
| 4 MAP screen | `screen-id-not-found` / `screen-id-missing` |
| 5 DETECT components | `no-component-candidates` / `component-name-collision` |
| 6 REPORT adapter | _no fail kind — pure RETURN_ |
| 7 HANDLE dispatch | _internal CLASSIFY only_ |
