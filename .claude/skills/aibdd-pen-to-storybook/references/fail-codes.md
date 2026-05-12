# Fail codes — caller-return message map

> 純 declarative reference。Phase 10 CLASSIFY 與 DERIVE 從此表查 `failure_kind` → `caller-return message`。
> 任何新加錯誤碼都必須先寫進此表，才能在 Phase N 內 ASSERT / IF 觸發。

## §1 對照表

| failure_kind | trigger condition (Phase) | caller-return message |
|---|---|---|
| `pen-path-invalid` | Phase 1: `$$pen_path` 缺項 / 不存在 / 副檔名非 `.pen` | `pen_path 無效；確認絕對路徑且副檔名為 .pen` |
| `target-dir-conflict` | Phase 1: `$$target_dir` 已存在且 `mode != "overwrite"` | `target_dir 已存在，caller 需指定 mode=overwrite 或改路徑` |
| `pen-not-parseable` | Phase 2: `file` 結果非 UTF-8 / `jq` 解析失敗 | `.pen 解析失敗（可能是 binary 或舊版 schema）；建議用最新 Pencil 重存後重試` |
| `pen-version-unsupported` | Phase 2: `$$schema_version` 非 `^2\.\d+$` | `不支援的 .pen schema version；本 skill 只接受 v2.x` |
| `pen-no-children` | Phase 2: `$$pen_doc.children` 為空陣列 | `.pen 無 top-level frame；無內容可轉換` |
| `pen-no-tokens` | Phase 3: `Document.variables` 全空或全為 boolean | `.pen 沒有任何 design token；通常代表設計尚未做完，建議回 Pencil 補變數` |
| `screen-id-not-found` | Phase 4: `$$screen_id` 不在 top-level frame 列表 | `screen_id 無效；列出可選清單後請 caller 重指定` |
| `screen-id-missing` | Phase 4: `$$screen_id` 未指定 | _特殊：列 top-level 候選回 caller，等補後重啟 Phase 4，不視為 hard fail_ |
| `no-component-candidates` | Phase 5: `$$component_table.rows` 為空 | `偵測不到任何 component candidate；該 screen 可能無重複結構，建議改 page-level scaffold 後手動切` |
| `component-name-collision` | Phase 5: 兩個 candidate 推導出同 PascalCase 名 | `component name 衝突；caller 需在 .pen 改名後重跑` |
| `write-io-failed` | Phase 6 / Phase 7: WRITE IO 失敗 | `WRITE IO failed；檢查 target_dir 權限或磁碟空間` |
| `npm-install-failed` | Phase 8: `npm install` exit_code != 0 | `npm install 失敗；附上 stderr 給 caller，常見為 registry / network 問題` |
| `tsc-error` | Phase 8: `tsc --noEmit` exit_code != 0 | `tsc --noEmit 有型別錯誤；不進 build-storybook（storybook 錯誤更難 debug）；附 tsc 輸出` |
| `storybook-build-failed` | Phase 8: `npm run build-storybook` exit_code != 0 | `build-storybook 失敗；附 storybook log；常見為 framework 錯選（用了 @storybook/nextjs 而非 nextjs-vite）` |
| `return-unreachable` | Phase 9: RETURN 失敗（caller 已斷線） | _特殊：寫 sidecar `${$$target_dir}/.aibdd-pen-to-storybook.report` 後 STOP，不送訊息_ |

## §2 對齊原則

1. 每一行對應 SOP 內一個具名 ASSERT / IF 的失敗模式；新增 ASSERT 必同步加列。
2. `failure_kind` 全為 kebab-case；message 為單行白話文，禁夾 stack trace（stderr 由 caller 自取）。
3. caller 收到 message 後決定上游修復推理包 / 指引 user 修 `.pen` / 視為 hard error；本 skill 在 message 內**不**提供修復步驟（修復 SOP 屬 caller 的事，避免重複 source of truth）。
4. `screen-id-missing` 與 `return-unreachable` 為兩個非 hard-fail 例外：
   - 前者列候選給 caller、等補後重啟 Phase 4
   - 後者改寫 sidecar 報告，避免靜默丟失最後一筆 report

## §3 Phase × 主要 fail kind

| Phase | 主要 fail kind |
|---|---|
| 1 ASSERT intake | `pen-path-invalid` / `target-dir-conflict` |
| 2 VERIFY .pen | `pen-not-parseable` / `pen-version-unsupported` / `pen-no-children` |
| 3 EXTRACT tokens | `pen-no-tokens` |
| 4 MAP screen | `screen-id-not-found` / `screen-id-missing` |
| 5 DETECT components | `no-component-candidates` / `component-name-collision` |
| 6 SCAFFOLD | `write-io-failed` |
| 7 RENDER | `write-io-failed` |
| 8 VERIFY | `npm-install-failed` / `tsc-error` / `storybook-build-failed` |
| 9 REPORT | `return-unreachable` |
