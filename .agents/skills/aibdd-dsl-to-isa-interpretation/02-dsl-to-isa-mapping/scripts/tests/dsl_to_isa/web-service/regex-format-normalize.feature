Feature: dsl_to_isa 將 isa.yml 的 regex format 正規化為乾淨 instruction（剝錨點/跳脫/regex 噪音），且正規化結果仍能被原 format 重新匹配

  # isa.yml 的 format 是 Python re pattern（真實檔帶 `^...$` 錨點、`\(` `\)` 跳脫、`,?\s*` 等）。
  # 翻譯產出的 isa step instruction 必須是乾淨人類語句、不得殘留 regex 語法；
  # 同時必須仍是「能被來源 format 成功 match 的正規化形式」（re-match invariant）。
  #
  # 本檔專測正規化規則本身（與 data_format 選擇解耦），逐條釘住：
  #   - 頭尾 `^` `$` 錨點剝除
  #   - `\(` `\)` 等跳脫字元還原
  #   - `\s*` / `\s+` 收斂為單一空白
  #   - 標點後的可選量詞 `,?` 去除 `?`

  Background:
    Given a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      rooms: rooms
      """

  Rule: 後置（狀態）- 頭尾 `^` `$` 錨點不得殘留於 instruction（time_control 單一 slot 最小例）
    Example: 真實 isa.yml time_control format 帶 `^...$`——instruction 應為 '現在時間為 "{{時間}}"'，無錨點
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: Time control
            instruction_type: time_control
            format: ^現在時間為 "(?P<time>[^"]+)"$
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "凍結時間 {時間}"
            name: time.freeze
            handler: time-control
            target_part_path: ""
            param_bindings:
              時間: { target: "@time" }
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "time.freeze" has isa_steps[0].instruction equal to '現在時間為 "{{時間}}"'
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format

  Rule: 後置（狀態）- `^` `$` 錨點 + 尾段標點同時正規化（entity_setup 真實 format）
    Example: format 帶 `^準備一個(...)，, with table:$`——instruction 結尾乾淨、無 `^` `$`
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: Data preparation
            instruction_type: entity_setup
            format: ^準備一個(?P<entity>[一-鿿a-zA-Z0-9_]+), with table:$
            data_format: data_table
        """
      And a temporary file at "data/domain.dbml" with content:
        """
        Table rooms {
          id        integer    [pk]
          room_code varchar(4) [not null]
        }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在房間"
            name: rooms.state-builder
            handler: state-builder
            target_part_path: data/domain.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              房號: { target: data/domain.dbml#rooms.room_code }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.state-builder" has isa_steps[0].instruction equal to "準備一個rooms, with table:"
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format

  Rule: 後置（API 呼叫）- actor alternation `\((?:No Actor|...|UID="(?P<userId>...)")\)` 渲染為 `(No Actor)` 或 `(UID="{{key}}")`，不殘留 regex 交替語法
    Example: format 帶 `\((?:No Actor|UID=""|UID="(?P<userId>...)")\)`——無 actor 時 instruction 為 '(No Actor) 設置密碼, call table:'
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: api_call
            instruction_type: action
            format: '^\((?:No Actor|UID=""|UID="(?P<userId>\$[<>\w.]+)")\) (?P<summary>.+?), call table:$'
            data_format: data_table
        """
      And a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /passwords:
            post:
              summary: 設置密碼
              requestBody:
                content:
                  application/json:
                    schema:
                      properties:
                        password: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "設置密碼 {密碼}"
            name: set-password
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1passwords/post
            param_bindings: {}
            datatable_bindings:
              密碼:
                target: contracts/games.api.yml#/paths/~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "set-password" has isa_steps[0].instruction equal to "(No Actor) 設置密碼, call table:"
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format

    Example: format 帶 `\((?:No Actor|UID=""|UID="(?P<userId>...)")\)`——有 actor binding 時 instruction 為 '(UID="{{玩家}}") 設置密碼, call table:'
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: api_call
            instruction_type: action
            format: '^\((?:No Actor|UID=""|UID="(?P<userId>\$[<>\w.]+)")\) (?P<summary>.+?), call table:$'
            data_format: data_table
        """
      And a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        components:
          securitySchemes:
            playerAuth:
              type: http
              scheme: bearer
        paths:
          /passwords:
            post:
              summary: 設置密碼
              security:
                - playerAuth: []
              requestBody:
                content:
                  application/json:
                    schema:
                      properties:
                        password: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "設置密碼 {密碼}"
            name: set-password
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1passwords/post
            param_bindings:
              玩家:
                target: literal:actor-key
            datatable_bindings:
              密碼:
                target: contracts/games.api.yml#/paths/~1passwords/post/requestBody/content/application~1json/schema/properties/password
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "set-password" has isa_steps[0].instruction equal to '(UID="{{玩家}}") 設置密碼, call table:'

  Rule: 後置（斷言）- `\(` `\)` 跳脫還原 + `,?\s*` regex 噪音收斂為 ", "（response_validate 真實 format）
    Example: format 帶 `\(` `\)` `,?\s*`——instruction 為 "開房(200)回應, with table:"，且能 re-match 來源
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: Response validation (DataTable)
            instruction_type: response_validate
            format: ^(?P<summary>.+?)\((?P<status_code>\d{3})\)回應,?\s*with table:$
            data_format: data_table
        """
      And a temporary file at "contracts/games.api.yml" with content:
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
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format
