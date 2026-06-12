Feature: OpenAPISpecParser merges path-item-level shared parameters into each operation

  Rule: 後置（狀態）- path-item 級共用 parameter 併入 operation 的 request_inputs
    Example: getState 取得 path-level 宣告的 gameId
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Games API
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            parameters:
              - name: gameId
                in: path
                required: true
                schema:
                  type: string
            get:
              operationId: getState
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name   | source | required |
        | gameId | path   | true     |
      And the request_input named "gameId" has target_part_path "contracts/games.api.yml#/paths/~1games~1{gameId}~1state/parameters/0"

  Rule: 後置（狀態）- path-level 與 operation-level parameter 並存時兩者皆收
    Example: gameId（path-level）與 verbose（operation-level）並列
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Games API
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            parameters:
              - name: gameId
                in: path
                required: true
                schema:
                  type: string
            get:
              operationId: getState
              parameters:
                - name: verbose
                  in: query
                  required: false
                  schema:
                    type: boolean
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name    | source | required |
        | gameId  | path   | true     |
        | verbose | query  | false    |

  Rule: 後置（狀態）- 同 (name, in) 的 operation-level parameter 覆寫 path-level
    Example: path-level gameId required true 被 operation-level gameId required false 覆寫
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Games API
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            parameters:
              - name: gameId
                in: path
                required: true
                schema:
                  type: string
            get:
              operationId: getState
              parameters:
                - name: gameId
                  in: path
                  required: false
                  schema:
                    type: string
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name   | source | required |
        | gameId | path   | false    |

  Rule: 後置（狀態）- path-level parameter 以 $ref 拆檔時仍收齊，anchor 落 definition-site
    Example: gameId 由 params.yml 引入
      Given a temporary file at "contracts/params.yml" with content:
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
      And a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        info:
          title: Games API
          version: 1.0.0
        paths:
          /games/{gameId}/state:
            parameters:
              - $ref: 'params.yml#/components/parameters/GameId'
            get:
              operationId: getState
              responses:
                '200':
                  description: OK
        """
      When OpenAPISpecParser parses the last file
      Then the part's request_inputs has entries:
        | name   | source | required |
        | gameId | path   | true     |
      And the request_input named "gameId" has target_part_path "contracts/params.yml#/components/parameters/GameId"
