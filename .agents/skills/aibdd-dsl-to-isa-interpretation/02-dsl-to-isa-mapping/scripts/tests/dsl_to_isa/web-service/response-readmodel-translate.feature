Feature: dsl_to_isa translates operation-response-success-readmodel into response_validate (body-fields populated)

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # 此 handler 與 operation-response-success-and-failure 共用同一條 response_validate instruction，
  # 差別在 table 內容：readmodel 帶 body fields，success-and-failure 留空（status-only）。
  # 候選 target 用 `response:<json_path>` URI scheme（見 part_to_dsl.py:87）。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: response_validate
          instruction_type: assertion
          format: '(?P<summary>.+)\((?P<status_code>\d{3})\)回應, with table:'
          data_format: table
      """

  Rule: 後置（狀態）- operation-response-success-readmodel 翻成 response_validate，table 帶 body fields；status_code 仍從 schema 路徑反推
    Example: 開房成功並回傳 roomNo + status 兩個 read-model field
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /rooms:
            post:
              summary: 開房
              responses:
                '200':
                  description: ok
                  content:
                    application/json:
                      schema:
                        required: [roomNo, status]
                        properties:
                          roomNo: { type: string }
                          status: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "開房成功並回傳房號 {房號} 狀態 {狀態}"
            name: rooms.create.response-readmodel
            handler: operation-response-success-readmodel
            target_part_path: contracts/games.api.yml#/paths/~1rooms/post/responses/200/content/application~1json/schema
            param_bindings: {}
            datatable_bindings:
              房號: { target: "response:$.roomNo" }
              狀態: { target: "response:$.status" }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.create.response-readmodel" has params keys ["房號", "狀態"] in order
      And dsl step "rooms.create.response-readmodel" has isa_steps[0].instruction equal to "開房(200)回應, with table:"
      And dsl step "rooms.create.response-readmodel" has isa_steps[0].table equal to:
        """
        roomNo: "{{房號}}"
        status: "{{狀態}}"
        """

  Rule: 後置（狀態）- readmodel 的 param_bindings（inline read-model 欄位）折入 assertion table（不進 params）；datatable_bindings 同時進 table 與 params；否則 inline 斷言被靜默丟棄
    # backend enterRoom readmodel 真實案例：房間ID/座位/是否新房 寫在 format inline（param_bindings），
    # 房間代碼/玩家人數 走 datatable（datatable_bindings）。兩者皆 target response:$.field，
    # 都必須成為 assertion table row。先前 translator 只讀 datatable_bindings，inline 三欄被丟失。
    # 但 params 只反映 datatable_bindings：inline 欄位入 table 不入 params。
    Example: param_bindings 兩個 inline 欄位入 table（不入 params）+ datatable 兩個欄位入 table 與 params；table 四欄（inline 先，datatable 後），params 只列 datatable 兩欄
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /rooms:
            post:
              summary: 開房
              responses:
                '200':
                  description: ok
                  content:
                    application/json:
                      schema:
                        required: [roomId, slot, isNewRoom, roomCode, playerCount]
                        properties:
                          roomId: { type: string }
                          slot: { type: integer }
                          isNewRoom: { type: boolean }
                          roomCode: { type: string }
                          playerCount: { type: integer }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "進入房間成功 房間ID={房間ID} 座位={座位} 是否新房={是否新房}"
            name: enterRoom.response-readmodel
            handler: operation-response-success-readmodel
            target_part_path: contracts/games.api.yml#/paths/~1rooms/post/responses/200/content/application~1json/schema
            param_bindings:
              房間ID: { target: "response:$.roomId" }
              座位: { target: "response:$.slot" }
              是否新房: { target: "response:$.isNewRoom" }
            datatable_bindings:
              房間代碼: { target: "response:$.roomCode" }
              玩家人數: { target: "response:$.playerCount" }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "enterRoom.response-readmodel" has params keys ["房間代碼", "玩家人數"] in order
      And dsl step "enterRoom.response-readmodel" has isa_steps[0].instruction equal to "開房(200)回應, with table:"
      And dsl step "enterRoom.response-readmodel" has isa_steps[0].table equal to:
        """
        roomId: "{{房間ID}}"
        slot: "{{座位}}"
        isNewRoom: "{{是否新房}}"
        roomCode: "{{房間代碼}}"
        playerCount: "{{玩家人數}}"
        """
