Feature: dsl_to_isa collects modular dsl corpus under contracts/ and data/

  # 修補：除 shared/dsl.yml、packages/*/dsl.yml 外，亦掃描
  # ${CONTRACTS_DIR}/*.dsl.yml 與 ${DATA_DIR}/*.dsl.yml（backend 實際佈局）。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: api_call
          instruction_type: action
          format: '(?P<actor>No Actor|UID="\$\S+") (?P<summary>.+), call table:'
          data_format: table
        - name: entity_setup
          instruction_type: state
          format: '準備一個(?P<entity>\S+), with table:'
          data_format: table
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      rooms: rooms
      """

  Rule: 後置（狀態）- env 驅動一次翻譯應同時處理 contracts/*.dsl.yml 與 data/*.dsl.yml
    Example: 兩份模組化 dsl 各寫入 isa_steps
      Given the env var BOUNDARY_SHARED_DSL is unset
      And TRUTH_BOUNDARY_PACKAGES_DIR contains no dsl.yml
      And a temporary file at "contracts/ops.dsl.yml" with content:
        """
        dsl_steps:
          - format: "建立遊戲"
            name: games.create
            handler: operation-invoke
            target_part_path: contracts/games.api.yml#/paths/~1games/post
            param_bindings: {}
            datatable_bindings:
              名稱: { target: contracts/games.api.yml#/paths/~1games/post/requestBody/content/application~1json/schema/properties/name }
        """
      And a temporary file at "contracts/games.api.yml" with content:
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
                      type: object
                      properties:
                        name: { type: string }
        """
      And a temporary file at "data/world.dsl.yml" with content:
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
      And a temporary file at "data/domain.dbml" with content:
        """
        Table rooms {
          id        integer    [pk]
          room_code varchar(4) [not null]
        }
        """
      When dsl_to_isa runs
      Then the run exits zero
      And summary reports first_write_count 2 and idempotent_skip_count 0
      And dsl file at "contracts/ops.dsl.yml" step "games.create" has isa_steps[0].instruction equal to "(No Actor) 建立遊戲, call table:"
      And dsl file at "data/world.dsl.yml" step "rooms.state-builder" has isa_steps[0].instruction equal to "準備一個rooms, with table:"
