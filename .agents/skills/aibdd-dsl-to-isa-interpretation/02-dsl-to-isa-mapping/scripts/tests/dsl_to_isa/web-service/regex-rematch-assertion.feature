Feature: dsl_to_isa asserts every translated instruction re-matches its source isa.yml format regex (FILL-IN sentinels excluded)

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # 翻譯結果含 (<FILL IN>) sentinel 之 step（如 api-call-security-placeholder.feature 涵蓋的
  # secured operation case）不在 re-match 範圍 — 屬於未完成中間態，待下游 AI/SOP 補正後才進入
  # re-match 範圍（同 datatable default_value 的 `<FILL IN>` 慣例）。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: entity_setup
          instruction_type: state
          format: '準備一個(?P<entity>\S+), with table:'
          data_format: table
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      rooms: rooms
      """

  Rule: 後置（回應）- 翻譯後的 instruction（排除 FILL-IN sentinel step）必須能被原 isa.yml 對應 format regex 重新匹配
    Example: 翻譯成功時，重 match 應 PASS（提供正例做為對照基準）
      Given a temporary file at "data/domain.dbml" with content:
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
      Then the run exits zero
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format

  Rule: 後置（回應）- 含 (<FILL IN>) sentinel 的 step 不參與 re-match 斷言；其他正常 step 仍受斷言保護
    Example: 帶 security: 區塊的 operation 產出 (<FILL IN>) sentinel — 不會讓 re-match 斷言整體失敗
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
          /games:
            post:
              summary: 建立遊戲
              security:
                - playerTokenAuth: []
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
          - format: "建立遊戲 {名稱}"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings: {}
            datatable_bindings:
              名稱: { target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/name }
        """
      When dsl_to_isa translates the last dsl file
      Then the run exits zero
      And dsl step "games.create" has isa_steps[0].instruction equal to "(<FILL IN>) 建立遊戲, call table:"
      And every non-sentinel translated isa_steps[0].instruction re-matches its source isa.yml format
