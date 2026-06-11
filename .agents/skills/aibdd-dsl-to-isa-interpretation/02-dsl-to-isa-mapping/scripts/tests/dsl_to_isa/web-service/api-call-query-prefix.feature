Feature: dsl_to_isa prefixes OpenAPI query parameters with Q: in the api_call table

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

  Rule: 後置（狀態）- query 參數同理以 `Q:<name>` 為 key 入 table
    Example: 帶 `page` query 必填項的 list operation
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games:
            get:
              summary: 列出遊戲
              parameters:
                - in: query
                  name: page
                  required: true
                  schema: { type: integer }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "列出遊戲 第 {頁碼} 頁"
            name: games.list
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/get
            param_bindings:
              頁碼:
                target: contracts/games.api.yml#/paths/~1games/get/parameters/0
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.list" has params length 0
      And dsl step "games.list" has isa_steps[0].table key "Q:page" with value "{{頁碼}}"
