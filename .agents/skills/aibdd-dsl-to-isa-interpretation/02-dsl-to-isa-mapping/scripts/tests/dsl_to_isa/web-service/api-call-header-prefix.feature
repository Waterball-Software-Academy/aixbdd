Feature: dsl_to_isa prefixes OpenAPI header parameters with H: in the api_call table

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

  Rule: 後置（狀態）- header 參數同理以 `H:<name>` 為 key 入 table
    Example: 帶 `X-Request-Id` header 必填項的 operation
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games:
            post:
              summary: 建立遊戲
              parameters:
                - in: header
                  name: X-Request-Id
                  required: true
                  schema: { type: string }
              requestBody:
                content:
                  application/json:
                    schema:
                      required: [name]
                      properties:
                        name: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "建立遊戲"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings:
              請求識別碼:
                target: contracts/games.api.yml#/paths/~1games/post/parameters/0
            datatable_bindings:
              名稱: { target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/name }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.create" has params keys ["名稱"] in order
      And dsl step "games.create" has isa_steps[0].table key "H:X-Request-Id" with value "{{請求識別碼}}"
