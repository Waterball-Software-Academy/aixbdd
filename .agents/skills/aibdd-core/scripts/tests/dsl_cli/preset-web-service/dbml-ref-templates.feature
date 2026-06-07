Feature: web-service plugin expands RefPart into a relationship-derived state-relationship-verifier template

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
      }

      Table memberships {
        id int [pk, increment]
        user_id int [not null, ref: > users.id]
      }
      """
    When DBMLSpecParser parses the last file
    And the web-service plugin generates templates from the parsed parts

  Rule: 後置（狀態）- 每條 relationship part 應展開為一條 state-relationship-verifier template
    Example: memberships.user_id > users.id → relationship-derived verifier
      Then a template with name "memberships_user_id_to_users_id.state-relationship-verifier" exists with handler "state-relationship-verifier"
      And template "memberships_user_id_to_users_id.state-relationship-verifier" has target_part_path "data/data.dbml#ref:memberships.user_id>users.id"

  Rule: 後置（狀態）- relationship-derived verifier 應只帶關係兩端的 candidate bindings
    Example: candidate keys 聚焦 memberships.user_id 與 users.id
      Then template "memberships_user_id_to_users_id.state-relationship-verifier" has candidate keys: memberships_user_id, users_id
      And template "memberships_user_id_to_users_id.state-relationship-verifier" candidate "memberships_user_id" has target "data/data.dbml#memberships.user_id"
      And template "memberships_user_id_to_users_id.state-relationship-verifier" candidate "users_id" has target "data/data.dbml#users.id"
