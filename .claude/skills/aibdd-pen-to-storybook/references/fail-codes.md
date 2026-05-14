# Fail codes — caller-return message map

> 純 declarative reference。Phase 7 CLASSIFY 與 DERIVE 從此表查 `failure_kind` → `caller-return message`。
> 任何新加錯誤碼都必須先寫進此表，才能在 Phase N 內 ASSERT / IF 觸發。

## §1 對照表

| failure_kind | trigger condition (Phase) | caller-return message |
|---|---|---|
| `pen-path-invalid` | Phase 1: `$$pen_path` 缺項 / 不存在 / 副檔名非 `.pen` | `pen_path 無效；確認絕對路徑且副檔名為 .pen` |
| `pen-not-parseable` | Phase 2: `file` 結果非 UTF-8 / `pen_query.py` 解析失敗（exit 1） | `.pen 解析失敗（可能是 binary 或舊版 schema）；建議用最新 Pencil 重存後重試` |
| `pen-version-unsupported` | Phase 2: `$$schema_version` 非 `^2\.\d+$` | `不支援的 .pen schema version；本 skill 只接受 v2.x` |
| `pen-no-children` | Phase 2: `$$pen_doc.children` 為空陣列 | `.pen 無 top-level frame；無內容可轉換` |
| `pen-no-tokens` | Phase 3: `Document.variables` 全空或全為 boolean | `.pen 沒有任何 design token；通常代表設計尚未做完，建議回 Pencil 補變數` |
| `screen-id-not-found` | Phase 4: `$$screen_id` 不在 top-level frame 列表 | `screen_id 無效；列出可選清單後請 caller 重指定` |
| `screen-id-missing` | Phase 4: `$$screen_id` 未指定 | _特殊：列 top-level 候選回 caller，等補後重啟 Phase 4，不視為 hard fail_ |
| `no-component-candidates` | Phase 5: `$$component_table.rows` 為空 | `偵測不到任何 component candidate；該 screen 可能無重複結構，建議下游改 page-level scaffold 後手動切` |
| `component-name-collision` | Phase 5: 兩個 candidate 推導出同 PascalCase 名 | `component name 衝突；caller 需在 .pen 改名後重跑` |
| `accessible-name-prop-missing` | Phase 6: render plan 找不到對應 accessible-name 來源 prop | `偵測到的 component 缺可見文字 prop；boundary I4 binding anchor 無法成立。caller 需在 .pen 內補可見文字節點，或改走 form-story-spec caller-driven 路徑` |
| `target-dir-invalid` | Phase 1: `$$target_dir` 缺項 / 非絕對路徑 / parent 不存在 | `target_dir 無效；請給絕對路徑，且 parent 必須先存在（例 ${TRUTH_BOUNDARY_ROOT}/contracts/components/）` |
| `target-dir-conflict` | Phase 9: `mode == "create"` 但檔案已存在 | `target 內已有同名 component / story 檔；若確認要覆寫請改 mode=overwrite，否則先清空對應 <ComponentId>/ 目錄` |
| `write-io-failed` | Phase 9: WRITE 或 CREATE dir 失敗 | `寫檔失敗（權限 / 磁碟 / fs error）；請 caller 確認 target_dir 可寫後重試` |

## §2 對齊原則

1. 每一行對應 SOP 內一個具名 ASSERT / IF 的失敗模式；新增 ASSERT 必同步加列。
2. `failure_kind` 全為 kebab-case；message 為單行白話文，禁夾 stack trace（stderr 由 caller 自取）。
3. caller 收到 message 後決定上游修復推理包 / 指引 user 修 `.pen` / 視為 hard error；本 skill 在 message 內**不**提供修復步驟（修復 SOP 屬 caller 的事，避免重複 source of truth）。
4. `screen-id-missing` 為非 hard-fail 例外：列候選給 caller、等補後重啟 Phase 4。
5. 本 skill 為 **producer**：寫 `<id>.tsx` + `<id>.stories.tsx` 兩檔到 `target_dir/<id>/`；因此有 `target-dir-invalid` / `target-dir-conflict` / `write-io-failed` 三條寫檔失敗 kind。Build / sidecar / npm 等動作仍**不在 scope**內（那是 `/aibdd-auto-starter` 的事）。

## §3 Phase × 主要 fail kind

| Phase | 主要 fail kind |
|---|---|
| 1 ASSERT intake | `pen-path-invalid` / `target-dir-invalid` |
| 2 VERIFY .pen | `pen-not-parseable` / `pen-version-unsupported` / `pen-no-children` |
| 3 EXTRACT tokens | `pen-no-tokens` |
| 4 MAP screen | `screen-id-not-found` / `screen-id-missing` |
| 5 DETECT components | `no-component-candidates` / `component-name-collision` |
| 6 DERIVE render plan | `accessible-name-prop-missing` |
| 7 RENDER component | _internal RENDER only — assertion failures bubble as `accessible-name-prop-missing` or pattern violations_ |
| 8 RENDER stories | _internal RENDER only — I4 hard gate failures bubble as `accessible-name-prop-missing`_ |
| 9 WRITE | `target-dir-conflict` / `write-io-failed` |
| 10 REPORT producer | _no fail kind — pure EMIT_ |
| 11 HANDLE dispatch | _internal CLASSIFY only_ |
