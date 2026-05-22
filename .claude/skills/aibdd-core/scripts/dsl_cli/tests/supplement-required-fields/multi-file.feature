Feature: dsl_cli supplement-required-fields 跨多個 spec / dsl 檔 dispatch，並對 target_part_path 對應不到任何 spec part 之 entry 做 skip

  Background:
    Given a temporary file at "data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        created_at timestamp [not null]
      }
      """
    And a temporary file at "contracts/room.api.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Room API
        version: 1.0.0
      paths:
        /rooms/{roomNo}/join:
          post:
            operationId: joinRoom
            parameters:
              - name: roomNo
                in: path
                required: true
                schema:
                  type: string
            requestBody:
              required: true
              content:
                application/json:
                  schema:
                    type: object
                    required: [playerId]
                    properties:
                      playerId:
                        type: string
            responses:
              '200':
                description: OK
      """
    And a temporary file at "data/data.dsl.yml" with content:
      """
      dsl_steps:
        - format: 系統中存在玩家
          name: users.state-builder
          handler: state-builder
          target_part_path: data/data.dbml#users
          param_bindings: {}
          datatable_bindings: {}

        - format: 系統中存在過時資料 "{狀態}"
          name: legacy.state-builder
          handler: state-builder
          target_part_path: data/data.dbml#legacy_table
          param_bindings:
            狀態:
              target: data/data.dbml#legacy_table.status
          datatable_bindings: {}
      """
    And a temporary file at "contracts/room.dsl.yml" with content:
      """
      dsl_steps:
        - format: 玩家加入房間 "{roomNo}"
          name: joinRoom.operation-invoke
          handler: operation-invoke
          target_part_path: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post
          param_bindings:
            roomNo:
              target: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0
          datatable_bindings: {}
      """
    When dsl_cli supplement-required-fields runs

  Rule: 後置（狀態）- 應同時 dispatch DBML 與 OpenAPI 之 entry 到對應 spec_parser
    Example: users.state-builder 從 data.dbml 補 created_at；joinRoom.operation-invoke 從 room.api.yml 補 playerId
      Then dsl entry "users.state-builder" in "data/data.dsl.yml" has datatable binding "created_at"
      And dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" has datatable binding "playerId"

  Rule: 後置（狀態）- target_part_path 對應不到任何 spec part 之 entry 應 skip 不報錯
    Example: legacy.state-builder 指向不存在的 data.dbml#legacy_table → skip、datatable_bindings 維持空
      Then dsl entry "legacy.state-builder" in "data/data.dsl.yml" has empty datatable_bindings

  Rule: 後置（狀態）- SupplementReport 應列出 skipped entries（含 entry name、檔名、原因）
    Example: legacy.state-builder 被列入 skipped；users.state-builder 與 joinRoom.operation-invoke 列入 supplemented
      Then SupplementReport contains 2 supplemented fields
      And SupplementReport contains 1 skipped entry
      And SupplementReport skipped entry "legacy.state-builder" in "data/data.dsl.yml" with reason "target_part_path 對應不到 spec part"
