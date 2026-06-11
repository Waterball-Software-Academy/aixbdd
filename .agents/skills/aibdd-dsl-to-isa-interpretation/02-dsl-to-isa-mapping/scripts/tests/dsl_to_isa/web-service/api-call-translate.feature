Feature: dsl_to_isa translates operation-invoke into api_call, prefixing path parameters with P:

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 後置（狀態）- operation-invoke 翻成 api_call，path param 以 `P:<name>` 入 table
    Example: setPassword 操作含 path param `gameId` + body required [player_id, password]
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games/{gameId}/passwords:
            post:
              summary: 玩家設置個人密碼
              parameters:
                - in: path
                  name: gameId
                  required: true
                  schema: { type: string }
              requestBody:
                content:
                  application/json:
                    schema:
                      required: [player_id, password]
                      properties:
                        player_id: { type: string }
                        password: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "玩家在遊戲 {遊戲ID} 設置個人密碼"
            name: games.set-password
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post
            param_bindings:
              遊戲ID:
                target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/parameters/0
            datatable_bindings:
              玩家: { target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/player_id }
              密碼: { target: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/requestBody/content/application~1json/schema/properties/password }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password" has params keys ["玩家", "密碼"] in order
      And dsl step "games.set-password" has isa_steps[0].instruction equal to "(No Actor) 玩家設置個人密碼, call table:"
      And dsl step "games.set-password" has isa_steps[0].table equal to:
        """
        "P:gameId": "{{遊戲ID}}"
        player_id: "{{玩家}}"
        password: "{{密碼}}"
        """
