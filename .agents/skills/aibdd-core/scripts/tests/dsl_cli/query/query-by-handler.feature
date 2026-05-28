Feature: dsl_cli query filters DSL corpus by handler

  Rule: 後置（狀態）- 單檔單 handler 應回傳 ordered JSON matches
    Example: operation-invoke entry 出現在 matches
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 系統回應
            name: joinRoom.operation-response-success-and-failure
            handler: operation-response-success-and-failure
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post/responses/200
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with handlers "operation-invoke" against the last file
      Then query match output should equal:
        """
        [
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "contracts/room.dsl.yml",
            "source_scope": "regular",
            "format": "玩家加入房間",
            "param_bindings": {},
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- 多 handler OR filter 只回符合者
    Example: 兩 handler 請求只回 state-builder
      Given a temporary file at "data/data.dsl.yml" with content:
        """
        dsl_steps:
          - format: 系統內已存在玩家
            name: users.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#users
            param_bindings: {}
            datatable_bindings: {}
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with handlers "state-builder,operation-invoke" against the last file
      Then query match output should equal:
        """
        [
          {
            "name": "users.state-builder",
            "handler": "state-builder",
            "target_part_path": "data/data.dbml#users",
            "source_file": "data/data.dsl.yml",
            "source_scope": "regular",
            "format": "系統內已存在玩家",
            "param_bindings": {},
            "datatable_bindings": {}
          },
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "data/data.dsl.yml",
            "source_scope": "regular",
            "format": "玩家加入房間",
            "param_bindings": {},
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- 跨多檔掃描順序與 name 去重
    Example: 先 A 檔再 B 檔，重複 name 只保留第一次
      Given a temporary file at "contracts/room.dsl.yml" with content (saved as "room"):
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      And a temporary file at "data/data.dsl.yml" with content (saved as "data"):
        """
        dsl_steps:
          - format: 重複 id
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: data/data.dbml#rooms
            param_bindings: {}
            datatable_bindings: {}
          - format: 標記準備
            name: markPlayerReady.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1ready/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with handlers "operation-invoke" against files aliased "room" and "data"
      Then query match output should equal:
        """
        [
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "contracts/room.dsl.yml",
            "source_scope": "regular",
            "format": "玩家加入房間",
            "param_bindings": {},
            "datatable_bindings": {}
          },
          {
            "name": "markPlayerReady.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms~1ready/post",
            "source_file": "data/data.dsl.yml",
            "source_scope": "regular",
            "format": "標記準備",
            "param_bindings": {},
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- source-scope shared 只查 shared DSL
    Example: time-control 只出現在 shared 檔
      Given a temporary file at "contracts/room.dsl.yml" with content (saved as "regular"):
        """
        dsl_steps:
          - format: 錯誤 scope
            name: clock.time-control
            handler: time-control
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      And a temporary file at "shared/boundary.dsl.yml" with content (saved as "shared"):
        """
        dsl_steps:
          - format: 時鐘控制
            name: clock.time-control
            handler: time-control
            target_part_path: literal:clock
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with handler "time-control" and source-scope "shared" against shared alias "shared"
      Then query match output should equal:
        """
        [
          {
            "name": "clock.time-control",
            "handler": "time-control",
            "target_part_path": "literal:clock",
            "source_file": "shared/boundary.dsl.yml",
            "source_scope": "shared",
            "format": "時鐘控制",
            "param_bindings": {},
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- source-scope all 合併 regular 與 shared 並保序
    Example: regular 在前 shared 在後
      Given a temporary file at "contracts/room.dsl.yml" with content (saved as "regular"):
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      And a temporary file at "shared/boundary.dsl.yml" with content (saved as "shared"):
        """
        dsl_steps:
          - format: 外部 stub
            name: inventoryService.external-stub
            handler: external-stub
            target_part_path: stub_payload:inventory
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with handlers "operation-invoke,external-stub" and source-scope "all" against regular file alias "regular" and shared file alias "shared"
      Then query match output should equal:
        """
        [
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "contracts/room.dsl.yml",
            "source_scope": "regular",
            "format": "玩家加入房間",
            "param_bindings": {},
            "datatable_bindings": {}
          },
          {
            "name": "inventoryService.external-stub",
            "handler": "external-stub",
            "target_part_path": "stub_payload:inventory",
            "source_file": "shared/boundary.dsl.yml",
            "source_scope": "shared",
            "format": "外部 stub",
            "param_bindings": {},
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- handler 無命中回空陣列
    Example: 未知 handler 零 matches
      Given a temporary file at "contracts/empty.dsl.yml" with content:
        """
        dsl_steps: []
        """
      When dsl_cli query runs with handlers "unknown-handler" against the last file
      Then query match output should equal:
        """
        []
        """
