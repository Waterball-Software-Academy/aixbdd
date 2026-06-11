Feature: dsl_to_isa emits (<FILL IN>) actor sentinel when an operation has a security: block

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  #
  # actor 機制過渡期做法（pending SOP §5.3.1 啟用設計）：
  # - operation 無 `security:` 區塊（或顯式 `security: []` opt-out）→ 走其他 api-call-*.feature 的 `(No Actor)` 路徑
  # - operation 有 `security:` 區塊 → translator 一律 emit `(<FILL IN>)` sentinel
  #   actor 真實值（要填 `(No Actor)` 還是 `UID="$..."`、$xxx 取自哪個 binding）
  #   由下游 AI / SOP 階段處理，不在 translator 範圍。
  #
  # 因 `(<FILL IN>)` 不符合 isa.yml 中 api_call format regex，
  # regex-rematch-assertion.feature 對「帶 security」的 step 預設不涵蓋；
  # 等下游補完才進入 re-match 範圍（同 datatable default_value 的 `<FILL IN>` 慣例）。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 後置（狀態）- operation 帶 security: 區塊時，instruction prefix 以 (<FILL IN>) sentinel 取代 actor；其餘 table 內容照常產出
    Example: setPassword 由 playerTokenAuth scheme 保護 — translator 不嘗試自行判定 actor 來源
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        components:
          securitySchemes:
            playerTokenAuth:
              type: apiKey
              in: header
              name: X-Player-Token
        paths:
          /games/{gameId}/passwords:
            post:
              summary: 玩家設置個人密碼
              security:
                - playerTokenAuth: []
              parameters:
                - in: path
                  name: gameId
                  required: true
                  schema: { type: string }
              requestBody:
                content:
                  application/json:
                    schema:
                      required: [password]
                      properties:
                        password: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "在遊戲 {遊戲ID} 設置個人密碼 {密碼}"
            name: games.set-password
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post
            param_bindings:
              遊戲ID:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/parameters/0
            datatable_bindings:
              密碼: { target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["密碼"] in order
      And dsl step "games.set-password" has isa_steps[0].instruction equal to "(<FILL IN>) 玩家設置個人密碼, call table:"
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        password: "{{密碼}}"
        """

  Rule: 後置（狀態）- operation 以 `security: []` 顯式 opt-out 時，回到 (No Actor) 路徑（與其他 api-call-*.feature 一致）
    Example: health-check 端點明示無需 auth
      Given a temporary file at "contracts/health.api.yml" with content:
        """
        openapi: 3.0.0
        components:
          securitySchemes:
            playerTokenAuth:
              type: apiKey
              in: header
              name: X-Player-Token
        security:
          - playerTokenAuth: []
        paths:
          /health:
            get:
              summary: 健康檢查
              security: []
              responses:
                '200':
                  description: ok
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "呼叫健康檢查"
            name: health.check
            handler: operation-invoke
            target_part_path: contracts/health.api.yml#/paths/~1health/get
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "health.check" has isa_steps[0].instruction equal to "(No Actor) 健康檢查, call table:"
