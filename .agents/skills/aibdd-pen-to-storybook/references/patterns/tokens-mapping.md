# Pattern — Tokens Mapping (`.pen` variables → Tailwind 4 `@theme`)

> 純 declarative reference。Phase 3 LOAD 取 namespace lookup table。

## §1 對照表

| `.pen` variable `type` | name 線索 | Tailwind 4 namespace | 自動派生 utility |
|---|---|---|---|
| `color` | — | `--color-<name>` | `bg-<name>` / `text-<name>` / `border-<name>` / `fill-<name>` / `ring-<name>` |
| `string` | font family | `--font-<role>` | `font-<role>` |
| `number` | name 含 `radius` | `--radius-<name>` | `rounded-<name>` |
| `number` | name 含 `spacing` 或 `gap` | `--spacing-<name>` | `p-<name>` / `m-<name>` / `gap-<name>` / `space-x-<name>` / `space-y-<name>` |
| `number` | 其他 | `--<name>`（custom var） | 透過 `var(--<name>)` 在 CSS 內手動取用；不自動派生 utility |
| `boolean` | — | **SKIP** | 由 component code 讀取，不入 Tailwind |

## §2 Phase 3 LOOP 推導順序

對每筆 `(var_name, var_def)` in `Document.variables`：

1. BRANCH `var_def.type`
   - `color`     → `namespace = "--color-"`
   - `string`    → `namespace = "--font-"`
   - `number`    → 走 §3 sub-decision
   - `boolean`   → SKIP，直接下一筆
2. `entry = { name: var_name, namespace, value: var_def.value }`
3. APPEND to `$$tokens`

## §3 Number sub-decision

```
IF lowercased(var_name) contains "radius":
  namespace = "--radius-"
ELSE IF lowercased(var_name) contains "spacing" OR "gap":
  namespace = "--spacing-"
ELSE:
  namespace = "--"  # custom CSS var；不接 Tailwind utility 派生
```

`number` 變數只有上面三種會落到 `@theme` 自動派生 utility；其他（如 `--z-toast`、`--duration-fast`）走 custom var 路徑，由 component code 用 `var(...)` 引用。

## §4 Theme-aware value 處理

`var_def.value` 可能是：

- scalar：直接寫進 `@theme`
- array of `{ value, theme }`：本 skill 取**第一個** scalar 值；多主題切換不在此 skill scope（需另起 multi-theme reference）

## §5 Output schema（`$$tokens`）

```yaml
$$tokens:
  - name: "accent-cyan"
    namespace: "--color-"
    value: "#00E5FF"
  - name: "mono"
    namespace: "--font-"
    value: '"JetBrains Mono", ui-monospace, monospace'
  - name: "cipher"
    namespace: "--radius-"
    value: "10px"
  - name: "section"
    namespace: "--spacing-"
    value: "32px"
```

## §6 Phase 6 RENDER 對照

`globals.css` `@theme { ... }` 區塊 RENDER 規則：每筆 `$$tokens[i]`：

```css
{namespace}{name}: {value};
```

例：

```css
@theme {
  --color-accent-cyan: #00E5FF;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --radius-cipher: 10px;
  --spacing-section: 32px;
}
```

## §7 Edge cases

- **8-digit hex (RGBA)** — 直接寫進 `--color-<name>: #AABBCCDD;`，Tailwind 會傳遞
- **font-family 含逗號 / 空格** — value 用雙引號包：`"JetBrains Mono", ui-monospace, monospace`
- **kebab-case 衝突** — 若兩個變數同名（不同主題），Phase 3 取第一筆並警示 caller；本 skill 不自動 disambiguate
- **空值 / null** — SKIP 該筆，不寫進 `@theme`
