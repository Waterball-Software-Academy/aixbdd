# Rule reducer metadata（每條 Rule 必備，internal only）

以下 metadata 來源 RP-02 / RP-03 / RP-04，**僅存在 reasoning / coverage / handoff artifact**；不得回寫進 `.feature`：

```gherkin
rule_anchor: …Discovery 原文標題與條件…
type: 前置（參數）| 前置（狀態）| 後置（回應）| 後置（狀態）
techniques: [EP, …]
params:
  ...
dimensions: [happy_path, …]
dsl_entry_ids: [dsl-order-...]
binding_keys: [customer_id, ...]
contract_refs: [contracts/api.yml#operation_id....]
dimension_na:
  - ...
cic:
  - ...
values:
  given: ...
  when: ...
  then: ...
merge_decision:
  step0_when_then_same: true
  step1_given_same: true
  outcome: Scenario | ScenarioOutline | Example
```
