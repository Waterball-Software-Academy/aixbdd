Feature: OpenAPISpecParser resolves external response schema $ref to definition-site property anchors

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
            responses:
              '200':
                description: OK
                content:
                  application/json:
                    schema:
                      $ref: 'common.yml#/components/schemas/RoomSnapshot'
      """

  Rule: 後置（狀態）- external response schema $ref 應展開 2xx properties
    Example: roomNo 與 playerCount 都出現
      When OpenAPISpecParser parses the last file
      Then the part's response_properties has entries:
        | name        | json_path        |
        | roomNo      | $.roomNo         |
        | playerCount | $.playerCount    |

  Rule: 後置（狀態）- external schema property 的 target_part_path 應指向 common.yml definition site
    Example: roomNo 錨定在 common.yml 的 RoomSnapshot property
      When OpenAPISpecParser parses the last file
      Then the response_property named "roomNo" has target_part_path "contracts/common.yml#/components/schemas/RoomSnapshot/properties/roomNo"
      And the response_property named "playerCount" has target_part_path "contracts/common.yml#/components/schemas/RoomSnapshot/properties/playerCount"
