Feature: OpenAPISpecParser extracts the effective security schemes per operation

  # security_schemes 抽取規則（operation 覆寫 root）：
  # - operation 自帶 security: 區塊        → 取該區塊的 scheme 名
  # - operation security: []（顯式 opt-out） → 空（即使 root 有 security）
  # - operation 無 security key            → 繼承 root-level security
  # - 處處皆無                              → 空
  #
  # security_schemes 之後驅動 web-service preset 的 actor slot：
  # part_to_dsl 對 secured operation 多吐一個 UID datatable_binding，
  # dsl_to_isa 再把它路由成 (UID="$...") instruction 前綴。

  Rule: 後置（狀態）- operation 自帶 security 區塊時，security_schemes 取該區塊的 scheme 名
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
      Then the part's security_schemes is "playerTokenAuth"

  Rule: 後置（狀態）- operation 以 security: [] 顯式 opt-out 時，security_schemes 為空（即使 root 有 security）
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
      Then the part's security_schemes is empty

  Rule: 後置（狀態）- operation 無 security key 時，繼承 root-level security
    Example: getState 未自帶 security，沿用 root 的 playerTokenAuth
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
      Then the part's security_schemes is "playerTokenAuth"

  Rule: 後置（狀態）- 處處皆無 security 時，security_schemes 為空
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
      Then the part's security_schemes is empty
