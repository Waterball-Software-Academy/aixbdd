Feature: preset_loader wraps Python syntax errors in PluginLoadError

  Background:
    Given a temporary file at "boundaries/broken-preset/scripts/part_to_dsl.py" with content:
      """
      def generate_templates(parts, context):
          this is not valid python
      """

  Rule: 後置（回應）- 載入有 syntax error 的 plugin 應 raise PluginLoadError（內含 plugin 路徑）
    Example: broken-preset → PluginLoadError 含 part_to_dsl.py 路徑
      When preset_loader loads "broken-preset" and captures the exception
      Then the captured exception is of type "PluginLoadError"
      And the captured exception message mentions "part_to_dsl.py"
