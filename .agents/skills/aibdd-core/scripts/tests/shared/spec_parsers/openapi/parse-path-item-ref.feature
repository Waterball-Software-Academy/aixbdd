Feature: OpenAPISpecParser discovers operations behind a path-item $ref (L3-a)

  Rule: 後置（狀態）- path-item $ref 拆出的 operation 被發現並繼承 root security
    Example: getState 在 routes.yml，沿用 entry root 的 BearerAuth
      Given a temporary file at "contracts/routes.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Routes
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            get:
              operationId: getState
              parameters:
                - name: gameId
                  in: path
                  required: true
                  schema:
                    type: string
              responses:
                '200':
                  description: OK
                  content:
                    application/json:
                      schema:
                        type: object
                        properties:
                          status:
                            type: string
        """
      And a temporary file at "contracts/api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: API
          version: 1.0.0
        components:
          securitySchemes:
            BearerAuth:
              type: http
              scheme: bearer
        security:
          - BearerAuth: []
        paths:
          /games/{gameId}/state:
            $ref: 'routes.yml#/paths/~1games~1{gameId}~1state'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 1 operation is returned
      And the operation "getState" requires auth
      And the operation "getState"'s target_part_path is "contracts/routes.yml#/paths/~1games~1{gameId}~1state/get"
      And the operation "getState" request_input "gameId" has target_part_path "contracts/routes.yml#/paths/~1games~1{gameId}~1state/get/parameters/0"
      And the operation "getState" response_property "status" has target_part_path "contracts/routes.yml#/paths/~1games~1{gameId}~1state/get/responses/200/content/application~1json/schema/properties/status"

  Rule: 後置（狀態）- 拆出的 operation 自帶 security: [] 仍 opt-out，覆寫 root scope
    Example: 拆出的 healthCheck 明示無需 auth，即使 entry root 有 security
      Given a temporary file at "contracts/routes.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Routes
          version: 1.0.0
        paths:
          /health:
            get:
              operationId: healthCheck
              security: []
              responses:
                '200':
                  description: OK
        """
      And a temporary file at "contracts/api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: API
          version: 1.0.0
        components:
          securitySchemes:
            BearerAuth:
              type: http
              scheme: bearer
        security:
          - BearerAuth: []
        paths:
          /health:
            $ref: 'routes.yml#/paths/~1health'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 1 operation is returned
      And the operation "healthCheck" does not require auth

  Rule: 後置（狀態）- 同 entry 內聯 operation 與 path-item $ref 拆出 operation 混用，各自正確
    Example: 內聯 listGames（公開）與拆出 getState（繼承 root）並存
      Given a temporary file at "contracts/routes.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Routes
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            get:
              operationId: getState
              responses:
                '200':
                  description: OK
        """
      And a temporary file at "contracts/api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: API
          version: 1.0.0
        components:
          securitySchemes:
            BearerAuth:
              type: http
              scheme: bearer
        security:
          - BearerAuth: []
        paths:
          /games/public:
            get:
              operationId: listGames
              security: []
              responses:
                '200':
                  description: OK
          /games/{gameId}/state:
            $ref: 'routes.yml#/paths/~1games~1{gameId}~1state'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 2 operations are returned
      And the operation "listGames" does not require auth
      And the operation "getState" requires auth
      And the operation "getState"'s target_part_path is "contracts/routes.yml#/paths/~1games~1{gameId}~1state/get"
