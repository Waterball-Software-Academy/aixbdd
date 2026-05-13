# Web Frontend `test-strategy.yml` Schema

> **Owner**: this schema is owned by `aibdd-core`; **`test-strategy.yml`** instances are owned by `/aibdd-plan` (initial placeholder by `/aibdd-kickoff`).  
> **Resolved path** in a project: `${TEST_STRATEGY_FILE}` (typically `specs/<boundary>/test-strategy.yml` per `arguments.yml` §5).  
> **Consumers**: `/aibdd-plan` (writes), `/aibdd-spec-by-example-analyze` (reads `policies`), `prehandling-before-red-phase.md` §3.6 / §3.7 (reads `tier2_handlers` / `viewport_profiles`), `check_frontend_preset_refs.py` (validates Tier-2 enablement match).

---

## §1 Top-level shape

```yaml
version: 1                           # int — schema version

tier2_handlers:                      # map<TierTwoHandler, EnablementState>
  api-stub: disabled
  url-then: disabled
  api-call-then: disabled
  mock-state-then: disabled

viewport_profiles:                   # map<ProfileName, Viewport>
  mobile:   { width: 375,  height: 667  }
  tablet:   { width: 768,  height: 1024 }
  desktop:  { width: 1440, height: 900  }

time_control:                        # optional — required only if any scenario uses time-control handler
  mode: freeze                       # 'freeze' | 'tick'
  epoch_iso: "2024-01-15T10:00:00Z"  # ISO 8601; required when mode is set
  tick_rate_ms: 1                    # mode=tick only; ms advanced per real ms; default 1
  named_instants:                    # map<InstantName, ISO8601>
    base: "2024-01-15T10:00:00Z"
    expiry: "2024-01-22T10:00:00Z"

coverage_gates:                      # map<GateName, GateConfig>
  operation_coverage:
    required: true
    threshold: 1.0
  story_export_coverage:
    required: false
    threshold: 0.8
  schema_field_coverage:
    required: false
    threshold: 0.9

policies: {}                         # map<PolicyId, PolicyEntry> — owned by Spec-by-Example
```

`version`、`tier2_handlers`、`policies` 為**必填**鍵；`viewport_profiles`、`time_control`、`coverage_gates` 為**選填**鍵但建議起始值就帶上（缺 → 對應檢查視為未啟用；scenario 若使用對應 handler 但鍵缺漏，會在 `prehandling-before-red-phase.md` §3.7 被阻擋）。

---

## §2 `tier2_handlers`

Tier-2 handler 來源：`handler-routing.yml` 的 4 個 opt-in handler。

| Key | 允許值 | 預設 | 何時 enable |
|---|---|---|---|
| `api-stub` | `enabled` \| `disabled` | `disabled` | scenario 需要 per-scenario mock-behavior override（next call 回 409、latency injection、response sequence） |
| `url-then` | `enabled` \| `disabled` | `disabled` | scenario 對 URL state 做 load-bearing 斷言（query param、pathname dynamic segment） |
| `api-call-then` | `enabled` \| `disabled` | `disabled` | scenario 斷言特定 outgoing call 是否被觸發（presence / count / shape） |
| `mock-state-then` | `enabled` \| `disabled` | `disabled` | UI 不 render 但 scenario 必須驗證 mock store 變更 |

**綁定規則**：

- 若 `dsl.yml` 出現某 Tier-2 handler 的 `L4.preset.handler`，本檔對應 key **必須**為 `enabled`，否則 `prehandling-before-red-phase.md` §3.6 阻擋。
- enable 後的 handler 落在 `${FE_STEPS_DIR}/<package>/<handler>/`（見 `step-definitions.md`）。
- Tier-1 handler **不**列入此區塊；它們永遠 enabled（由 boundary 自身規約強制）。

---

## §3 `viewport_profiles`

供 `viewport-control` handler 引用具名 viewport 的 SSOT。

```yaml
viewport_profiles:
  <profile-name>:
    width: <int>     # px, > 0
    height: <int>    # px, > 0
    deviceScaleFactor: <float>?     # optional, default 1
    isMobile: <bool>?               # optional, default false
    hasTouch: <bool>?               # optional, default false
```

**綁定規則**：

- DSL 中 `viewport-control` 的 `L4.param_bindings.profile.target` 解析至 `${TEST_STRATEGY_FILE}.viewport_profiles.<name>`。
- step file 內透過 `page.setViewportSize({width, height})` 或 `test.use({ viewport })` 套用；name → object lookup 由 fixture / step rendering 完成。
- profile name 不存在 → `prehandling-before-red-phase.md` §3.7 阻擋（transport switch sanity 同類處理）。
- 命名建議：`mobile` / `tablet` / `desktop` / `wide` / `ultrawide` / `<device-name>`；不限定列舉。

---

## §4 `time_control`

供 `time-control` handler 引用 browser-visible time 控制配置的 SSOT。為選填鍵；缺 → `time-control` handler 不可使用（DSL 若引用會被 `prehandling-before-red-phase.md` §3.7 阻擋）。

```yaml
time_control:
  mode: <freeze | tick>              # 必填
  epoch_iso: <ISO8601>               # 必填; 固定時間錨點
  tick_rate_ms: <int>?               # mode=tick only; 每真實 ms 推進 N ms; default 1
  named_instants:                    # optional; map<InstantName, ISO8601>
    <name>: <ISO8601>
```

