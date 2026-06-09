Feature: OpenAPISpecParser resolves auth scope across a heavily modular OpenAPI doc

  Background:
    Given a temporary file at "contracts/schemes.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Shared security schemes
        version: 1.0.0
      components:
        securitySchemes:
          playerTokenAuth:
            type: http
            scheme: bearer
            bearerFormat: JWT
      """
    And a temporary file at "contracts/params.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Shared parameters
        version: 1.0.0
      components:
        parameters:
          GameId:
            name: gameId
            in: path
            required: true
            schema:
              type: string
      """
    And a temporary file at "contracts/common.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Shared schemas
        version: 1.0.0
      components:
        schemas:
          GameState:
            type: object
            properties:
              status:
                type: string
              round:
                type: integer
          PasswordBody:
            type: object
            required: [password]
            properties:
              password:
                type: string
      """
    And a temporary file at "contracts/games.api.yml" with content:
      """
      openapi: 3.0.0
      info:
        title: Games API
        version: 1.0.0
      components:
        securitySchemes:
          playerTokenAuth:
            $ref: 'schemes.yml#/components/securitySchemes/playerTokenAuth'
      security:
        - playerTokenAuth: []
      paths:
        /games/{gameId}/state:
          get:
            operationId: getState
            parameters:
              - $ref: 'params.yml#/components/parameters/GameId'
            responses:
              '200':
                description: OK
                content:
                  application/json:
                    schema:
                      $ref: 'common.yml#/components/schemas/GameState'
        /games/{gameId}/passwords:
          post:
            operationId: setPassword
            security:
              - playerTokenAuth: []
            parameters:
              - $ref: 'params.yml#/components/parameters/GameId'
            requestBody:
              required: true
              content:
                application/json:
                  schema:
                    $ref: 'common.yml#/components/schemas/PasswordBody'
            responses:
              '200':
                description: OK
        /health:
          get:
            operationId: healthCheck
            security: []
            responses:
              '200':
                description: OK
                content:
                  application/json:
                    schema:
                      $ref: 'common.yml#/components/schemas/GameState'
      """
    When OpenAPISpecParser parses the last file

  Rule: 後置（狀態）- entry 的三個 inline operation 全被發現
    Example: getState / setPassword / healthCheck 三者皆產出 part
      Then exactly 3 operations are returned

  Rule: 後置（狀態）- operation 無 security key 時，繼承 root scope（scheme 在外部檔）
    Example: getState 沿用 root 的 playerTokenAuth → auth_required 為 true
      Then the operation "getState" requires auth

  Rule: 後置（狀態）- operation 自帶 security 引用外部 scheme → auth_required 為 true
    Example: setPassword 由外部 playerTokenAuth 保護
      Then the operation "setPassword" requires auth

  Rule: 後置（狀態）- operation 以 security: [] opt-out，覆寫 root scope → auth_required 為 false
    Example: healthCheck 明示無需 auth，即使 root 有 security
      Then the operation "healthCheck" does not require auth

  Rule: 後置（狀態）- 跨檔抽出的 parameter 仍收齊，anchor 落在 params.yml definition-site
    Example: getState 的 gameId 來自 params.yml
      Then the operation "getState" request_input "gameId" has target_part_path "contracts/params.yml#/components/parameters/GameId"

  Rule: 後置（狀態）- 跨檔抽出的 requestBody property 仍收齊，anchor 落在 common.yml definition-site
    Example: setPassword 的 password 來自 common.yml
      Then the operation "setPassword" request_input "password" has target_part_path "contracts/common.yml#/components/schemas/PasswordBody/properties/password"

  Rule: 後置（狀態）- 跨檔抽出的 response property 仍收齊，anchor 落在 common.yml definition-site
    Example: getState 的 200 response status 來自 common.yml
      Then the operation "getState" response_property "status" has target_part_path "contracts/common.yml#/components/schemas/GameState/properties/status"

  # --- 真實 production 形態：每個 slice 是獨立檔、各自被 parse ---
  # 對齊現行 aibdd-form-api-spec 產出（backend/specs/contracts/*.api.yml）：
  #   - 各 slice 自足；security 一律 per-operation（不靠 root global、不跨檔）
  #   - securityScheme 在該 slice 自己的 components 本地定義（不跨檔 $ref）
  #   - 公開 slice（如 account）整份無任何 security
  # 以下每個 Example 自帶 fixture + parse，模擬「逐檔獨立解析」。

  Rule: 後置（狀態）- 公開 slice（account 型）整份無 security，全部 operation 不需 auth
    Example: registerAccount / loginAccount 皆為公開端點
      Given a temporary file at "contracts/account.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Account API
          version: 1.0.0
        paths:
          /api/accounts/register:
            post:
              operationId: registerAccount
              responses:
                '201':
                  description: Created
          /api/accounts/login:
            post:
              operationId: loginAccount
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then exactly 2 operations are returned
      And the operation "registerAccount" does not require auth
      And the operation "loginAccount" does not require auth

  Rule: 後置（狀態）- 受保護 slice（room 型）per-operation security + 本地 scheme，全部 operation 需 auth
    Example: joinOrCreateRoom / getRoom / readyPlayer 皆由本地 BearerAuth 保護
      Given a temporary file at "contracts/room.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Room API
          version: 1.0.0
        paths:
          /api/rooms:
            post:
              operationId: joinOrCreateRoom
              security:
                - BearerAuth: []
              responses:
                '200':
                  description: OK
          /api/rooms/{roomId}:
            get:
              operationId: getRoom
              security:
                - BearerAuth: []
              responses:
                '200':
                  description: OK
          /api/rooms/{roomId}/ready:
            post:
              operationId: readyPlayer
              security:
                - BearerAuth: []
              responses:
                '200':
                  description: OK
        components:
          securitySchemes:
            BearerAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
        """
      When OpenAPISpecParser parses the last file
      Then exactly 3 operations are returned
      And the operation "joinOrCreateRoom" requires auth
      And the operation "getRoom" requires auth
      And the operation "readyPlayer" requires auth

  Rule: 後置（狀態）- 同一受保護 slice 內，公開 operation 與受保護 operation 混用各自判定正確
    Example: 受保護的 createGame 與公開的 listPublicGames 並存
      Given a temporary file at "contracts/game.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Game API
          version: 1.0.0
        paths:
          /api/games:
            post:
              operationId: createGame
              security:
                - BearerAuth: []
              responses:
                '201':
                  description: Created
          /api/games/public:
            get:
              operationId: listPublicGames
              responses:
                '200':
                  description: OK
        components:
          securitySchemes:
            BearerAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
        """
      When OpenAPISpecParser parses the last file
      Then exactly 2 operations are returned
      And the operation "createGame" requires auth
      And the operation "listPublicGames" does not require auth

  Rule: 後置（狀態）- 四種來源的 operation 混用，發現完整且 auth scope 各自正確
    Example: listGames / getState / setPassword / healthCheck 全混
      Given a temporary file at "contracts/schemes.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Schemes
          version: 1.0.0
        components:
          securitySchemes:
            TokenAuth:
              type: http
              scheme: bearer
              bearerFormat: JWT
        """
      And a temporary file at "contracts/routes.yml" with content:
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
      And a temporary file at "contracts/ops/set-password.yml" with content:
        """
        operationId: setPassword
        security:
          - TokenAuth: []
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
        """
      And a temporary file at "contracts/ops/health.yml" with content:
        """
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
            TokenAuth:
              $ref: 'schemes.yml#/components/securitySchemes/TokenAuth'
        security:
          - TokenAuth: []
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
          /games/{gameId}/passwords:
            post:
              $ref: 'ops/set-password.yml'
          /health:
            get:
              $ref: 'ops/health.yml'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 4 operations are returned
      And the operation "listGames" does not require auth
      And the operation "getState" requires auth
      And the operation "setPassword" requires auth
      And the operation "healthCheck" does not require auth
      And the operation "getState"'s target_part_path is "contracts/routes.yml#/paths/~1games~1{gameId}~1state/get"
      And the operation "setPassword"'s target_part_path is "contracts/ops/set-password.yml#"
      And the operation "healthCheck"'s target_part_path is "contracts/ops/health.yml#"
      And the operation "setPassword" request_input "password" has target_part_path "contracts/ops/set-password.yml#/requestBody/content/application~1json/schema/properties/password"
