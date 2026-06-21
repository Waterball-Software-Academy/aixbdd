# NON_INTERACTIVE 由 caller 注入

## Rule 1 — NON_INTERACTIVE 是被注入的事實，不是要問 user 的問題

- `NON_INTERACTIVE` 反映「這次呼叫有沒有真人在線上回答」，由 caller 的執行情境決定，不是使用者偏好。判定來源固定三條，任一成立即 `true`：caller payload 帶 `non_interactive: true`、帶 `defaults_profile: happy-path`、或落在 headless sandbox（如 `.tests/<scenario>/before`）。向 user 反問「要 interactive 還是 happy-path」會在 headless／CI 情境直接卡死流程——那裡沒有人能回答。此 flag 必須推導，永遠不能用問的。

### ✅ Good

情境：caller payload 帶 defaults_profile

```json
{ "project_root": "/work/repo", "defaults_profile": "happy-path" }
```

→ DERIVE NON_INTERACTIVE = true（命中 happy-path），直接走 default decisions，不發任何問題。

### ❌ Bad

```
payload 無旗標、身處 .tests/checkout/before sandbox：
AI：「請問你想用 interactive 模式還是 happy-path 預設？」
（sandbox 無真人 → 永久等待 / 流程 hang）
```

**預期改法**
- 偵測到 `.tests/<scenario>/before` → DERIVE NON_INTERACTIVE = true，套 default decisions，完全不問。
