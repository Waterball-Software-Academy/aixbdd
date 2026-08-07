Feature: 額度試用

  Rule: 前置（參數） - 目標額度不得超過上限 200 萬

    # 測試設計註記：上限 200 萬的 BVA 對照（max / max+1）
    Example: 目標額度等於上限，提交成功
      When "Alice" 提交目標額度 2000000 的試用單
      Then 提交成功

    Example: 目標額度超過上限，提交沒有成功
      When "Alice" 提交目標額度 2000001 的試用單
      Then 提交沒有成功
