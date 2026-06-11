Feature: dsl_to_isa loads entity_to_table_mapping from nested list layout

  # 修補：01-table-to-entity 曾產出
  #   entity_to_table_mapping:
  #     - rooms: rooms
  # orchestrator 應與 flat `rooms: rooms` 等價。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: entity_setup
          instruction_type: state
          format: '準備一個(?P<entity>\S+), with table:'
          data_format: table
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      entity_to_table_mapping:
        - rooms: rooms
      """

  Rule: 後置（狀態）- nested list 格式應能通過 state-builder 驗證並翻譯
    Example: rooms.state-builder 使用 nested entity map
      Given a temporary file at "data/domain.dbml" with content:
        """
        Table rooms {
          id        integer    [pk]
          room_code varchar(4) [not null]
        }
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
      When dsl_to_isa translates the last dsl file
      Then the run exits zero
      And dsl step "rooms.state-builder" has isa_steps[0].instruction equal to "準備一個rooms, with table:"
      And dsl step "rooms.state-builder" has isa_steps[0].table equal to:
        """
        room_code: "{{房號}}"
        """
