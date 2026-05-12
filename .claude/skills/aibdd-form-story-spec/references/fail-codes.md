# Fail codes — caller-return message map

> 純 declarative reference。Phase 6 CLASSIFY 與 DERIVE 從此表查 `failure_kind` → `caller-return message`。
> 任何新加錯誤碼都必須先寫進這張表，才能在 Phase N 內 ASSERT / IF 觸發。

| failure_kind | trigger condition (Phase) | caller-return message |
|---|---|---|
| `empty-payload` | Phase 1: caller payload 完全空 | `empty payload — caller misuse` |
| `target-path-missing` | Phase 1: `$$payload.target_path` 未指定 | `target_path missing` |
| `format-unsupported` | Phase 1: `$$format ∉ {.stories.ts, .stories.tsx}` | `format unsupported` |
| `target-format-mismatch` | Phase 1: `target_path` 副檔名與 `format` 不一致 | `target_path / format mismatch` |
| `component-import-path-missing` | Phase 1: `$$component.import_path` 缺失 | `component import_path missing` |
| `binding-anchor-missing` | Phase 1: 任一 `$story.accessible_name` 缺失，或 `accessible_name_arg.field` / `value` 缺失 | `BINDING_ANCHOR_MISSING — Storybook export 缺 accessible-name args；依 boundary I4，caller 需先補 args 再 DELEGATE，本 skill 不偽造可繫值` |
| `binding-anchor-mismatch` | Phase 1: `$story.accessible_name != $story.accessible_name_arg.value` | `BINDING_ANCHOR_MISMATCH — accessible_name 與 accessible_name_arg.value 不一致；caller 需先同步` |
| `role-missing` | Phase 1: 任一 `$story.role` 缺失 | `ARIA role missing — caller 需指定` |
| `framework-unsupported` | Phase 1: `$framework` 不在 caller-allowed list | `framework unsupported — 目前僅支援 @storybook/nextjs-vite，其他需擴充 variant 文件` |
| `modeling-incomplete` | Phase 1: `exit_status != "complete"` 或 `component_modeling` 任一欄位缺項 | `component modeling units missing` |
| `reserved-export-name` | Phase 2: Story export name 撞 `default` / `meta` | `RESERVED_EXPORT_NAME` |
| `play-import-surface-missing` | Phase 2: `play_steps` 含 step-def 慣用語但 caller 未指定 import surface | `play step missing import surface` |
| `autodocs-conflict` | Phase 2: `tags=["autodocs"]` 與 `parameters.docs.disable=true` 同時出現 | `autodocs / docs-disable conflict` |
| `write-io-failed` | Phase 3: WRITE IO 失敗 | `WRITE IO failed` |
| `path-conflict` | Phase 3: `$$target_path` 已存在且 `mode != overwrite` | `path conflict — target_path 已存在，caller 需指定 mode=overwrite 或改 target_path` |
| `meta-block-malformed` | Phase 4: default export 結構非 Meta block | `META_BLOCK_MALFORMED` |
| `accessible-name-arg-missing-render` | Phase 4: 任一 Story 在 RENDER 後 `args` 仍缺 caller 指定之 accessible-name arg field | `ACCESSIBLE_NAME_ARG_MISSING_AT_RENDER`（指出哪個 export 缺哪個欄位；不自動補） |
| `return-unreachable` | Phase 5: RETURN 失敗（caller 已斷線） | _特殊處理：寫 sidecar `${$$target_path}.report` 後 STOP，不送訊息_ |

### 對齊原則

1. 每一行對應 SOP 內一個具名 ASSERT / IF 的失敗模式；新增 ASSERT 必同步加列。
2. `failure_kind` 全為 kebab-case；message 為單行白話文，禁夾 stack trace。
3. caller 收到 message 後決定上游修復推理包還是視為 hard error；本 skill 不在 message 內提供修復步驟（修復 SOP 屬 caller 的事）。
4. `return-unreachable` 是唯一不送 message 的 kind — 改寫 sidecar 報告，避免靜默丟失最後一筆 report。
