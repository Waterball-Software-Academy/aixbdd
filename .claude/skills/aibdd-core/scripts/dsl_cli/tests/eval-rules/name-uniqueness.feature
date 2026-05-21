Feature: eval rule `name-uniqueness` enforces unique entry names across all dsl + shared

  Rule: 後置（回應）- 同一 dsl.yml 內兩條 entry 同名 → FAIL
    Example: 重複 name 'joinRoom.operation-invoke'
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家加入房間 v1
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
          - format: 玩家加入房間 v2
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "name-uniqueness" is present

  Rule: 後置（回應）- 與 shared-dsl 中的 name 撞名 → FAIL
    Example: 'shared.now' 已在 shared-dsl namespace
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 系統時間現在
            name: shared.now
            handler: time-control
            target_part_path: contracts/room.api.yml#/paths/~1now/get
            param_bindings: {}
            datatable_bindings: {}
        """
      And a shared DSL namespace containing:
        | name       |
        | shared.now |
      When evaluate runs
      Then a violation with rule_id "name-uniqueness" is present