| Mode | Playwright API | 說明 |
|---|---|---|
| `freeze` | `page.clock.install({ time: epoch_iso })` | 時間靜止於 `epoch_iso`；scenario 內時間不自動推進 |
| `tick` | `page.clock.install({ time: epoch_iso })` + `page.clock.runFor(tick_rate_ms)` | 自 `epoch_iso` 開始，每真實 ms 推進 `tick_rate_ms` ms |

**綁定規則**：

- DSL 中 `time-control` 的 `L4.source_refs.test_strategy` 解析至本檔 `time_control` 區塊。
- `named_instants.<name>` → step param binding target `test_strategy:time_control.named_instants.<name>`。
- `named_instants` 為空但 scenario step 引用具名 instant → `prehandling-before-red-phase.md` §3.7 阻擋。
- step body 不得計算時間（`now + offset` 形態必須先在 `named_instants` 宣告）。
- Playwright 版本 < 1.45 → STOP；`page.clock` 不可用，需升級或改 `none`-profile。

---

## §5 `coverage_gates`

Refactor 階段是否 enforce 三條 coverage gate。預設未啟用，避免 walking skeleton 階段就被卡。

```yaml
coverage_gates:
  operation_coverage:
    required: <bool>                # default false
    threshold: <float>              # 0.0–1.0, default 1.0
    report: <path>                  # optional override
  story_export_coverage:
    required: <bool>                # default false
    threshold: <float>              # 0.0–1.0, default 0.8
    report: <path>
  schema_field_coverage:
    required: <bool>                # default false
    threshold: <float>              # 0.0–1.0, default 0.9
    report: <path>
```

| Gate | 計算公式 | 預設 report 路徑 |
|---|---|---|
| `operation_coverage` | `|scenarios touching operationId|` / `|operationId in api.yml|` | `${PLAN_COVERAGE_REPORT_DIR}/operation-coverage.md` |
| `story_export_coverage` | `|stories bound by L4.source_refs.component|` / `|stories in ${FE_STORIES_DIR}|` | `${PLAN_COVERAGE_REPORT_DIR}/story-coverage.md` |
| `schema_field_coverage` | `|Zod schema fields touched by fixtures|` / `|total Zod schema fields|` | `${PLAN_COVERAGE_REPORT_DIR}/schema-field-coverage.md` |

**綁定規則**：

- `required: true` → `/aibdd-refactor-evaluate` 把該 gate 列入 final pass-fail 條件。
- `required: false` → gate 報告仍輸出（供觀察），但**不**阻擋 ship。
- threshold 未達 → refactor evaluator 報 `coverage_gate_below_threshold`，回 refactor worker 修正。

---

## §6 `policies`

Spec-by-Example 動態填入；非 boundary preset 範圍。Schema 定義在 `aibdd-spec-by-example-analyze` 自身的 references。本檔不重抄；`policies: {}` 為 kickoff 起始值。

---

## §7 完整範例

最小可用版本（首個 feature package 落地時）：

```yaml
version: 1
tier2_handlers:
  api-stub: disabled
  url-then: disabled
  api-call-then: enabled        # 例：scenario 要驗 createBorrowRequest 觸發
  mock-state-then: disabled
viewport_profiles:
  mobile:  { width: 375,  height: 667  }
  desktop: { width: 1440, height: 900  }
coverage_gates: {}              # 全部未啟用
policies: {}
```

進階版本（refactor gate 全開）：

```yaml
version: 1
tier2_handlers:
  api-stub: enabled
  url-then: enabled
  api-call-then: enabled
  mock-state-then: enabled
viewport_profiles:
  mobile:  { width: 375,  height: 667  }
  tablet:  { width: 768,  height: 1024 }
  desktop: { width: 1440, height: 900  }
  wide:    { width: 1920, height: 1080 }
coverage_gates:
  operation_coverage:    { required: true,  threshold: 1.0 }
  story_export_coverage: { required: true,  threshold: 0.8 }
  schema_field_coverage: { required: false, threshold: 0.9 }
policies:
  P1: { ... }   # by /aibdd-spec-by-example-analyze
```

---

## §8 Forbidden

- 重抄 Tier-1 handler 到 `tier2_handlers`（Tier-1 永遠 enabled，列出來會誤導 enablement 檢查）。
- 在 `viewport_profiles` 內寫入非 `width` / `height` / `deviceScaleFactor` / `isMobile` / `hasTouch` 之外的鍵（會被 Playwright `viewport` 型別 reject）。
- `coverage_gates.<gate>.report` 寫絕對路徑（破壞 `${PLAN_COVERAGE_REPORT_DIR}` 抽象）。
- 在 `policies` 內手寫 Spec-by-Example clause 結構（必須由 `/aibdd-spec-by-example-analyze` 產出）。
- 把 `version` 升到 `2` 而本檔還停在 `1` 規約 —— schema bump 須先修訂本檔再升版。
- 在 `time_control` 內寫入 `mode` 以外的計算性欄位（如 `offset_ms`、`relative_to`）—— 所有計算必須先在 `named_instants` 宣告靜態錨點。
