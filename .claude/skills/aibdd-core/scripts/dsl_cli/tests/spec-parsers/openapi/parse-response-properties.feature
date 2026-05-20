Feature: OpenAPISpecParser collects response_properties from 2xx response schemas

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
              '400':
                description: Bad Request
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        errorCode:
                          type: string
      """

  Rule: 後置（狀態）- response_properties 應僅收 2xx 成功回應的 schema properties
    Example: 200 之 roomNo / playerCount 收齊，400 之 errorCode 不收
      When OpenAPISpecParser parses the last file
      Then the part's response_properties has entries:
        | name        | json_path        |
        | roomNo      | $.roomNo         |
        | playerCount | $.playerCount    |

  Rule: 後置（狀態）- 每條 response_property 的 target_part_path 應指向 200 response schema property 節點
    Example: roomNo 的 target 落在 responses/200/.../schema/properties/roomNo
      When OpenAPISpecParser parses the last file
      Then the response_property named "roomNo" has target_part_path "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/responses/200/content/application~1json/schema/properties/roomNo"
