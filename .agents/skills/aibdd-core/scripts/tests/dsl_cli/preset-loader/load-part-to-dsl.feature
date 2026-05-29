Feature: preset_loader path-based loads a preset's part_to_dsl plugin

  Background:
    Given a temporary file at "boundaries/fake-preset/scripts/part_to_dsl.py" with content:
      """
      def generate_templates(parts, context):
          return [{"handler": "fake-handler", "from_part": getattr(p, "target_part_path", None)} for p in parts]
      """

  Rule: 後置（狀態）- 載入後的 plugin module 應暴露 generate_templates entry function
    Example: 對空 parts 呼叫 generate_templates 應回傳空 list
      When preset_loader loads "fake-preset"
      Then the loaded module exposes attribute "generate_templates"
      And calling generate_templates with empty parts and empty context returns an empty list

  Rule: 後置（狀態）- 同名 preset 重複載入應拿到獨立 module（不共享 sys.modules cache）
    Example: 兩次載入回傳兩個不同 module 物件
      When preset_loader loads "fake-preset"
      And preset_loader loads "fake-preset" again
      Then the two loaded modules are not the same object
