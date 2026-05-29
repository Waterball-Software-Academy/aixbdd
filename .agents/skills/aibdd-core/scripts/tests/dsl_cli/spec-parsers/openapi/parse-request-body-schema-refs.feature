Feature: OpenAPISpecParser resolves requestBody schema $ref to definition-site property anchors

  Background:
    Given a temporary file at "contracts/room.api.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Room API
        version: 1.0.0
      paths:
        /rooms/{roomNo}/join:
          post:
            operationId: joinRoom
            requestBody:
              required: true
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/JoinRequest'
            responses:
              '200':
                description: OK
      components:
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

  Rule: 後置（狀態）- requestBody schema $ref 應展開全部 body properties
    Example: playerId required、nickname optional 都出現
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name     | source | required |
        | playerId | body   | true     |
        | nickname | body   | false    |

  Rule: 後置（狀態）- body property 的 target_part_path 應指向 schema definition site
    Example: playerId 錨定在 components/schemas/JoinRequest/properties/playerId
      When OpenAPISpecParser parses the last file
      Then the request_input named "playerId" has target_part_path "contracts/room.api.yml#/components/schemas/JoinRequest/properties/playerId"
      And the request_input named "nickname" has target_part_path "contracts/room.api.yml#/components/schemas/JoinRequest/properties/nickname"
