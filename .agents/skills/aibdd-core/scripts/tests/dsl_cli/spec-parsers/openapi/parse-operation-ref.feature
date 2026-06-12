Feature: OpenAPISpecParser resolves operations behind an operation-level $ref (L3-b)

  # 結構性拆檔：path 下某 method 的值是 $ref，指向別檔的單一 operation 物件（裸 operation 檔）。
  # operation 的 operationId / parameters / requestBody / responses / security 都應被解析；
  # anchor 落在 operation 真身所在檔（definition-site）。
  # 值由 prance resolved 提供（正確 ref target 下），本檔鎖定解析 + scope + anchor。

  Rule: 後置（狀態）- operation $ref 拆出的 operation 自帶 security，完整解析
    Example: setPassword 在 ops/set-password.yml，自帶 BearerAuth
      Given a temporary file at "contracts/ops/set-password.yml" with content:
        """
        operationId: setPassword
        security:
          - BearerAuth: []
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
        paths:
          /games/{gameId}/passwords:
            post:
              $ref: 'ops/set-password.yml'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 1 operation is returned
      And the operation "setPassword" requires auth
      And the operation "setPassword"'s target_part_path is "contracts/ops/set-password.yml#"
      And the operation "setPassword" request_input "gameId" has target_part_path "contracts/ops/set-password.yml#/parameters/0"
      And the operation "setPassword" request_input "password" has target_part_path "contracts/ops/set-password.yml#/requestBody/content/application~1json/schema/properties/password"

  Rule: 後置（狀態）- operation $ref 拆出的 operation 無 security、entry 亦無 root，判公開
    Example: 拆出的 listPublicGames 為公開端點
      Given a temporary file at "contracts/ops/list-public-games.yml" with content:
        """
        operationId: listPublicGames
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
        paths:
          /games/public:
            get:
              $ref: 'ops/list-public-games.yml'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 1 operation is returned
      And the operation "listPublicGames" does not require auth

  Rule: 後置（狀態）- operation $ref 拆出的 operation 無自帶 security 時，繼承 entry root scope
    Example: 拆出的 getState 無 security key，沿用 entry root 的 BearerAuth
      Given a temporary file at "contracts/ops/get-state.yml" with content:
        """
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
          /games/{gameId}/state:
            get:
              $ref: 'ops/get-state.yml'
        """
      When OpenAPISpecParser parses the last file
      Then exactly 1 operation is returned
      And the operation "getState" requires auth
