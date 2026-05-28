Feature: load form-lock profile for active boundary

  Rule: 後置（狀態） - loader 應把 profile 轉成可用 JSON
    Example: 明確 profile 輸入應得到對應 JSON projection
      Given a form-lock profile at "fixtures/web-service/sbe-form-lock/form-lock.profile.yml" with content:
        """
        boundary_type: web-service
        rule_prefix_to_template:
          - rule_prefix: "前置（狀態"
            template: precondition-state.tmpl
          - rule_prefix: "後置（回應"
            template: postcondition-response.tmpl
        """
      When load_form_lock_profile CLI is run on the profile path
      Then CLI exit code is 0
      And CLI JSON projection should equal:
        """
        {
          "boundary_type": "web-service",
          "rule_prefix_to_template": [
            { "rule_prefix": "前置（狀態", "template": "precondition-state.tmpl" },
            { "rule_prefix": "後置（回應", "template": "postcondition-response.tmpl" }
          ]
        }
        """

  Rule: 後置（狀態） - rule_prefix 應依長度降序排序
    Example: 輸入未排序 prefix 時輸出應為最長者在前
      Given a form-lock profile at "fixtures/web-service/sbe-form-lock/form-lock.profile.yml" with content:
        """
        boundary_type: web-service
        rule_prefix_to_template:
          - rule_prefix: "後置"
            template: postcondition-state-short.tmpl
          - rule_prefix: "後置（狀態）-特殊流程"
            template: postcondition-state-special.tmpl
          - rule_prefix: "後置（狀態"
            template: postcondition-state.tmpl
        """
      When load_form_lock_profile CLI is run on the profile path
      Then CLI exit code is 0
      And CLI JSON projection should equal:
        """
        {
          "boundary_type": "web-service",
          "rule_prefix_to_template": [
            { "rule_prefix": "後置（狀態）-特殊流程", "template": "postcondition-state-special.tmpl" },
            { "rule_prefix": "後置（狀態", "template": "postcondition-state.tmpl" },
            { "rule_prefix": "後置", "template": "postcondition-state-short.tmpl" }
          ]
        }
        """
