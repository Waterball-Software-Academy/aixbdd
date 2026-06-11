Feature: dsl_to_isa translates state-builder into entity_setup — placeholders for every datatable_binding, default_value carried into params

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。
  # 翻譯只看 dsl.yml — 上游 part_to_dsl 已把所有 not-null 欄位（除 pk+increment）收進 datatable_bindings
  # 並填好 default_value；adapter 不 parse DBML。
  #
  # 每筆 datatable_binding → table 的 "{{<DSL key>}}" placeholder。
  # params 攜帶 default_value 或 null：
  #   - null  = required（runtime 必須由 .feature DataTable 提供）
  #   - 非 null = optional with fallback default

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
      players: players
      users: users
      """

  Rule: 後置（狀態）- state-builder 翻成 entity_setup；每筆 datatable_binding 入 table 為 "{{<DSL key>}}" placeholder；params 攜帶 default_value 或 null
    Example: rooms 表 3 個 not-null（除 pk+increment id），混合 required 與 optional-with-default
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在以下房間資料"
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
                default_value: "waiting"
              建立時間:
                required: false
                target: data/domain.dbml#rooms.created_at
                default_value: '@time("now")'
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "rooms.state-builder" has params keys ["房號", "狀態", "建立時間"] in order
      # 混寫（至少一個 binding 帶 default_value）→ 整個 params 切換為 mapping；
      # required 鍵（房號）攜帶 null，序列化為裸尾冒號 `房號:`，與帶值鍵同處一個 mapping。
      And dsl step "rooms.state-builder" has params equal to:
        """
        房號:
        狀態: "waiting"
        建立時間: '@time("now")'
        """
      And dsl step "rooms.state-builder" has isa_steps[0].instruction equal to "準備一個rooms, with table:"
      And dsl step "rooms.state-builder" has isa_steps[0].table equal to:
        """
        room_code: "{{房號}}"
        status: "{{狀態}}"
        created_at: "{{建立時間}}"
        """

  Rule: 後置（狀態）- default_value 各型別（string / integer / boolean / timestamp）皆原樣帶進 params，不被型別轉型；table 一律 placeholder
    Example: players 表 4 種 not-null 型別，全 optional-with-default，驗證 params 攜值原樣
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在玩家"
            name: players.state-builder
            handler: state-builder
            target_part_path: data/domain.dbml#players
            param_bindings: {}
            datatable_bindings:
              暱稱:
                required: false
                target: data/domain.dbml#players.nickname
                default_value: ""
              年齡:
                required: false
                target: data/domain.dbml#players.age
                default_value: 0
              是否啟用:
                required: false
                target: data/domain.dbml#players.is_active
                default_value: false
              註冊時間:
                required: false
                target: data/domain.dbml#players.registered_at
                default_value: '@time("now")'
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "players.state-builder" has params equal to:
        """
        暱稱: ""
        年齡: 0
        是否啟用: false
        註冊時間: '@time("now")'
        """
      And dsl step "players.state-builder" has isa_steps[0].table equal to:
        """
        nickname: "{{暱稱}}"
        age: "{{年齡}}"
        is_active: "{{是否啟用}}"
        registered_at: "{{註冊時間}}"
        """

  Rule: 後置（狀態）- state-builder 的 inline param_bindings 也應進 table；params 仍只由 datatable_bindings 產生
    Example: users 表 inline role 進 table，datatable nickname 仍進 params
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "there is a user with role {role}"
            name: users.state-builder
            handler: state-builder
            target_part_path: data/domain.dbml#users
            param_bindings:
              role:
                target: data/domain.dbml#users.role
            datatable_bindings:
              nickname:
                required: false
                target: data/domain.dbml#users.nickname
                default_value: "guest"
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "users.state-builder" has params equal to:
        """
        nickname: "guest"
        """
      And dsl step "users.state-builder" has isa_steps[0].instruction equal to "準備一個users, with table:"
      And dsl step "users.state-builder" has isa_steps[0].table equal to:
        """
        role: "{{role}}"
        nickname: "{{nickname}}"
        """

  Rule: 後置（狀態）- SQL now() default（來自 DDL DEFAULT now()）翻成 DSL 時間巨集 @time("now")；大小寫不敏感
    Example: players 表 created_at DEFAULT now() → params 攜 @time("now")，table 仍 placeholder
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在玩家"
            name: players.state-builder
            handler: state-builder
            target_part_path: data/accounts.pg.sql#players
            param_bindings: {}
            datatable_bindings:
              暱稱:
                target: data/accounts.pg.sql#players.nickname
              建立時間:
                required: false
                target: data/accounts.pg.sql#players.created_at
                default_value: "NOW()"
              更新時間:
                required: false
                target: data/accounts.pg.sql#players.updated_at
                default_value: "now()"
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "players.state-builder" has params equal to:
        """
        暱稱:
        建立時間: '@time("now")'
        更新時間: '@time("now")'
        """
      And dsl step "players.state-builder" has isa_steps[0].table equal to:
        """
        nickname: "{{暱稱}}"
        created_at: "{{建立時間}}"
        updated_at: "{{更新時間}}"
        """

    Example: 其他方言的當下時間 default（MSSQL GETDATE() / 標準 CURRENT_TIMESTAMP）同樣翻成 @time("now")
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "已存在玩家"
            name: players.state-builder
            handler: state-builder
            target_part_path: data/accounts.pg.sql#players
            param_bindings: {}
            datatable_bindings:
              建立時間:
                required: false
                target: data/accounts.pg.sql#players.created_at
                default_value: "GETDATE()"
              更新時間:
                required: false
                target: data/accounts.pg.sql#players.updated_at
                default_value: "CURRENT_TIMESTAMP"
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "players.state-builder" has params equal to:
        """
        建立時間: '@time("now")'
        更新時間: '@time("now")'
        """
