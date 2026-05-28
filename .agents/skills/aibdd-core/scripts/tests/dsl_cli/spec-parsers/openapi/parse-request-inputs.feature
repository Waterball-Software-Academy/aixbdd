Feature: OpenAPISpecParser collects request inputs from parameters + requestBody

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
      """

  Rule: 後置（狀態）- request_inputs 應同時涵蓋 parameters 與 requestBody schema properties
    Example: roomNo（path）、playerId（body required）、nickname（body optional）三條都出現
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name     | source | required |
        | roomNo   | path   | true     |
        | playerId | body   | true     |
        | nickname | body   | false    |

  Rule: 後置（狀態）- 每條 request_input 的 target_part_path 應指向其 OpenAPI 出處
    Example: playerId 對應 body schema property、roomNo 對應 parameters/0
      When OpenAPISpecParser parses the last file
      Then the request_input named "roomNo" has target_part_path "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0"
      And the request_input named "playerId" has target_part_path "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/requestBody/content/application~1json/schema/properties/playerId"
