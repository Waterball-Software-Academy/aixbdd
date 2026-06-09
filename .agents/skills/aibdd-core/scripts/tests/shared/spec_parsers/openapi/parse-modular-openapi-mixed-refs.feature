Feature: OpenAPISpecParser resolves mixed local and external $ref in one operation

  Background:
    Given a temporary file at "contracts/common.yml" with content:
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

  Rule: 後置（狀態）- 同一 operation 的 parameter/body/response $ref 應一次收齊
    Example: path + body + 200 response surfaces 全出現
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name     | source | required |
        | roomNo   | path   | true     |
        | playerId | body   | true     |
        | nickname | body   | false    |
      And the part's response_properties has entries:
        | name        | json_path        |
        | roomNo      | $.roomNo         |
        | playerCount | $.playerCount    |

  Rule: 後置（狀態）- mixed refs 的 anchors 應分別落在 api 檔與 common.yml definition site
    Example: parameter 在 room.api.yml、response property 在 common.yml
      When OpenAPISpecParser parses the last file
      Then the request_input named "roomNo" has target_part_path "contracts/room.api.yml#/components/parameters/RoomNo"
      And the request_input named "playerId" has target_part_path "contracts/room.api.yml#/components/schemas/JoinRequest/properties/playerId"
      And the response_property named "playerCount" has target_part_path "contracts/common.yml#/components/schemas/RoomSnapshot/properties/playerCount"
