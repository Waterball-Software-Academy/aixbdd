Feature: dsl_cli generate-dsl-instructions on modular OpenAPI with $ref

  Background:
    Given a temporary file at "specs/contracts/common.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Common
        version: 1.0.0
      components:
        schemas:
          RoomSnapshot:
            type: object
            properties:
              roomNo:
                type: string
              playerCount:
                type: integer
      """
    And a temporary file at "specs/contracts/room.api.yml" with content:
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
              - $ref: '#/components/parameters/RoomNo'
            requestBody:
              required: true
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/JoinRequest'
            responses:
              '200':
                description: OK
                content:
                  application/json:
                    schema:
                      $ref: 'common.yml#/components/schemas/RoomSnapshot'
      components:
        parameters:
          RoomNo:
            name: roomNo
            in: path
            required: true
            schema:
              type: string
        schemas:
          JoinRequest:
            type: object
            required: [playerId]
            properties:
              playerId:
                type: string
              nickname:
                type: string
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

  Rule: 後置（狀態）- modular joinRoom operation 應展開為 2 條 entry 落到 contracts/room.dsl.yml
    Example: invoke + response-verify 兩 entry name 出現
      Then the file "specs/contracts/room.dsl.yml" contains the text "name: joinRoom.operation-invoke"
      And the file "specs/contracts/room.dsl.yml" contains the text "name: joinRoom.operation-response-verify"

  Rule: 後置（狀態）- invoke entry 應帶候選參數註解，從 resolved request schema 欄位 fan-out
    Example: playerId、roomNo、nickname 三條候選註解出現
      Then the file "specs/contracts/room.dsl.yml" contains the text "#   playerId:"
      And the file "specs/contracts/room.dsl.yml" contains the text "#   roomNo:"
      And the file "specs/contracts/room.dsl.yml" contains the text "#   nickname:"

  Rule: 後置（狀態）- readmodel entry 應帶 resolved response property 候選註解
    Example: roomNo 與 playerCount 候選註解出現
      Then the file "specs/contracts/room.dsl.yml" contains the text "#   roomNo:"
      And the file "specs/contracts/room.dsl.yml" contains the text "#   playerCount:"
