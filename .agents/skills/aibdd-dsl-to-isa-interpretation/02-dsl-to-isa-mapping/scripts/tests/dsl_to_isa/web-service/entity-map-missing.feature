Feature: dsl_to_isa stops when an entity referenced by a DSL step is absent from entity_to_table_mapping

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。

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
      rooms: rooms
      """

  Rule: 後置（回應）- entity_to_table_mapping 缺少對應 table 時 STOP
    Example: dsl 引用 `orders` 但 entity_map 沒這條
      Given a temporary file at "data/domain.dbml" with content:
        """
        Table orders {
          id        integer    [pk]
          order_no  varchar(8) [not null]
        }
        """
      And a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在訂單"
            name: orders.state-builder
            handler: state-builder
            target_part_path: data/domain.dbml#orders
            param_bindings: {}
            datatable_bindings:
              訂單號: { target: data/domain.dbml#orders.order_no }
        """
      When dsl_to_isa translates the last dsl file
      Then the run exits non-zero
      And stderr contains "orders"
      And stderr contains "entity_to_table_mapping"
