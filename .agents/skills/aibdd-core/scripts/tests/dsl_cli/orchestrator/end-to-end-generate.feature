Feature: dsl_cli generate-dsl-instructions on joinRoom (spec §1 worked example)

  Background:
    Given a temporary file at "specs/contracts/room.api.yml" with content:
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
                      nickname:
                        type: string
            responses:
              '200':
                description: OK
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        roomNo:
                          type: string
                        playerCount:
                          type: integer
      """
    And a temporary file at "specs/data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
        nickname varchar [not null]
      }
      Table room_members {
        room_no varchar [not null]
        player_id varchar [not null]
      }

      Ref: room_members.player_id > users.id
      """
    And a temporary file at "specs/contracts/room.dsl.yml" with content:
      """
      dsl_steps: []
      """
    And a temporary file at "specs/data/data.dsl.yml" with content:
      """
      dsl_steps: []
      """
    When dsl_cli generate-dsl-instructions runs for boundary "web-service"

  Rule: 後置（狀態）- joinRoom operation 應展開為 3 條 entry 落到 contracts/room.dsl.yml
    Example: invoke + response-success-and-failure + response-readmodel 三 entry name 出現
      Then the file "specs/contracts/room.dsl.yml" contains the text "name: joinRoom.operation-invoke"
      And the file "specs/contracts/room.dsl.yml" contains the text "name: joinRoom.operation-response-success-and-failure"
      And the file "specs/contracts/room.dsl.yml" contains the text "name: joinRoom.operation-response-success-readmodel"

  Rule: 後置（狀態）- DBML 兩張 table 應各展開 builder + verifier，落到 data/data.dsl.yml
    Example: users + room_members 共 4 條 entry
      Then the file "specs/data/data.dsl.yml" contains the text "name: users.state-builder"
      And the file "specs/data/data.dsl.yml" contains the text "name: users.state-verifier"
      And the file "specs/data/data.dsl.yml" contains the text "name: room_members.state-builder"
      And the file "specs/data/data.dsl.yml" contains the text "name: room_members.state-verifier"

  Rule: 後置（狀態）- DBML relationship 應額外展開一條 relationship-derived verifier
    Example: room_members.player_id > users.id 會落成 state-verifier skeleton
      Then the file "specs/data/data.dsl.yml" contains the text "name: room_members_player_id_to_users_id.state-verifier"
      And the file "specs/data/data.dsl.yml" contains the text "target_part_path: specs/data/data.dbml#ref:room_members.player_id>users.id"
      And the file "specs/data/data.dsl.yml" contains the text "#   room_members_player_id:"
      And the file "specs/data/data.dsl.yml" contains the text "#   users_id:"

  Rule: 後置（狀態）- 寫出的 entry 皆為 HARNESS skeleton 形態（format 為 <FILL IN>）
    Example: room.dsl.yml 含 `<FILL IN>` 占位
      Then the file "specs/contracts/room.dsl.yml" contains the text "<FILL IN>"

  Rule: 後置（狀態）- invoke entry 應帶候選參數註解，列出 spec 中的 request_inputs
    Example: playerId、roomNo、nickname 三條候選註解出現
      Then the file "specs/contracts/room.dsl.yml" contains the text "#   playerId:"
      And the file "specs/contracts/room.dsl.yml" contains the text "#   roomNo:"
      And the file "specs/contracts/room.dsl.yml" contains the text "#   nickname:"
