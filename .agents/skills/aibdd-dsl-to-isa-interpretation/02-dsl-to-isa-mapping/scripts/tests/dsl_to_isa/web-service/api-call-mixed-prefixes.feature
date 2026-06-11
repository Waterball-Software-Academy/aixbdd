Feature: dsl_to_isa simultaneously emits P:, H:, Q: prefixes and body fields in a single api_call table

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # 本檔覆蓋 path / header / query 三種前綴同時出現的整合 case，補上單檔分測之外的橫向組合保證。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """

  Rule: 後置（狀態）- path / header / query 三種參數同時出現時，table 同時帶 P: / H: / Q: 三種前綴鍵，且 body 必填項以原欄名入 table
    Example: 查詢遊戲列表的 operation 同時帶 path `tenantId` + header `X-Request-Id` + query `page` + body `filter`
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /tenants/{tenantId}/games:
            post:
              summary: 查詢租戶遊戲列表
              parameters:
                - in: path
                  name: tenantId
                  required: true
                  schema: { type: string }
                - in: header
                  name: X-Request-Id
                  required: true
                  schema: { type: string }
                - in: query
                  name: page
                  required: true
                  schema: { type: integer }
              requestBody:
                content:
                  application/json:
                    schema:
                      required: [filter]
                      properties:
                        filter: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "查詢租戶 {租戶ID} 的遊戲第 {頁碼} 頁，過濾條件 {過濾條件}"
            name: games.search
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1tenants~1{tenantId}~1games/post
            param_bindings:
              租戶ID:
                target: contracts/games.api.yml#/paths/~1tenants~1{tenantId}~1games/post/parameters/0
              請求識別碼:
                target: contracts/games.api.yml#/paths/~1tenants~1{tenantId}~1games/post/parameters/1
              頁碼:
                target: contracts/games.api.yml#/paths/~1tenants~1{tenantId}~1games/post/parameters/2
            datatable_bindings:
              過濾條件: { target: contracts/games.api.yml#/paths/~1tenants~1{tenantId}~1games/post/requestBody/content/application~1json/schema/properties/filter }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.search" has params keys ["過濾條件"] in order
      And dsl step "games.search" has isa_steps[0].instruction equal to "(No Actor) 查詢租戶遊戲列表, call table:"
      And dsl step "games.search" has isa_steps[0].table equal to:
        """
        "P:tenantId": "{{租戶ID}}"
        "H:X-Request-Id": "{{請求識別碼}}"
        "Q:page": "{{頁碼}}"
        filter: "{{過濾條件}}"
        """
