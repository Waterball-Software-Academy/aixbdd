Feature: dsl_to_isa 對真實 isa.yml 風格的 response_validate（json + data_table 雙條、format 帶 regex 錨點）正確選用與渲染

  # 真實 backend/specs/contracts/isa.yml 對每個 instruction_type 提供兩種 data_format（data_table / json），
  # 且 format 是 Python re pattern——帶 `^...$` 錨點、`\(` `\)` 跳脫、`,?\s*` 等 regex 噪音，name 為人類描述字串。
  #
  # 兩個缺陷在此釘住：
  #   1) 選錯條：_instruction_format 只比對單一鍵且回傳第一個 match。handler 契約鍵是 instruction_type
  #      （response_validate），非 name；且雙條同 instruction_type 時須用 data_format 消歧。
  #   2) 渲染殘留 regex：rendered instruction 不該保留 `^` `$` 錨點、`\(`→`(`、`,?\s*`→`, ` 等。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: Response validation (JSON)
          instruction_type: response_validate
          format: ^(?P<summary>.+?)\((?P<status_code>\d{3})\)回應為,?\s*with JSON:$
          data_format: json
        - name: Response validation (DataTable)
          instruction_type: response_validate
          format: ^(?P<summary>.+?)\((?P<status_code>\d{3})\)回應,?\s*with table:$
          data_format: data_table
      """

  Rule: 後置（斷言）- status-only handler 選 data_table variant（即使 json 排前面），且渲染無 regex 錨點/跳脫殘留
    Example: 200 回應——instruction 應為乾淨人類語句、以 "回應, with table:" 結尾，無 `^` `$` `\(` `\)`
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games/{gameId}/passwords:
            post:
              summary: 玩家設置個人密碼
              responses:
                '200':
                  description: ok
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "設定密碼成功"
            name: games.set-password.response-200
            handler: operation-response-success-and-failure
            target_part_path: contracts/games.api.yml#/paths/~1games~1{gameId}~1passwords/post/responses/200
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.set-password.response-200" has isa_steps[0].instruction equal to "玩家設置個人密碼(200)回應, with table:"
      And dsl step "games.set-password.response-200" has isa_steps[0].table length 0

  Rule: 後置（斷言）- readmodel handler 同樣選 data_table variant，table 帶 body fields，渲染無 regex 殘留
    Example: 開房回 roomNo 一個 read-model field——instruction 乾淨且 table 帶欄位
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /rooms:
            post:
              summary: 開房
              responses:
                '200':
                  description: ok
                  content:
                    application/json:
                      schema:
                        properties:
                          roomNo: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "開房成功並回傳房號 {房號}"
            name: rooms.create.response-readmodel
            handler: operation-response-success-readmodel
            target_part_path: contracts/games.api.yml#/paths/~1rooms/post/responses/200/content/application~1json/schema
            param_bindings: {}
            datatable_bindings:
              房號: { target: "response:$.roomNo" }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.create.response-readmodel" has isa_steps[0].instruction equal to "開房(200)回應, with table:"
      And dsl step "rooms.create.response-readmodel" has isa_steps[0].table equal to:
        """
        roomNo: "{{房號}}"
        """
