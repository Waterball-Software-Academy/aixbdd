Feature: dsl_to_isa 以 securitySchemes target 定位保留 actor binding，不再以字面 key "UID" 定位

  # 承接 api-call-security-actor-resolve.feature 的 path B（actor 進 params + {{...}} 佔位 + 不進 table），
  # 但把「哪個 binding 是 actor」的判定從『字面 key == "UID"』改成『binding 的 target 指向
  # /components/securitySchemes/ 節點』。
  #
  # 理由：part_to_dsl 對 secured operation 產出的保留 actor binding，其 DSL key 不保證叫 "UID"
  # （可能是 玩家 / player / 操作者 …）。舊版以字面 key "UID" 去 pop，遇到非 "UID" 命名的 actor
  # binding 會漏抓 → 該 binding 殘留在 call table（污染 request body），prefix 退回 (<FILL IN>)。
  #
  # 新規則（locator = target securitySchemes）：
  #   1. actor binding 由 target 含 `/components/securitySchemes/` 認定，與 key 名稱無關。
  #   2. 命中者從 datatable_bindings pop 出 → 不進 call table（actor 不是 request 欄位）。
  #   3. 進 params（帶其 default_value）→ 可被 .feature DataTable 覆蓋。
  #   4. instruction actor 前綴 emit `(UID="{{<該 binding 的 key>}}")`；
  #      slot 關鍵字 `UID` 為 ISA api_call 文法 token（固定），佔位引用實際 binding key。
  #
  # 反向：字面叫 "UID" 但 target 不是 securitySchemes（指向 request body 欄位）的 binding
  # 不再被當 actor — 證明 locator 已從 key 名稱切換為 target。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 前置（狀態）- actor binding 以 target securitySchemes 認定，即使 key 不叫 "UID"
    Example: binding key 為 玩家、target 指 playerTokenAuth scheme → 進 params、不進 table、prefix (UID="{{玩家}}")
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
              玩家:
                required: false
                target: contracts/games.api.yml#/components/securitySchemes/playerTokenAuth
                default_value: "$玩家A"
              密碼:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["密碼", "玩家"] in order
      And dsl step "games.set-password" has params equal to:
        """
        密碼:
        玩家: "$玩家A"
        """
      And dsl step "games.set-password" has isa_steps[0].instruction equal to '(UID="{{玩家}}") 玩家設置個人密碼, call table:'
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        password: "{{密碼}}"
        """

  Rule: 前置（狀態）- default_value 仍為 <FILL IN> 時，一樣以 target 定位、進 params、前綴仍 emit {{key}} 佔位（值差異只在 param default）
    Example: 玩家 default 未填 → params 為 {密碼: null, 玩家: "<FILL IN>"}；instruction 模板不變；table 同樣不含 玩家
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
              玩家:
                required: false
                target: contracts/games.api.yml#/components/securitySchemes/playerTokenAuth
                default_value: "<FILL IN>"
              密碼:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["密碼", "玩家"] in order
      And dsl step "games.set-password" has params equal to:
        """
        密碼:
        玩家: "<FILL IN>"
        """
      And dsl step "games.set-password" has isa_steps[0].instruction equal to '(UID="{{玩家}}") 玩家設置個人密碼, call table:'
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        password: "{{密碼}}"
        """

  Rule: 後置（狀態）- 字面 key "UID" 但 target 非 securitySchemes（指向 body 欄位）時，不再被當 actor
    Example: 未受保護 operation、binding key 為 UID 但 target 指 body 欄位 note → 留在 table、prefix (No Actor)
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games:
            post:
              summary: 建立對局
              requestBody:
                content:
                  application/json:
                    schema:
                      properties:
                        note: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "建立對局 備註 {UID}"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings: {}
            datatable_bindings:
              UID:
                target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/note
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.create" has params keys ["UID"] in order
      And dsl step "games.create" has isa_steps[0].instruction equal to "(No Actor) 建立對局, call table:"
      And dsl step "games.create" has isa_steps[0].table equal to:
        """
        note: "{{UID}}"
        """
