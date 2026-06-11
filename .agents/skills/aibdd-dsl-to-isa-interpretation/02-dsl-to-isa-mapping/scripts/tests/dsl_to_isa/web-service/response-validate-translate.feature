Feature: dsl_to_isa translates operation-response-success-and-failure into response_validate (status-only, empty table)

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # 此 handler 僅斷言 status code，不檢查 body fields（handler doc 明文禁止）；body 斷言走 readmodel handler。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: response_validate
          instruction_type: assertion
          format: '(?P<summary>.+)\((?P<status_code>\d{3})\)回應, with table:'
          data_format: table
      """

  Rule: 後置（狀態）- operation-response-success-and-failure 翻成 response_validate；status_code 從 fragment `responses/{code}` 取，instruction 攜帶 summary + status_code，table 留空
    Example: 200 success response — 即使 schema 有 body properties，本 handler 也不入 table
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games/{gameId}/passwords:
            post:
              summary: 玩家設置個人密碼
              responses:
                '200':
                  description: ok
                  content:
                    application/json:
                      schema:
                        required: [ok]
                        properties:
                          ok: { type: boolean }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "設定密碼成功"
            name: games.set-password.response-200
            handler: operation-response-success-and-failure
            target_part_path: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/responses/200
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password.response-200" has params length 0
      And dsl step "games.set-password.response-200" has isa_steps[0].instruction equal to "玩家設置個人密碼(200)回應, with table:"
      And dsl step "games.set-password.response-200" has isa_steps[0].table length 0

  Rule: 後置（狀態）- 失敗狀態碼（4xx/5xx）同樣走 success-and-failure handler；status_code 從 fragment 直接取，table 仍留空（不入 error envelope 欄位）
    Example: 422 validation failed — 即使 response body 有 error envelope schema，本 handler 也不入 table
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games/{gameId}/passwords:
            post:
              summary: 玩家設置個人密碼
              responses:
                '422':
                  description: validation failed
                  content:
                    application/json:
                      schema:
                        required: [code, message]
                        properties:
                          code: { type: string }
                          message: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "設定密碼驗證失敗"
            name: games.set-password.response-422
            handler: operation-response-success-and-failure
            target_part_path: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/responses/422
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password.response-422" has params length 0
      And dsl step "games.set-password.response-422" has isa_steps[0].instruction equal to "玩家設置個人密碼(422)回應, with table:"
      And dsl step "games.set-password.response-422" has isa_steps[0].table length 0
