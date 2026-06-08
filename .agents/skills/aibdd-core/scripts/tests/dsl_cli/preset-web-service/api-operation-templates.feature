Feature: web-service plugin expands ApiOperationPart into invoke + readmodel templates

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
    When OpenAPISpecParser parses the last file
    And the web-service plugin generates templates from the parsed parts

  Rule: 後置（狀態）- joinRoom operation 應展開為 invoke + response-readmodel 兩條 template
    Example: 兩個 handler 各一條，name 以 <operationId>.<handler> 自動生成
      Then a template with name "joinRoom.operation-invoke" exists with handler "operation-invoke"
      And a template with name "joinRoom.operation-response-verify" exists with handler "operation-response-verify"

  Rule: 後置（狀態）- invoke template 之候選參數應涵蓋全部 request_inputs（path + body）
    Example: roomNo + playerId + nickname 三條候選
      Then template "joinRoom.operation-invoke" has candidate keys: roomNo, playerId, nickname

  Rule: 後置（狀態）- invoke template 之候選 target 應走 OpenAPI spec anchor scheme
    Example: roomNo 候選 target 指向 parameters/0
      Then template "joinRoom.operation-invoke" candidate "roomNo" has target "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0"

  Rule: 後置（狀態）- readmodel template 之候選參數應走 `response:` JSONPath scheme
    Example: roomNo / playerCount 兩條候選分別為 response:$.roomNo / response:$.playerCount
      Then template "joinRoom.operation-response-verify" candidate "roomNo" has target "response:$.roomNo"
      And template "joinRoom.operation-response-verify" candidate "playerCount" has target "response:$.playerCount"
