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

  Rule: 後置（狀態）- datatable_bindings 中有 default_value 仍為 <FILL IN> 的欄位應 FAIL
    Example: nickname 欄位 default_value 尚未被 SEMANTIC 替換
      Given the following DSL entries in "data/data.dsl.yml":
        """
        dsl_steps:
          - format: "there is a user"
            name: users.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#users
            param_bindings: {}
            datatable_bindings:
              nickname:
                required: false
                target: data/data.dbml#users.nickname
                default_value: "<FILL IN>"
        """
      When evaluate runs
      Then a violation with rule_id "schema-completeness" is present

  Rule: 後置（狀態）- datatable_bindings 中 default_value 為真實值應 PASS
    Example: role 欄位已填入 "guest"，不應產生 violation
      Given the following DSL entries in "data/data.dsl.yml":
        """
        dsl_steps:
          - format: "there is a user with role {role}"
            name: users.state-builder
            handler: state-builder
            target_part_path: data/data.dbml#users
            param_bindings:
              role:
                target: data/data.dbml#users.role
            datatable_bindings:
              nickname:
                required: false
                target: data/data.dbml#users.nickname
                default_value: "guest"
        """
      When evaluate runs
      Then no violation with rule_id "schema-completeness" is present
