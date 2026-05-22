Feature: eval rule `schema-completeness` enforces non-empty required fields

  Rule: 後置（回應）- format 仍為 <FILL IN> 應 FAIL
    Example: HARNESS-only entry 尚未 SEMANTIC 填字
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: "<FILL IN>"
            name: joinRoom.operation-invoke
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "schema-completeness" is present

  Rule: 後置（回應）- datatable_bindings 中之 default_value 仍為 <FILL IN> 應 FAIL（supplement 補完後 SEMANTIC 尚未填業務值）
    Example: supplement 留下 placeholder、SEMANTIC step 6 未填
      Given the following DSL entries in "data/data.dsl.yml":
        """
        dsl_steps:
          - format: "已存在以下房間資料"
            name: rooms.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              created_at:
                target: data/data.dbml#rooms.created_at
                required: false
                default_value: "<FILL IN>"
        """
      When evaluate runs
      Then a violation with rule_id "schema-completeness" is present

  Rule: 後置（回應）- datatable_bindings 中之 default_value 已被填上業務值 應 PASS
    Example: SEMANTIC 把 placeholder 換成 "now()" → PASS
      Given the following DSL entries in "data/data.dsl.yml":
        """
        dsl_steps:
          - format: "已存在以下房間資料"
            name: rooms.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#rooms
            param_bindings: {}
            datatable_bindings:
              created_at:
                target: data/data.dbml#rooms.created_at
                required: false
                default_value: "now()"
        """
      When evaluate runs
      Then EvalReport status is "PASS"
