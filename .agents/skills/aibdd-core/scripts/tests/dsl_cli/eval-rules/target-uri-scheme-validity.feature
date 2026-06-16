Feature: eval rule `target-uri-scheme-validity` enforces 5 valid target URI schemes

  Rule: 後置（狀態）- 五種合法 scheme 應全 PASS
    Example: spec anchor、response:、literal:、stub_payload:、DBML anchor 各一條
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 房號 "{房號}" 與人數 "{人數}"
            name: ok.entry
            handler: operation-response-verify
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              房號:
                target: response:$.roomNo
              人數:
                target: response:$.playerCount
            datatable_bindings:
              時刻:
                required: true
                target: literal:iso8601-instant
              玩家Id:
                required: true
                target: stub_payload:targetUserId
              users-id:
                required: true
                target: data/data.dbml#users.id
        """
      When evaluate runs
      Then EvalReport status is "PASS"

  Rule: 後置（回應）- target 不符合任何合法 scheme 應 FAIL
    Example: target 用 unknown:foo 開頭
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 異常條目 "{x}"
            name: bad.entry
            handler: operation-invoke
            target_part_path: contracts/room.api.yml#/paths/~1rooms/post
            param_bindings:
              x:
                target: unknown:nope
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "target-uri-scheme-validity" is present

  Rule: 後置（回應）- target_part_path 非 spec anchor 形態（缺 #）應 FAIL
    Example: target_part_path 無 # 分隔
      Given the following DSL entries in "contracts/room.dsl.yml":
        """
        dsl_steps:
          - format: 異常條目
            name: bad.entry
            handler: operation-invoke
            target_part_path: contracts/room.api.yml
            param_bindings: {}
            datatable_bindings: {}
        """
      When evaluate runs
      Then a violation with rule_id "target-uri-scheme-validity" is present
