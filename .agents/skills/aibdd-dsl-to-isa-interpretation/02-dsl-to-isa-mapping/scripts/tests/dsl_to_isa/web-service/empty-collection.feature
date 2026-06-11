Feature: dsl_to_isa exits zero and reports an info message when no dsl.yml files exist

  # NOTE: handler → (instruction, adapter) 對照表為 translator 內建（hard-coded），非 runtime fixture。

  Rule: 後置（狀態）- 沒有任何 dsl.yml 待翻譯時 emit 訊息並以 0 退出
    Example: BOUNDARY_SHARED_DSL 不存在、TRUTH_BOUNDARY_PACKAGES_DIR 為空
      Given the env var BOUNDARY_SHARED_DSL is unset
      And TRUTH_BOUNDARY_PACKAGES_DIR contains no dsl.yml
      When dsl_to_isa runs
      Then the run exits zero
      And stdout contains "無 dsl.yml 待翻譯"
