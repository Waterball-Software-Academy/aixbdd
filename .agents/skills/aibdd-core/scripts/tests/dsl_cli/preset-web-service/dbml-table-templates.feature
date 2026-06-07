Feature: web-service plugin expands TablePart into state-builder + state-verifier templates

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
        bio text
      }
      """
    When DBMLSpecParser parses the last file
    And the web-service plugin generates templates from the parsed parts

  Rule: 後置（狀態）- 每張 table 應展開為 state-builder + state-verifier 兩條 template
    Example: users 表 → users.state-builder + users.state-verifier
      Then a template with name "users.state-builder" exists with handler "state-builder"
      And a template with name "users.state-verifier" exists with handler "state-verifier"

  Rule: 後置（狀態）- state-builder template 之 nullable 欄位候選 target 應走 DBML spec anchor scheme
    Example: bio（nullable）候選 target 為 data/data.dbml#users.bio
      Then template "users.state-builder" candidate "bio" has target "data/data.dbml#users.bio"

  Rule: 後置（狀態）- state-builder / state-verifier 之 target_part_path 應指向 table root
    Example: 兩條 template target_part_path 都是 data/data.dbml#users
      Then template "users.state-builder" has target_part_path "data/data.dbml#users"
      And template "users.state-verifier" has target_part_path "data/data.dbml#users"

  Rule: 後置（狀態）- state-builder 不應將 auto-increment pk 欄位放入 datatable_bindings
    Example: id int [pk, increment]（Background 已提供）→ 不在 datatable_bindings 中
      Then template "users.state-builder" has no datatable_binding "id"

  Rule: 後置（狀態）- state-builder 應將手動 pk（無 increment）欄位放入 datatable_bindings
    Example: code varchar [pk] → datatable_binding required false, default_value "<FILL IN>"
      Given a temporary file at "data/data.dbml" with content:
        """
        Table products {
          code varchar [pk]
          name varchar [not null]
        }
        """
      When DBMLSpecParser parses the last file
      And the web-service plugin generates templates from the parsed parts
      Then template "products.state-builder" datatable_binding "code" has required false
      And template "products.state-builder" datatable_binding "code" has default_value "<FILL IN>"

  Rule: 後置（狀態）- state-builder 應將 NOT NULL 且無 DBML default 的欄位放入 datatable_bindings，
        required: false，default_value: "<FILL IN>"
    Example: nickname varchar [not null]（Background 已提供）→ datatable_binding required false, default_value "<FILL IN>"
      Then template "users.state-builder" datatable_binding "nickname" has required false
      And template "users.state-builder" datatable_binding "nickname" has default_value "<FILL IN>"

  Rule: 後置（狀態）- state-builder 應將 NOT NULL 且有 DBML default 的欄位放入 datatable_bindings，
        required: false，default_value 為 DBML 設定值
    Example: role varchar [not null, default: 'guest'] → datatable_binding required false, default_value "guest"
      Given a temporary file at "data/data.dbml" with content:
        """
        Table users {
          id int [pk, increment]
          role varchar [not null, default: 'guest']
        }
        """
      When DBMLSpecParser parses the last file
      And the web-service plugin generates templates from the parsed parts
      Then template "users.state-builder" datatable_binding "role" has required false
      And template "users.state-builder" datatable_binding "role" has default_value "guest"
