Feature: dsl_to_isa renders instruction text from isa.yml formats

  # Translator 不應 hard-code ISA instruction 的自然語言 literal。
  # Handler table 仍決定 handler -> instruction name；實際 instruction 文字必須從
  # contracts/isa.yml 對應 instruction.format 取出，並以 named capture group
  # （例如 entity / time）作為 slot 判定與代入點。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: entity_setup
          instruction_type: state
          format: '建立資料列 for (?P<entity>\S+), table follows:'
          data_format: table
        - name: entity_validate
          instruction_type: state
          format: '確認資料列 exists in (?P<entity>\S+), table follows:'
          data_format: table
        - name: api_call
          instruction_type: action
          format: 'invoke actor (?P<actor>No Actor|UID="\$\S+") summary (?P<summary>.+), payload:'
          data_format: table
        - name: response_validate
          instruction_type: assertion
          format: 'response summary (?P<summary>.+) status (?P<status_code>\d{3}), payload:'
          data_format: table
        - name: time_control
          instruction_type: control
          format: 'time is frozen at "(?P<time>[^"]+)"'
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      rooms: rooms
      games: games
      """

  Rule: 後置（狀態）- entity_setup / entity_validate 的 instruction literal 由 isa.yml format 決定，entity group 是代入點
    Example: state-builder 使用 isa.yml 的 entity_setup format，而不是寫死「準備一個...」
      Given a temporary file at "specs/p1/dsl.yml" with content:
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
      Then dsl step "rooms.state-builder" has isa_steps[0].instruction equal to "建立資料列 for rooms, table follows:"

    Example: state-verifier 使用 isa.yml 的 entity_validate format，而不是寫死「應該存在一個...」
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "驗證遊戲"
            name: games.state-verifier
            handler: state-verifier
            target_part_path: data/domain.dbml#games
            param_bindings: {}
            datatable_bindings:
              階段: { target: data/domain.dbml#games.phase }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.state-verifier" has isa_steps[0].instruction equal to "確認資料列 exists in games, table follows:"

  Rule: 後置（動作）- api_call 的 instruction literal 由 isa.yml format 決定，actor / summary group 是代入點
    Example: operation-invoke 使用 isa.yml 的 api_call format，而不是寫死「(... ) <summary>, call table:」
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games:
            post:
              summary: 建立遊戲
              requestBody:
                content:
                  application/json:
                    schema:
                      properties:
                        name: { type: string }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "建立遊戲 {名稱}"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings: {}
            datatable_bindings:
              名稱: { target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/name }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.create" has isa_steps[0].instruction equal to "invoke actor No Actor summary 建立遊戲, payload:"

  Rule: 後置（斷言）- response_validate 的 instruction literal 由 isa.yml format 決定，summary / status_code group 是代入點
    Example: operation-response-success-and-failure 使用 isa.yml 的 response_validate format，而不是寫死「<summary>(<status>)回應, with table:」
      Given a temporary file at "contracts/games.api.yml" with content:
        """
        openapi: 3.0.0
        paths:
          /games:
            post:
              summary: 建立遊戲
              responses:
                '201':
                  description: created
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "建立遊戲成功"
            name: games.create.response-201
            handler: operation-response-success-and-failure
            target_part_path: contracts/games.api.yml#/paths/~1games/post/responses/201
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.create.response-201" has isa_steps[0].instruction equal to "response summary 建立遊戲 status 201, payload:"

  Rule: 後置（狀態）- time_control 的 instruction literal 由 isa.yml format 決定，time group 是代入點
    Example: time-control 使用 isa.yml 的 time_control format，而不是寫死「現在時間為...」
      Given a temporary file at "specs/p1/dsl.yml" with content:
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
      Then dsl step "time.freeze" has isa_steps[0].instruction equal to 'time is frozen at "{{時間}}"'
