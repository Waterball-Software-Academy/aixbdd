Feature: web-service plugin expands DbmlTablePart into state-builder + state-verifier templates

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
      }
      """
    When DBMLSpecParser parses the last file
    And the web-service plugin generates templates from the parsed parts

  Rule: 後置（狀態）- 每張 table 應展開為 state-builder + state-verifier 兩條 template
    Example: users 表 → users.state-builder + users.state-verifier
      Then a template with name "users.state-builder" exists with handler "state-builder"
      And a template with name "users.state-verifier" exists with handler "state-verifier"

  Rule: 後置（狀態）- state-builder template 之候選 target 應走 DBML spec anchor scheme
    Example: nickname 候選 target 為 data/data.dbml#users.nickname
      Then template "users.state-builder" candidate "nickname" has target "data/data.dbml#users.nickname"

  Rule: 後置（狀態）- state-builder / state-verifier 之 target_part_path 應指向 table root
    Example: 兩條 template target_part_path 都是 data/data.dbml#users
      Then template "users.state-builder" has target_part_path "data/data.dbml#users"
      And template "users.state-verifier" has target_part_path "data/data.dbml#users"
