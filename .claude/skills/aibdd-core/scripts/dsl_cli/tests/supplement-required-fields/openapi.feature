Feature: dsl_cli supplement-required-fields 對 OpenAPI required request inputs 進行回補

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
    And a temporary file at "contracts/room.dsl.yml" with content:
      """
      dsl_steps:
        - format: 玩家加入房間 "{roomNo}"
          name: joinRoom.operation-invoke
          handler: operation-invoke
          target_part_path: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post
          param_bindings:
            roomNo:
              target: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/parameters/0
          datatable_bindings: {}
      """
    When dsl_cli supplement-required-fields runs

  Rule: 前置（動作）- required body 欄位若未在 bindings 出現 → 補進 datatable_bindings 並標 required:false + default_value 為 placeholder "<FILL IN>"
    Example: playerId（required body）未在既有 bindings → 補進 datatable_bindings
      Then dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" has datatable binding "playerId"
      And dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" datatable binding "playerId" has required "false"
      And dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" datatable binding "playerId" has target "contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/requestBody/content/application~1json/schema/properties/playerId"
      And dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" datatable binding "playerId" has default_value "<FILL IN>"

  Rule: 前置（動作）- optional body 欄位不應補進 datatable_bindings（spec 不要求）
    Example: nickname（optional body）→ 不出現於 datatable_bindings
      Then dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" has no datatable binding "nickname"

  Rule: 前置（動作）- 已在 param_bindings 之 path param 不應重複補進
    Example: roomNo（required path，已在 param_bindings）→ 不出現於 datatable_bindings
      Then dsl entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml" has no datatable binding "roomNo"

  Rule: 前置（動作）- SupplementReport 應列出新增的 OpenAPI 欄位、所屬 entry、寫入哪個檔
    Example: 首次補進 1 欄位（playerId）→ report 含一條 supplement record
      Then SupplementReport contains 1 supplemented field
      And SupplementReport supplemented "playerId" into entry "joinRoom.operation-invoke" in "contracts/room.dsl.yml"

  Rule: 後置（狀態）- response-success-and-failure / response-readmodel handler 不參與 supplement（response 不建 state，無需補）
    Example: 加入 readmodel entry 後其 datatable_bindings 仍為空
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 加入房間後應收到回應
            name: joinRoom.operation-response-success-readmodel
            handler: operation-response-success-readmodel
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1{roomNo}~1join/post/responses/200/content/application~1json/schema
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli supplement-required-fields runs
      Then dsl entry "joinRoom.operation-response-success-readmodel" in "contracts/room.dsl.yml" has empty datatable_bindings
