Feature: OpenAPISpecParser fails clearly when an external $ref target is missing

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
                      $ref: 'missing-common.yml#/components/schemas/RoomSnapshot'
      """

  Rule: 後置（失敗）- 缺失 external ref 應 raise OpenAPIParseError 且 message 帶缺失檔名
    Example: missing-common.yml 不存在時解析失敗
      When OpenAPISpecParser parses the last file and captures the exception
      Then the captured exception is of type "OpenAPIParseError"
      And the captured exception message mentions "missing-common.yml"
