Feature: dsl_to_isa translates DBML relationship ref anchors for state-relationship-verifier

  # ISA 沒有跨表 primitive。一條 #ref:<from>.<col><op><to>.<col> 關聯
  # 拆成「每個 endpoint 一個單表 entity_validate」：from-column 與 to-column
  # 各自展開為 `應該存在一個<entity>, with table: {<column>: {{<DSL key>}}}`。
  # column 名取自 param_bindings 的 target；entity 名以 target 的 table 名
  # 過 entity_to_table_mapping（查不到 fallback 回 table 名），與 state-verifier
  # 渲染一致。不強制 map 存在（缺 map 時退回 table 名，不報錯）。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: entity_validate
          instruction_type: state
          format: '應該存在一個(?P<entity>\S+), with table:'
          data_format: table
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      memberships: memberships
      users: users
      """

  Rule: 後置（狀態）- #ref: 錨點拆成每個 endpoint 一個單表 entity_validate
    Example: memberships.user_id > users.id 關聯拆成兩個 entity_validate
      Given a temporary file at "data/domain.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }

        Table memberships {
          id int [pk, increment]
          user_id int [not null, ref: > users.id]
        }
        """
      And a temporary file at "data/world.dsl.yml" with content:
        """
        dsl_steps:
          - format: "驗證會員 {會員編號} 對應使用者 {使用者編號}"
            name: memberships_user_id_to_users_id.state-relationship-verifier
            handler: state-relationship-verifier
            target_part_path: data/domain.dbml#ref:memberships.user_id>users.id
            param_bindings:
              會員編號:
                target: data/domain.dbml#memberships.user_id
              使用者編號:
                target: data/domain.dbml#users.id
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then the run exits zero
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps length 2
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[0].instruction equal to "應該存在一個memberships, with table:"
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[0].table equal to:
        """
        user_id: "{{會員編號}}"
        """
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[1].instruction equal to "應該存在一個users, with table:"
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[1].table equal to:
        """
        id: "{{使用者編號}}"
        """

  Rule: 後置（狀態）- 每個 endpoint 的 entity 名走 entity_to_table_mapping（與 state-verifier 一致）
    Example: 非 identity mapping 時 instruction 用 entity 名而非 table 名
      Given a temporary file at "data/entity_to_table_mapping.yml" with content:
        """
        entity_to_table_mapping:
          - memberships: 會員資料
          - users: 使用者資料
        """
      And a temporary file at "data/domain.dbml" with content:
        """
        Table users {
          id int [pk, increment]
        }

        Table memberships {
          id int [pk, increment]
          user_id int [not null, ref: > users.id]
        }
        """
      And a temporary file at "data/world.dsl.yml" with content:
        """
        dsl_steps:
          - format: "驗證會員 {會員編號} 對應使用者 {使用者編號}"
            name: memberships_user_id_to_users_id.state-relationship-verifier
            handler: state-relationship-verifier
            target_part_path: data/domain.dbml#ref:memberships.user_id>users.id
            param_bindings:
              會員編號:
                target: data/domain.dbml#memberships.user_id
              使用者編號:
                target: data/domain.dbml#users.id
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then the run exits zero
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[0].instruction equal to "應該存在一個會員資料, with table:"
      And dsl step "memberships_user_id_to_users_id.state-relationship-verifier" has isa_steps[1].instruction equal to "應該存在一個使用者資料, with table:"
