# Implementation Task Wording Contract

## Goal

GREEN task wording must not misstate current product-code reality.

## Required Distinction

Every implementation task should make clear which of these states applies:

1. the class does not exist yet and must be created
2. the class exists and needs a new method or responsibility
3. the class and method already exist, and the task is to adjust or extend behavior

## Allowed Wording Patterns

- New class:
  - `建立 \`ClassName\` 類別，並實作 ...`
  - `若 \`ClassName\` 尚不存在，先建立類別，再 ...`
- Existing class, new capability:
  - `在既有 \`ClassName\` 上補上 ...`
  - `基於既有 \`ClassName\` 擴充 ...`
- Existing class and existing method:
  - `基於既有 \`ClassName.method\` 調整 / 補強 ...`
  - `檢查既有 \`ClassName.method\`，必要時修正 ...`

## Forbidden Drift

- Do not describe a non-existent class as if it already exists.
- Do not describe an already-existing method as if it is certainly missing, unless the task explicitly says the worker should verify and then patch if needed.
- Do not use broad `補齊` wording when the class existence state is unknown but inferable from current code.
