Feature: DBMLSpecParser derives not_null_columns view from each Table's columns

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
        email varchar [unique]
        created_at timestamp [default: `now()`]
      }
      """

  Rule: 後置（狀態）- not_null_columns 應收下所有 nullable=false 的欄位
    Example: users 之 not_null_columns 為 [id, nickname]（pk 隱含 not null；[not null] 明示）
      When DBMLSpecParser parses the last file
      Then the part named "users" has not_null_columns:
        | name     |
        | id       |
        | nickname |

  Rule: 後置（狀態）- 每欄 target_part_path 應為 `<spec>#<table>.<column>`
    Example: users.id 與 users.nickname 路徑正確
      When DBMLSpecParser parses the last file
      Then the column "users.id" has target_part_path "data/data.dbml#users.id"
      And the column "users.nickname" has target_part_path "data/data.dbml#users.nickname"
