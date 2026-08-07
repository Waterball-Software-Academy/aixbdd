Feature: build_worklist 完成度判準與 schema
  作為 dsl-refine 主流程步驟 5
  我要 只把「真的還沒有可用定義」的 example 列進 worklist，並給消費端一組固定的鍵
  以便 已收官模組不會永久假陽性、消費端不必猜鍵

  Rule: #48 判準＝該 example 每個 step 都對得上一條定義（`# done` 或 isa_steps 已備妥）

    Example: red-execute 機械修補新增的定義沒補 `# done`，仍算已完成
      Given packages fixture "packages"
      When 執行 build_worklist
      Then worklist 沒有任何待處理 FP

  Rule: #46 推導中的定義只住 `.dsl.yml.draft`，不算已完成

    Example: 定義只在草稿檔，example 仍為 pending
      Given packages fixture "packages-draft"
      When 執行 build_worklist
      Then worklist 的 FP「02-課程管理」有 1 個待處理 example
      And worklist 各層的鍵為:
        | 層級       | 鍵                                  |
        | fps[]      | slug、pending_examples、features    |
        | features[] | feature、pending_examples、examples |
        | examples[] | title、status、undone_steps         |
