Feature: dsl_to_isa skips byte-equal rewrites and overwrites stale translations (no append)

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

  Rule: 後置（狀態）- 既有 isa_steps 與新翻譯結果 byte-equal 時應 skip 寫入
    Example: 第二次跑同一份 dsl.yml 應計入 idempotent skip
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
      And dsl_to_isa has translated the last dsl file
      When dsl_to_isa translates the last dsl file
      Then summary reports first_write_count 0 and idempotent_skip_count 1

  Rule: 後置（狀態）- 已有 isa_steps 但已過期應整段覆寫，不疊加
    Example: dsl.yml 預先含舊翻譯（單一 isa_steps 條目，內容過期），翻譯後 length 仍為 1 且內容為新版
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在房間"
            name: rooms.state-builder
            handler: state-builder
            target_part_path: data/domain.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              房號:
                target: data/domain.dbml#rooms.room_code
              狀態:
                required: false
                target: data/domain.dbml#rooms.status
                default_value: ""
            params:
              - 舊欄:
            isa_steps:
              - instruction: "舊指令, with table:"
                table:
                  old_col: "{{舊欄}}"
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.state-builder" has isa_steps length 1
      And dsl step "rooms.state-builder" has isa_steps[0].instruction equal to "準備一個rooms, with table:"
      And dsl step "rooms.state-builder" has isa_steps[0].table equal to:
        """
        room_code: "{{房號}}"
        status: "{{狀態}}"
        """
