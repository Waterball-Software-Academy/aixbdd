Feature: {{FEATURE_TITLE}}

  # 預設直接從 Rule / Example 起手，不要把 Background 當成起手式。
  # 只有多個 Example 真的共用同一段帶測試語意的步驟，且抽出後更好讀時，才另外補上 Background。
  # 不可把 spec 摘要、世界觀或全域規則導讀寫成 Background。

  Rule: {{RULE_NAME}}

    # [need clarification] {{CLARIFICATION_QUESTION_1}}

    Example: {{JOURNEY_EXAMPLE_TITLE}}
      Given {{ACTOR_NAME}} 已具備 {{PRECONDITION_SUMMARY}}
      And {{ACTOR_NAME}} 的情境如下：
        | {{SETUP_TABLE_HEADER_1}} | {{SETUP_TABLE_HEADER_2}} | {{SETUP_TABLE_HEADER_3}} |
        | {{SETUP_TABLE_VALUE_1}}  | {{SETUP_TABLE_VALUE_2}}  | {{SETUP_TABLE_VALUE_3}}  |
      When {{ACTOR_NAME}} {{PRIMARY_ACTION}}
      And {{ACTOR_NAME}} {{SECONDARY_ACTION}}
      Then {{PRIMARY_BUSINESS_OUTCOME}}
      And {{SUMMARY_LABEL}} 如下：
        | 項目               | 值                  |
        | {{SUMMARY_ITEM_1}} | {{SUMMARY_VALUE_1}} |
        | {{SUMMARY_ITEM_2}} | {{SUMMARY_VALUE_2}} |
      And {{FOLLOW_UP_OUTCOME}}
