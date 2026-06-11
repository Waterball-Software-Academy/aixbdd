Feature: dsl_to_isa stops with a clear pointer when isa.yml or entity_to_table_mapping.yml is missing

  # NOTE: 翻譯前必備檔（contracts/isa.yml + data/entity_to_table_mapping.yml）由上游 skill 產生；
  # 缺檔屬於 spec drift，translator 必須立刻 STOP 並指向上游修復點，不能 silent-skip 或產出半截結果。
  # 兩條 Rule 各自只放對應「未缺」的那一份 fixture，避免 Background 干擾「缺檔」斷言。

  Rule: 前置（輸入）- contracts/isa.yml 不存在時 STOP，stderr 指出檔路徑 + 上游修復點
    Example: 只有 entity_map + dsl.yml，沒有 isa.yml
      Given a temporary file at "data/entity_to_table_mapping.yml" with content:
        """
        rooms: rooms
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
      Then the run exits non-zero
      And stderr contains "contracts/isa.yml"
      And stderr contains "/aibdd-plan"
      And stderr contains "02-contracts-design"

  Rule: 前置（輸入）- data/entity_to_table_mapping.yml 不存在時 STOP，stderr 指出檔路徑 + 上游修復點
    Example: 只有 isa.yml + dsl.yml，沒有 entity_to_table_mapping.yml
      Given a temporary file at "contracts/isa.yml" with content:
        """
        instructions:
          - name: entity_setup
            instruction_type: state
            format: '準備一個(?P<entity>\S+), with table:'
            data_format: table
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
      Then the run exits non-zero
      And stderr contains "data/entity_to_table_mapping.yml"
      And stderr contains "01-table-to-entity"
