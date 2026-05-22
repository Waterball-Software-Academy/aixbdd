Feature: dsl_cli supplement-required-fields 自動把 DB not_null 且無 default 之缺漏欄位補進 DSL entry 之 datatable_bindings

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
        email varchar [unique]
        created_at timestamp [not null]
        updated_at timestamp [not null, default: `now()`]
      }
      """
    And a temporary file at "data/data.dsl.yml" with content:
      """
      dsl_steps:
        - format: 系統中存在玩家 "{玩家暱稱}"
          name: users.state-builder
          handler: state-builder
          target_part_path: data/data.dbml#users
          param_bindings:
            玩家暱稱:
              target: data/data.dbml#users.nickname
          datatable_bindings: {}

        - format: 驗證玩家 "{玩家暱稱}" 已建立
          name: users.state-verifier
          handler: state-verifier
          target_part_path: data/data.dbml#users
          param_bindings:
            玩家暱稱:
              target: data/data.dbml#users.nickname
          datatable_bindings: {}
      """
    When dsl_cli supplement-required-fields runs

  Rule: 後置（狀態）- not_null 且無 default 之欄位若未在 param_bindings / datatable_bindings 出現，應補進 datatable_bindings 並標 required:false + default_value 為 placeholder "<FILL IN>"
    Example: created_at [not null]（無 default）未出現於既有 bindings → 補進 datatable_bindings
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has datatable binding "created_at"
      And dsl entry "users.state-builder" in "data/data.dsl.yml" datatable binding "created_at" has required "false"
      And dsl entry "users.state-builder" in "data/data.dsl.yml" datatable binding "created_at" has target "data/data.dbml#users.created_at"
      And dsl entry "users.state-builder" in "data/data.dsl.yml" datatable binding "created_at" has default_value "<FILL IN>"

  Rule: 後置（狀態）- 已出現於 param_bindings 之欄位不應重複補進 datatable_bindings
    Example: nickname 已在 param_bindings → 不出現於 datatable_bindings
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has no datatable binding "nickname"

  Rule: 後置（狀態）- has_default 之欄位不應補進 datatable_bindings（DB 自帶 fallback）
    Example: updated_at [not null, default: `now()`] → 不出現於 datatable_bindings
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has no datatable binding "updated_at"

  Rule: 後置（狀態）- nullable 欄位不應補進 datatable_bindings（NULL 即可）
    Example: email（nullable）→ 不出現於 datatable_bindings
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has no datatable binding "email"

  Rule: 後置（狀態）- PK 欄位不應補進 datatable_bindings
    Example: id（pk）→ 不出現於 datatable_bindings
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has no datatable binding "id"

  Rule: 後置（狀態）- SupplementReport 應列出新增的欄位、所屬 entry、寫入哪個檔
    Example: 首次補進 1 欄位（created_at）→ report 含一條 supplement record
      Then SupplementReport contains 1 supplemented field
      And SupplementReport supplemented "created_at" into entry "users.state-builder" in "data/data.dsl.yml"

  Rule: 後置（狀態）- 命令應 idempotent — 二次執行不應重複新增已存在欄位
    Example: supplement 再跑一次，SupplementReport 為 0 且既有 default_value 不被覆寫
      When dsl_cli supplement-required-fields runs
      Then SupplementReport contains 0 supplemented fields
      And dsl entry "users.state-builder" in "data/data.dsl.yml" datatable binding "created_at" has default_value "<FILL IN>"

  Rule: 後置（狀態）- state-verifier handler 不參與 supplement（verifier 只驗證、不建 state，無須補 DB 約束）
    Example: state-verifier entry 之 datatable_bindings 保持空 {}，created_at 不會被補進
      Then dsl entry "users.state-verifier" in "data/data.dsl.yml" has no datatable binding "created_at"
      And dsl entry "users.state-verifier" in "data/data.dsl.yml" has empty datatable_bindings
