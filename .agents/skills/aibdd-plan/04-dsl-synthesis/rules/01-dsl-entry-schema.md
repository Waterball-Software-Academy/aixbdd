# DSL entry schema

每條 DSL entry 採扁平單層 schema：

```yml
- format: 操作者 "{操作者Id}" 於大廳以房號 "{房號}" 開房或加入  # gherkin step 句型，通常為 actor-{actor identifiable key}-operation / object-{object identifiable key}
  name: joinRoom.operation-invoke  # DSL instruction 的唯一 id；plugin auto-gen 規則為 <spec-native-id>.<handler>（OpenAPI 用 operationId、DBML 用 table_name）
  handler: operation-invoke
  target_part_path: <Spec anchor>  # 此 DSL instruction 對應規格部位的絕對路徑

  # param_bindings：必要參數，必須以 {key} 在 format 中被參考
  param_bindings:
    <param's key name>:
      target: <Spec anchor>  # 該參數在規格內的絕對路徑

  # datatable_bindings：Gherkin DataTable 參數，不在 format 中被 {key} 參考；可必要或非必要
  datatable_bindings:
    <param's key name>:
      required: true | false       # 必要 → DataTable 必填；非必要 → 可省略或於 DataTable 可選提供
      target: <Spec anchor | response:... | literal:... | stub_payload:...>
      default_value: <value>       # 僅當 required: false 時可定義
```

## Target URI Schemes

`target_part_path` 與 `param_bindings.*.target` / `datatable_bindings.*.target` 的字串值只能落在以下 6 種 scheme，eval 階段會驗 scheme 合法性：

| Scheme | 形態 | 出現於 | 語義 |
|---|---|---|---|
| Spec anchor (OpenAPI) | `<spec_file>#<json_pointer>` | `target_part_path`、bindings.target | 指向 OpenAPI 規格內某節點，JSON Pointer 依 RFC 6901，路徑 `/` 需 escape 成 `~1`。e.g., `contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post` |
| Spec anchor (DBML) | `<spec_file>#<table>` 或 `<spec_file>#<table>.<column>` | `target_part_path`、bindings.target | 指向 DBML 規格內某表或某欄。e.g., `data/data.dbml#users`、`data/data.dbml#users.nickname` |
| Code anchor | `code:<file_path>#<function_name>` 或 `code:<file_path>#<Class>.<method>` | `target_part_path`、bindings.target | 指向程式碼某 file + function / class method，粒度為 function（不到行號）。用於 code-level / architectural-level handler — 對應的 DSL instruction 落在程式碼部位而非 spec 部位。eval 靜態檢查檔存在且 function/method name 在該檔出現。e.g., `code:src/domain/room_service.py#join_room`、`code:src/main/java/.../RoomService.java#RoomService.joinRoom` |
| Response JSONPath | `response:<jsonpath>` | bindings.target（僅限 response-readmodel 等 verify handler 用） | runtime 從 invoke 取得的 response body 抽值；`$` 為 root。e.g., `response:$.roomNo` |
| Literal type hint | `literal:<type>` | bindings.target（time-control 等 shared DSL） | 不指向 spec — 由 Gherkin DataTable 直接提供 literal value，`<type>` 標示型別 hint 供 red-execute 解析。e.g., `literal:iso8601-instant` |
| Stub payload field | `stub_payload:<field_path>` | bindings.target（external-stub handler） | runtime 從 external-stub 的 mock payload 取欄位。e.g., `stub_payload:targetUserId`、`stub_payload:body` |

合法性收斂：

1. `target_part_path` 只能用 Spec anchor (OpenAPI / DBML) 或 Code anchor 三種 — 它的語義是「該 DSL instruction 對應的規格部位或程式碼部位」，必須能在 OpenAPI / DBML 規格內或程式碼檔內定位。
2. `bindings.target` 6 種皆合法；具體允許哪幾種依 handler 而異（譬如 `state-builder` 只接 Spec anchor，`operation-response-verify` 接 Spec anchor + `response:`），由 plugin `generate_templates` 在構造時保證。

完整 7-handler 範例見 `research/aibdd-plan-dsl合成步驟超級 harness 計劃/spec.md` §1。
