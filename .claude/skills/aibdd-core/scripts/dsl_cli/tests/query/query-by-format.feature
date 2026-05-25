Feature: dsl_cli query filters DSL corpus by step text with placeholder-aware exact match

  Rule: 後置（狀態）- literal format 與 step text 完全一致時回一筆
    Example: 無 placeholder 的 format 精確命中
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
      When dsl_cli query runs with step-text "玩家加入房間" against the last file
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

  Rule: 後置（狀態）- placeholder 槽位接受具體 Example 值
    Example: format 內 placeholder 以具體值查詢
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家 {玩家Id} 加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              玩家Id:
                target: literal:playerId
            datatable_bindings: {}
        """
      When dsl_cli query runs with step-text "玩家 P1 加入房間" against the last file
      Then query match output should equal:
        """
        [
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "contracts/room.dsl.yml",
            "source_scope": "regular",
            "format": "玩家 {玩家Id} 加入房間",
            "param_bindings": {
              "玩家Id": {
                "target": "literal:playerId"
              }
            },
            "datatable_bindings": {}
          }
        ]
        """

  Rule: 後置（狀態）- handler 與 step-text 併用時為 AND filter
    Example: handler 不符者不回、format 不符者也不回
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
      When dsl_cli step-text query runs with handlers "operation-invoke" and text "玩家加入房間" against the last file
      Then query match output should equal:
        """
        [
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

  Rule: 後置（狀態）- step text 無命中回空陣列
    Example: 語意無關的查詢字串
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with step-text "完全不相關的操作" against the last file
      Then query match output should equal:
        """
        []
        """

  Rule: 後置（狀態）- 多筆相同 format 皆命中且保 scan order
    Example: 兩條同 format 不同 name 全回傳
      Given a temporary file at "contracts/dup.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 玩家加入房間
            name: altRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1alt/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with step-text "玩家加入房間" against the last file
      Then query match output should equal:
        """
        [
          {
            "name": "joinRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms/post",
            "source_file": "contracts/dup.dsl.yml",
            "source_scope": "regular",
            "format": "玩家加入房間",
            "param_bindings": {},
            "datatable_bindings": {}
          },
          {
            "name": "altRoom.operation-invoke",
            "handler": "operation-invoke",
            "target_part_path": "contracts/room.api.yml#/paths/~1rooms~1alt/post",
            "source_file": "contracts/dup.dsl.yml",
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
          - format: 玩家加入房間
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
      When dsl_cli query runs with step-text "標記準備" against files aliased "room" and "data"
      Then query match output should equal:
        """
        [
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
      When dsl_cli query runs with step-text "時鐘控制" and source-scope "shared" against shared alias "shared"
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
      When dsl_cli query runs with step-text "外部 stub" and source-scope "all" against regular file alias "regular" and shared file alias "shared"
      Then query match output should equal:
        """
        [
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

  Rule: 後置（狀態）- 純查詢重跑結果不變
    Example: 第二次 step-text query 與第一次相同
      Given a temporary file at "contracts/room.dsl.yml" with content:
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When dsl_cli query runs with step-text "玩家加入房間" against the last file
      And dsl_cli query runs with step-text "玩家加入房間" against the last file again
      Then query match output should equal the previous query match output
