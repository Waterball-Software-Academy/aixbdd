Feature: dsl_to_isa translates time-control into time_control by direct format substitution

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。

  Background:
    Given a temporary file at "contracts/isa.yml" with content:
      """
      instructions:
        - name: time_control
          instruction_type: control
          format: '現在時間為 "(?P<time>[^"]+)"'
      """

  Rule: 後置（狀態）- time-control 翻成 time_control，instruction 直接套 format
    Example: 凍結到具體時刻
      Given a temporary file at "specs/p1/dsl.yml" with content:
        """
        dsl_steps:
          - format: "現在時間為 {時間}"
            name: time.freeze
            handler: time-control
            target_part_path: ""
            param_bindings:
              時間: { target: "@time" }
            datatable_bindings: {}
        """
      When dsl_to_isa translates the last dsl file
      Then dsl step "time.freeze" has params length 0
      And dsl step "time.freeze" has isa_steps[0].instruction equal to '現在時間為 "{{時間}}"'
