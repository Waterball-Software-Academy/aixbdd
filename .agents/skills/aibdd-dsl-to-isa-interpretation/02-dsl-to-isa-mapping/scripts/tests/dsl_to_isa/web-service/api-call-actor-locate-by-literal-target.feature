Feature: dsl_to_isa 以 param_binding 的 target `literal:actor-key` 定位 actor，不再以 datatable securitySchemes 定位

  # 取代舊規則（actor = datatable_binding 且 target 含 /components/securitySchemes/）。
  #
  # 新 part_to_dsl 對 secured operation 的 operation-invoke 產出保留 actor slot 的方式改為：
  #   param_bindings:
  #     <actor-key>:
  #       target: literal:actor-key
  # 其中 <actor-key> 預設由 preset emit 為 "actor"，但 dsl_to_isa 的判定與 key 名稱無關 ——
  # 認定 actor 的唯一依據是 binding 的 target 字面等於 `literal:actor-key`。
  #
  # 新規則（locator = param_binding target == literal:actor-key）：
  #   1. actor binding 由 param_bindings 中 target == `literal:actor-key` 認定，與 key 名稱無關。
  #   2. actor 不進 params（該 binding 無 default_value，actor 真實值由下游 .feature DataTable / SOP 提供）。
  #   3. actor 不進 call table（actor 不是 request 欄位）。
  #   4. instruction actor 前綴 emit `(UID="{{<該 binding 的 key>}}")` —— 引用動態 key；
  #      slot 關鍵字 `UID` 為 ISA api_call 文法 token（固定），佔位引用實際 binding key。
  #
  # 反向：key 名稱即使叫 "actor"，只要 target 不是 `literal:actor-key`（指向 request 欄位），
  # 就不被當 actor —— 證明 locator 已從 securitySchemes / key 名稱切換為 target == literal:actor-key。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 前置（狀態）- actor binding 由 param_binding target == literal:actor-key 認定，preset 預設 key "actor"
    Example: key 為 actor、target literal:actor-key → 不進 params、不進 table、prefix (UID="{{actor}}")
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
              actor:
                target: literal:actor-key
            datatable_bindings:
              密碼:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["密碼"] in order
      And dsl step "games.set-password" has isa_steps[0].instruction equal to '(UID="{{actor}}") 玩家設置個人密碼, call table:'
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        password: "{{密碼}}"
        """

  Rule: 前置（狀態）- locator 與 key 名稱無關，前綴佔位符引用該 binding 的動態 key
    Example: key 為 操作者、target literal:actor-key → 仍認定為 actor、prefix (UID="{{操作者}}")
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
              操作者:
                target: literal:actor-key
            datatable_bindings:
              密碼:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["密碼"] in order
      And dsl step "games.set-password" has isa_steps[0].instruction equal to '(UID="{{操作者}}") 玩家設置個人密碼, call table:'
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        password: "{{密碼}}"
        """

  Rule: 後置（狀態）- key 名稱即使叫 "actor"，target 非 literal:actor-key（指 body 欄位）時不被當 actor
    Example: 未受保護 operation、param_binding key 為 actor 但 target 指 body 欄位 note → 留在 table、prefix (No Actor)
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
          - format: "建立對局 備註 {actor}"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings:
              actor:
                target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/note
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.create" has empty params list
      And dsl step "games.create" has isa_steps[0].instruction equal to "(No Actor) 建立對局, call table:"
      And dsl step "games.create" has isa_steps[0].table equal to:
        """
        note: "{{actor}}"
        """
