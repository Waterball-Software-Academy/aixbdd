Feature: dsl_to_isa treats schema property param_bindings as request body fields (joinGameRoom pattern)

  # 本 feature 涵蓋 dsl_to_isa 修補（2025-05）中與 API 呼叫相關者：
  #   • param_bindings 指向 #/components/schemas/.../properties/<field> → body 欄位名入 table
  #   • 不得產生空字串 table key（regression）
  #   • target / binding 使用 codebase-root 前綴 specs/contracts/...（backend 實際寫法）
  #
  # 其他修補見 sibling features：
  #   dsl-corpus-collection.feature、entity-map-nested-list.feature、
  #   state-ref-verifier-translate.feature

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 後置（狀態）- 僅 requestBody、param_bindings 指向 schema properties 時，table 以 JSON 欄位名入列
    Example: joinGameRoom — roomCode + playerDisplayName，無 path/query param
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /game-rooms/join:
            post:
              summary: 以四位房號開房或加入現有房間
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/JoinGameRoomRequest'
              responses:
                '200':
                  description: ok
        components:
          schemas:
            JoinGameRoomRequest:
              type: object
              required: [roomCode, playerDisplayName]
              properties:
                roomCode:
                  type: string
                playerDisplayName:
                  type: string
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "玩家以房號 {房號}、顯示名稱 {顯示名稱} 呼叫加入遊戲房"
            name: joinGameRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1game-rooms~1join/post
            param_bindings:
              房號:
                target: contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/roomCode
              顯示名稱:
                target: contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/playerDisplayName
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "joinGameRoom.operation-invoke" has empty params list
      And dsl step "joinGameRoom.operation-invoke" has isa_steps[0].instruction equal to "(No Actor) 以四位房號開房或加入現有房間, call table:"
      And dsl step "joinGameRoom.operation-invoke" has isa_steps[0].table equal to:
        """
        roomCode: "{{房號}}"
        playerDisplayName: "{{顯示名稱}}"
        """

  Rule: 後置（狀態）- 不得產生空字串 table key（regression：兩個 schema property 合併成 ""）
    Example: joinGameRoom 翻譯後 isa_steps[0].table 不含 key ""
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /game-rooms/join:
            post:
              summary: 以四位房號開房或加入現有房間
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        roomCode: { type: string }
                        playerDisplayName: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "玩家以房號 {房號}、顯示名稱 {顯示名稱} 呼叫加入遊戲房"
            name: joinGameRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1game-rooms~1join/post
            param_bindings:
              房號:
                target: contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/roomCode
              顯示名稱:
                target: contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/playerDisplayName
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "joinGameRoom.operation-invoke" has isa_steps[0].table key "roomCode" with value "{{房號}}"
      And dsl step "joinGameRoom.operation-invoke" has isa_steps[0].table key "playerDisplayName" with value "{{顯示名稱}}"

  Rule: 後置（狀態）- target 使用 specs/contracts/ 前綴（boundary codebase root）仍可載入 OpenAPI
    Example: joinGameRoom — 與 backend dsl 相同的路徑寫法
      Given a temporary file at "specs/contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /game-rooms/join:
            post:
              summary: 以四位房號開房或加入現有房間
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        roomCode: { type: string }
                        playerDisplayName: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "玩家以房號 {房號}、顯示名稱 {顯示名稱} 呼叫加入遊戲房"
            name: joinGameRoom.operation-invoke
            handler: operation-invoke
            target_part_path: specs/contracts/games.api.yml#/paths/~1game-rooms~1join/post
            param_bindings:
              房號:
                target: specs/contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/roomCode
              顯示名稱:
                target: specs/contracts/games.api.yml#/components/schemas/JoinGameRoomRequest/properties/playerDisplayName
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "joinGameRoom.operation-invoke" has isa_steps[0].table equal to:
        """
        roomCode: "{{房號}}"
        playerDisplayName: "{{顯示名稱}}"
        """
