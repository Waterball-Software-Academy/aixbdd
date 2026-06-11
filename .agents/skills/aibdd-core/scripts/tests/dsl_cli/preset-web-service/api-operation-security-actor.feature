Feature: web-service plugin emits an actor parameter slot for secured operations

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

  Rule: 後置（狀態）- secured operation 的 invoke template 多一條 actor param_binding
    Example: setPassword（playerTokenAuth 保護）→ actor param_binding、target 為 literal:actor-key
      Then template "setPassword.operation-invoke" param_binding "actor" has target "literal:actor-key"

  Rule: 後置（狀態）- 未受保護的 operation 不得有 actor param_binding
    Example: healthCheck（無 security）→ invoke template 無 actor
      Then template "healthCheck.operation-invoke" has no param_binding "actor"
