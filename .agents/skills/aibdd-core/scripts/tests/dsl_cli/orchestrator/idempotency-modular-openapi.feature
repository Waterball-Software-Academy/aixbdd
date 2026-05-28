Feature: generate-dsl-instructions is idempotent for modular OpenAPI with $ref

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
      """
    And a temporary file at "specs/contracts/room.dsl.yml" with content:
      """
      dsl_steps: []
      """
    And a temporary file at "specs/data/data.dbml" with content:
      """
      Table users {
        id int [pk, increment]
      }
      """
    And a temporary file at "specs/data/data.dsl.yml" with content:
      """
      dsl_steps: []
      """

  Rule: 後置（狀態）- modular OpenAPI corpus 重新 generate 應產生 0 added entries
    Example: 含 external response $ref 的 specs 跑兩次，第二次 report 沒有新增
      When dsl_cli generate-dsl-instructions runs for boundary "web-service"
      And dsl_cli generate-dsl-instructions runs again for boundary "web-service"
      Then the second run's GenerationReport has 0 added entries
