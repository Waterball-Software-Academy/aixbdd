Feature: dsl_to_isa translates state-verifier into entity_validate

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: entity_validate
          instruction_type: state
          format: '應該存在一個(?P<entity>\S+), with table:'
          data_format: table
      """
    And a temporary file at "data/entity_to_table_mapping.yml" with content:
      """
      rooms: rooms
      games: games
      """

  Rule: 後置（狀態）- state-verifier 翻成 entity_validate，instruction format 對應 `應該存在一個<entity>`
    Example: rooms.state-verifier 引用既有 domain.dbml#rooms
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
          - format: "驗證房間"
            name: rooms.state-verifier
            handler: state-verifier
            target_part_path: data/domain.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              房號: { target: data/domain.dbml#rooms.room_code }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.state-verifier" has params keys ["房號"] in order
      And dsl step "rooms.state-verifier" has isa_steps[0].instruction equal to "應該存在一個rooms, with table:"

  Rule: 後置（狀態）- params 全部 required（無 default_value）時，序列化為「裸鍵字串清單」，不得多出尾冒號
    # 規約：params 清單同質——全 required → flat list of bare keys（- A / - B）；
    # 一旦有任一 binding 帶 default_value 才切換為 single-key mapping 清單（見 entity-setup-translate）。
    Example: rooms.state-verifier 多個 required 欄位，params 為裸字串清單
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "驗證房間"
            name: rooms.state-verifier
            handler: state-verifier
            target_part_path: data/domain.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              房號: { target: data/domain.dbml#rooms.room_code }
              狀態: { target: data/domain.dbml#rooms.status }
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.state-verifier" has params equal to:
        """
        - 房號
        - 狀態
        """

  Rule: 後置（狀態）- state-verifier 的 inline param_bindings 也應進 table；params 仍只由 datatable_bindings 產生
    Example: games.state-verifier 將 phase / demon_hp / demon_hp_max 寫入驗證 table
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: 資料表 games 的階段 "{phase}" 魔王血量 "{demon_hp}" 上限 "{demon_hp_max}"
            name: games.state-verifier
            handler: state-verifier
            target_part_path: specs/data/domain.pg.sql#games
            param_bindings:
              phase:
                target: specs/data/domain.pg.sql#games.phase
              demon_hp:
                target: specs/data/domain.pg.sql#games.demon_hp
              demon_hp_max:
                target: specs/data/domain.pg.sql#games.demon_hp_max
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "games.state-verifier" has empty params list
      And dsl step "games.state-verifier" has isa_steps[0].instruction equal to "應該存在一個games, with table:"
      And dsl step "games.state-verifier" has isa_steps[0].table equal to:
        """
        phase: "{{phase}}"
        demon_hp: "{{demon_hp}}"
        demon_hp_max: "{{demon_hp_max}}"
        """
