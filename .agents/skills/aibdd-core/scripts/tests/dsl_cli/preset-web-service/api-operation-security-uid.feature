Feature: web-service plugin emits a UID actor slot for secured operations

  # secured operation（part.security_schemes 非空）→ invoke template 多一條 UID datatable_binding：
  #   - required: false
  #   - default_value: "<FILL IN>"  （待 SBE/planner 填入真實身分變數，如 $玩家A）
  #   - target: 指向該 securityScheme 的 spec anchor（真 anchor、過 eval、語意＝身分源自此 scheme）
  # 未受保護的 operation 不得有 UID datatable_binding。
  # dsl_to_isa 之後把這個 UID 路由成 (UID="$...") instruction 前綴（見 dsl_to_isa 測試）。

  Background:
    Given a temporary file at "contracts/games.api.yml" with content:
      """
      openapi: 3.0.0
      components:
        securitySchemes:
          playerTokenAuth:
            type: http
            scheme: bearer
            bearerFormat: JWT
      paths:
        /games/{gameId}/passwords:
          post:
            operationId: setPassword
            security:
              - playerTokenAuth: []
            parameters:
              - name: gameId
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
                    required: [password]
                    properties:
                      password:
                        type: string
            responses:
              '200':
                description: OK
        /health:
          get:
            operationId: healthCheck
            responses:
              '200':
                description: OK
      """
    When OpenAPISpecParser parses the last file
    And the web-service plugin generates templates from the parsed parts

  Rule: 後置（狀態）- secured operation 的 invoke template 多一條 UID datatable_binding
    Example: setPassword（playerTokenAuth 保護）→ UID required false、default <FILL IN>、target 指向 securityScheme anchor
      Then template "setPassword.operation-invoke" datatable_binding "UID" has required false
      And template "setPassword.operation-invoke" datatable_binding "UID" has default_value "<FILL IN>"
      And template "setPassword.operation-invoke" datatable_binding "UID" has target "contracts/games.api.yml#/components/securitySchemes/playerTokenAuth"

  Rule: 後置（狀態）- 未受保護的 operation 不得有 UID datatable_binding
    Example: healthCheck（無 security）→ invoke template 無 UID
      Then template "healthCheck.operation-invoke" has no datatable_binding "UID"
