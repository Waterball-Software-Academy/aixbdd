Feature: preset_loader rejects plugins that violate the entry-function contract

  Background:
    Given a temporary file at "boundaries/bad-preset/scripts/part_to_dsl.py" with content:
      """
      # Intentionally missing generate_templates.
      def unrelated_function():
          return None
      """

  Rule: 後置（回應）- 載入缺 generate_templates 的 plugin 應 raise PluginContractError
    Example: bad-preset 無 entry function → PluginContractError
      When preset_loader loads "bad-preset" and captures the exception
      Then the captured exception is of type "PluginContractError"
      And the captured exception message mentions "generate_templates"
