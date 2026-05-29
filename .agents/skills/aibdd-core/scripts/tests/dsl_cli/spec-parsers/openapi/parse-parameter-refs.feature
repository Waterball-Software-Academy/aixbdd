Feature: OpenAPISpecParser resolves parameter $ref to definition-site anchors

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
              - $ref: '#/components/parameters/RoomNo'
            responses:
              '200':
                description: OK
      components:
        parameters:
          RoomNo:
            name: roomNo
            in: path
            required: true
            schema:
              type: string
      """

  Rule: 後置（狀態）- parameter $ref 應展開為 request_input 且保留 required/source
    Example: roomNo 來自 components/parameters/RoomNo
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name   | source | required |
        | roomNo | path   | true     |

  Rule: 後置（狀態）- parameter $ref 的 target_part_path 應指向 definition site
    Example: roomNo 錨定在 components/parameters/RoomNo
      When OpenAPISpecParser parses the last file
      Then the request_input named "roomNo" has target_part_path "contracts/room.api.yml#/components/parameters/RoomNo"
