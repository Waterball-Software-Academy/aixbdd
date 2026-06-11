Feature: dsl_to_isa rejects DSL steps whose handler is absent from the translator's built-in handler table

  # NOTE: handler → instruction 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # SSOT 為翻譯器模組 02-dsl-to-isa-mapping/scripts/lib/dsl_to_isa/web_service.py（HANDLER_TABLE），
  # 詳見 aibdd-dsl-to-isa-interpretation skill 的 02-dsl-to-isa-mapping/SOP.md。

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

  Rule: 前置（輸入）- handler 必須命中 translator 內建對照表才能翻譯
    Example: 不在內建表上的 handler 應 STOP 並列出 step name
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "未知行為"
            name: rooms.bogus-handler
            handler: unknown-handler
            target_part_path: data/domain.dbml#rooms
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then the run exits non-zero
      And stderr contains "rooms.bogus-handler"
      And stderr contains "handler not in translator built-in handler table"
