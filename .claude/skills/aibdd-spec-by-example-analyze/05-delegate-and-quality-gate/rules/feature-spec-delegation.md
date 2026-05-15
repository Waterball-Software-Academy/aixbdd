# `/aibdd-form-feature-spec` DELEGATE 顆粒度

- **記什麼**：每個 feature path 之 example-fill 委派 payload 之必要欄位、subagent 並行策略、回應驗收條件。
- **WHY**：`.feature` 之 mutation 之唯一合法管道是 `/aibdd-form-feature-spec` mode=example-fill；本 skill 不手寫 `.feature` 任一行（quality gate 之 VETO 條件之一）。

## §1 Payload shape

```yaml
target_path: <repo-relative feature path>     # 必須落於 ${FEATURE_SPECS_DIR}
mode: "example-fill"                          # 固定字串
reasoning:
  groups:                                     # 04 之 $scenario_plan.groups[]，僅該 feature_path 之子集
    - feature_path: ...
      rule_anchor: ...
      merge_decision: { ... }
      example_body_shape: { ... }
      example_columns: [ ... ]
      rows: [ ... ]
      precondition_setup: [ ... ]
  coverage_rows: [ ... ]                      # 該 feature 之 coverage rows
  dsl_binding_refs:                           # 該 feature 用到之 DSL entry id 子集
    - entry_id: ...
      L1: { ... }
      L4: { ... }
atomic_rule_ids: [ ... ]                      # 該 feature 涵蓋之 atomic rule anchors（用於 form-feature-spec 驗證 NO_RULE_WORDING_CHANGE）
```

## §2 並行策略

- **多 feature path（`length($feature_file_tasks) > 1`）+ runtime 支援 subagent／task 平行**：以 subagent 並行 DELEGATE。
- **多 feature path + runtime 不支援平行**：sequential DELEGATE，行為等價。
- **單一 feature path**：直接 DELEGATE 一次。
- 並行模式下，任一 task 失敗 → 收集失敗 target_path 後 STOP；不續跑剩餘 task。

## §3 驗收條件

- DELEGATE 回傳 `{ok: bool, target_path, atomic_rule_anchors_preserved: bool, dsl_bindings_unchanged: bool }`。
- `ok=true` AND `atomic_rule_anchors_preserved=true` AND `dsl_bindings_unchanged=true` → PASS。
- 任一為 false → STOP + REPORT；不寫 coverage rows，不續跑 quality gate。

# 反例

- ✗ payload 缺 `mode: "example-fill"`——form-feature-spec 預設可能跑 full-rebuild，會吃 atomic rule body。
- ✗ payload 把整份 `$scenario_plan`（含其他 feature path 之 groups）塞入單一 task——`/aibdd-form-feature-spec` 是 per-target-path skill，跨 path payload 會被 reject。
- ✗ `target_path` 寫絕對路徑——必須為 repo-relative（`${FEATURE_SPECS_DIR}` 為基準）。
- ✗ 多 feature path 用單一 DELEGATE 一次傳——本 skill 不批次；form-feature-spec 一次一份。
- ✗ runtime 支援 subagent 卻仍 sequential——浪費並行能力，違反 v2 預設並行策略。
- ✓ 4 個 feature path → 4 個並行 subagent DELEGATE；任一失敗 → 等其餘完成後 STOP，列出 4 個結果。

# 禁止自生

- **不得**繞過 DELEGATE 直接寫 `.feature`（即使是「順手加一條 Scenario」）——quality gate 偵測本 skill 對 `.feature` 之直接寫入即 VETO。
- **不得**自加 payload 欄位譬如 `auto_fix_rule_wording: true`——`/aibdd-form-feature-spec` 之 contract 不接受此類欄位；自加 = 違反 ownership。
- **不得**把上游 `/aibdd-plan` 之 DSL／contract／data 塞入 payload 之 mutable 欄位（譬如 `dsl_overrides`）——上游真相為唯讀。
- 違反處置：DELEGATE 動作取消，CiC(CON) 累積，提示使用者本 skill 配置錯誤。
