Feature: OpenAPISpecParser identifies each operation as a single api_operation part

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

  Rule: 後置（狀態）- 每個 OpenAPI operation 應產出單一 api_operation Part
    Example: 一個 POST operation 對應一個 part
      When OpenAPISpecParser parses the last file
      Then exactly 1 part of kind "api_operation" is returned

  Rule: 後置（狀態）- api_operation Part 的 path/method/operation_id 應對應 OpenAPI 原文
    Example: joinRoom 的 path、method、operationId 完整保留
      When OpenAPISpecParser parses the last file
      Then the part's path is "/rooms/{roomNo}/join"
      And the part's method is "post"
      And the part's operation_id is "joinRoom"

  Rule: 後置（狀態）- api_operation Part 的 target_part_path 應為 JSON Pointer 形式
    Example: target_part_path 以 ~1 escape 路徑分隔符
      When OpenAPISpecParser parses the last file
      Then the part's target_part_path is "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post"
