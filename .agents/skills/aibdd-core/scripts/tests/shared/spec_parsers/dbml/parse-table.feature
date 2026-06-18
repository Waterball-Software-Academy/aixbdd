Feature: DBMLSpecParser collects one table Part per Table block

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
        email varchar [unique]
        bio text
        created_at timestamp [default: `now()`]
      }

      Table room_members {
        room_no varchar [not null]
        player_id varchar [not null]
      }
      """

  Rule: 後置（狀態）- 每張 DBML Table 應產出單一 table Part
    Example: data.dbml 內兩張 Table → 兩個 part
      When DBMLSpecParser parses the last file
      Then exactly 2 parts of kind "table" are returned

  Rule: 後置（狀態）- table Part 的 table_name 與 target_part_path 應對應 DBML 原文
    Example: users / room_members table 各自具備正確 identity
      When DBMLSpecParser parses the last file
      Then the part named "users" has target_part_path "data/data.dbml#users"
      And the part named "room_members" has target_part_path "data/data.dbml#room_members"

  Rule: 後置（狀態）- 每張 table 之 columns 應包含全部欄位與其旗標
    Example: users 表 5 欄位、id 為 pk、created_at 帶 default
      When DBMLSpecParser parses the last file
      Then the part named "users" has columns:
        | name       | type      | nullable | is_pk | has_default |
        | id         | int       | false    | true  | false       |
        | nickname   | varchar   | false    | false | false       |
        | email      | varchar   | true     | false | false       |
        | bio        | text      | true     | false | false       |
        | created_at | timestamp | true     | false | true        |

  Rule: 後置（狀態）- table 內含 indexes 區塊時仍應產出 table Part
    Example: users table has an indexes block
      Given a temporary file at "data/indexed.dbml" with content:
        """
        Table users {
          id int [pk]
          email varchar [not null]

          indexes {
            email [unique]
          }
        }
        """
      When DBMLSpecParser parses the last file
      Then exactly 1 part of kind "table" is returned
      And the part named "users" has columns:
        | name  | type    | nullable | is_pk | has_default |
        | id    | int     | false    | true  | false       |
        | email | varchar | false    | false | false       |
