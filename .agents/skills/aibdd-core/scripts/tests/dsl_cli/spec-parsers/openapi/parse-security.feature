Feature: OpenAPISpecParser extracts whether each operation requires auth

  Rule: 後置（狀態）- operation 自帶 security 區塊時，auth_required 為 true
    Example: setPassword 由 playerTokenAuth 保護
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
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part requires auth

  Rule: 後置（狀態）- operation 以 security: [] 顯式 opt-out 時，auth_required 為 false（即使 root 有 security）
    Example: health-check 端點明示無需 auth
      Given a temporary file at "contracts/health.api.yml" with content:
        """
        openapi: 3.0.0
        components:
          securitySchemes:
            playerTokenAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
        security:
          - playerTokenAuth: []
        paths:
          /health:
            get:
              operationId: healthCheck
              security: []
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part does not require auth

  Rule: 後置（狀態）- operation 無 security key 時，繼承 root-level security
    Example: getState 未自帶 security，沿用 root 的 playerTokenAuth → auth_required 為 true
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        components:
          securitySchemes:
            playerTokenAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
        security:
          - playerTokenAuth: []
        paths:
          /games/{gameId}/state:
            get:
              operationId: getState
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part requires auth

  Rule: 後置（狀態）- 處處皆無 security 時，auth_required 為 false
    Example: 公開端點
      Given a temporary file at "contracts/health.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /health:
            get:
              operationId: healthCheck
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part does not require auth
