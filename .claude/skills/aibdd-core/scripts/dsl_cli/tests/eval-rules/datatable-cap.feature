Feature: eval rule `datatable-cap` enforces ≤ 6 required datatable fields

  Rule: 後置（回應）- datatable_bindings 中 required:true 且無 default_value 之欄位 > 6 應 FAIL
    Example: 7 個必填 datatable 欄位 → violation
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家以 datatable 加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings:
              a: { required: true, target: contracts/room.api.yml#a }
              b: { required: true, target: contracts/room.api.yml#b }
              c: { required: true, target: contracts/room.api.yml#c }
              d: { required: true, target: contracts/room.api.yml#d }
              e: { required: true, target: contracts/room.api.yml#e }
              f: { required: true, target: contracts/room.api.yml#f }
              g: { required: true, target: contracts/room.api.yml#g }
        """
      When evaluate runs
      Then a violation with rule_id "datatable-cap" is present

  Rule: 後置（狀態）- 套用 default_value 後不再算 required 之欄位不入閘門
    Example: 7 個欄位但其中 2 個帶 default_value → 5 required ≤ 6 → PASS
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 玩家以 datatable 加入房間
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings:
              a: { required: true,  target: contracts/room.api.yml#a }
              b: { required: true,  target: contracts/room.api.yml#b }
              c: { required: true,  target: contracts/room.api.yml#c }
              d: { required: true,  target: contracts/room.api.yml#d }
              e: { required: true,  target: contracts/room.api.yml#e }
              f: { required: false, target: contracts/room.api.yml#f, default_value: "x" }
              g: { required: false, target: contracts/room.api.yml#g, default_value: "y" }
        """
      When evaluate runs
      Then EvalReport status is "PASS"
