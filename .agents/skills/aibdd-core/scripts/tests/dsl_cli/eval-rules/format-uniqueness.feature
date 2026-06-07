Feature: eval rule `format-uniqueness` enforces unique dsl_step format strings across all dsl

  Rule: 後置（回應）- 同一 dsl.yml 內兩條 entry 的 format 字串完全相同 → FAIL
    Example: 重複 format '玩家加入房間'（name 不同，仍算重複）
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 玩家加入房間
            name: joinRoomAgain.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "FAIL"
      And a violation with rule_id "format-uniqueness" is present

  Rule: 後置（回應）- 跨 dsl.yml 兩條 entry 的 format 字串完全相同 → FAIL
    Example: 'room' 與 'lobby' 兩檔出現相同 format '系統時間現在'
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 系統時間現在
            name: room.now.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1now/get
            param_bindings: {}
            datatable_bindings: {}
        """
      And the following DSL entries in "contracts/lobby.dsl.yml":
        """
        dsl_steps:
          - format: 系統時間現在
            name: lobby.now.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/lobby.api.yml#/paths/~1now/get
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "FAIL"
      And a violation with rule_id "format-uniqueness" is present

  Rule: 後置（回應）- 兩條 entry 的 format 相同但 target_part_path 不同 → 仍 FAIL
    Example: 同 format '操作成功' 對到兩個不同 target part（binding 歧義）
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 操作成功
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 操作成功
            name: leaveRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1leave/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "FAIL"
      And a violation with rule_id "format-uniqueness" is present

  Rule: 後置（狀態）- 兩條 entry 的 format 同為 <FILL IN> → 不開 format-uniqueness（歸 schema-completeness）
    Example: 兩條未填字 entry 只觸發 schema-completeness，不被 format-uniqueness 重複開罰
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: "<FILL IN>"
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: "<FILL IN>"
            name: leaveRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1leave/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "schema-completeness" is present
      And no violation with rule_id "format-uniqueness" is present

  Rule: 後置（狀態）- 所有 entry 的 format 字串皆相異 → PASS
    Example: 三條不同 format 的 entry 全數通過
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 玩家離開房間
            name: leaveRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms~1leave/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 系統時間現在
            name: room.now.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1now/get
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then EvalReport status is "PASS"
      And no violation with rule_id "format-uniqueness" is present
