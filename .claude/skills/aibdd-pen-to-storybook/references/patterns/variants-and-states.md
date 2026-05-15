# Pattern — Variants / States：detection enum → conditional className + 一狀態一 story

> 純 declarative reference。Phase 6 DERIVE render plan、Phase 7 RENDER component、Phase 8 RENDER stories 時
> LOAD 取規則。
>
> 與 [`component-detection.md`](component-detection.md) 是配對：detection 抽 enum，本 doc 規範如何渲染。

## §1 哪些差異值得拆 variant / state

| detection heuristic 命中 | 推導 prop | 拆 story 嗎 |
|---|---|---|
| H2（numeric-suffix） | `variant` / `index` enum | 是 — 每個 enum 值一個 story |
| H3（prefix grouping） | `kind` × `count` 雙 enum | 是 — 主 axis（kind）每值一 story |
| H4（同 subtree 不同 content） | `label` / `title` / `description` string | 否 — 只是 content prop，args 帶值即可 |
| H5（同 subtree 不同 fill/text-color） | `state` enum | 是 — 每個 enum 值一 story |
| H1 / H6（顯式 component） | 依視覺差異另行 detect | 是 — 一個 default + observable variant |

## §2 Conditional className 渲染規則

### §2.1 三段式串接

className 由三段純字串 join：

```ts
const className = [
  baseClass,                     // §3.1 .pen 節點通用視覺
  variantClass[props.variant],   // §3.2 variant axis 對應的 className diff
  stateClass[props.state],       // §3.3 state axis 對應的 className diff
].filter(Boolean).join(" ");
```

- 三段都是**字面量字串**（無模板字串、無 `clsx` / `cn`）。
- `filter(Boolean)` 排除 undefined / 空字串；不是條件邏輯，是 join 衛生。

### §2.2 變數宣告位置

- `baseClass` 為 function 內 `const`，**不是** prop。
- `variantClass` / `stateClass` 為 module-level `const`（function 外宣告），對應 enum literal union。

```tsx
const baseClass = "flex flex-col gap-4 p-6 rounded-cipher bg-surface";

const variantClass: Record<ButtonVariant, string> = {
  primary: "bg-accent text-text-on-accent",
  secondary: "bg-surface-2 text-text",
  ghost: "bg-transparent text-accent",
};

const stateClass: Record<ButtonState, string> = {
  default: "",
  loading: "opacity-70 cursor-progress",
  disabled: "opacity-50 cursor-not-allowed pointer-events-none",
};

export function SubmitButton(props: SubmitButtonProps) {
  const className = [baseClass, variantClass[props.variant], stateClass[props.state]]
    .filter(Boolean)
    .join(" ");
  return <button type="button" className={className}>{props.label}</button>;
}
```

### §2.3 enum 缺值處理

- props type 用 string literal union（`"primary" | "secondary" | "ghost"`），TypeScript 編譯期保證窮舉。
- `variantClass` map 必須涵蓋每個 union 值；缺值 → Phase 7 ASSERT 失敗。
- 預設值不在本 skill 補（屬 green-execute）；caller 使用時自己給。

## §3 className 對應規則（detection enum → Tailwind diff）

### §3.1 baseClass — 共通視覺

從 detected component 的 canonical instance 取所有節點都共享的 graphics / layout：
- 結構性 class（`flex`、`gap-*`、`p-*`、`rounded-*`）→ base
- 共享的 fill / stroke / text color → base
- 變動的 fill / text color → variant 或 state map

### §3.2 variantClass — variant axis

對應 H2 / H3 detection heuristic 抽出的 enum。

```yaml
# detection 結果
variant_axis: "kind"
enum_values: ["A", "B"]
diff_features:
  A: { fill: "$accent" }
  B: { fill: "$accent-secondary" }
```

→ 對應渲染：

```ts
const variantClass: Record<ResultKind, string> = {
  A: "bg-accent text-text-on-accent",
  B: "bg-accent-secondary text-text-on-accent",
};
```

### §3.3 stateClass — state axis

對應 H5 detection heuristic 抽出的 enum（fill / opacity / pointer-events 差異）。

```yaml
state_axis: "state"
enum_values: ["default", "active", "disabled", "error", "success"]
diff_features:
  default:  {}
  active:   { fill: "$accent",  opacity: 1 }
  disabled: { opacity: 0.5 }
  error:    { fill: "$danger",  text_color: "$text-on-danger" }
  success:  { fill: "$success", text_color: "$text-on-success" }
```

→ 對應渲染：

```ts
const stateClass: Record<PlayerCardState, string> = {
  default:  "",
  active:   "bg-accent opacity-100",
  disabled: "opacity-50",
  error:    "bg-danger text-text-on-danger",
  success:  "bg-success text-text-on-success",
};
```

## §4 一 variant/state = 一 story export

### §4.1 命名規則

- 用**狀態名詞**或**形容詞**：`Default` / `Loading` / `Empty` / `WithError` / `Disabled` / `Active`
- 不用**動詞片語**：避免 `ClickToSubmit` / `WhenLoaded`
- 不用**版本號**：避免 `V2` / `New`

### §4.2 推薦上限

每個 component 3–6 個 story exports；> 6 通常表示該抽成兩個 component 或 axis 太多。

### §4.3 Detection-driven 自動生成

Phase 8 對每個 detected variant / state 自動生成 story export：

```tsx
// detected variant: "primary" | "secondary" | "ghost"
// detected state:   "default" | "loading" | "disabled"
// detection 給 6 個 observed combos → 6 個 stories

export const Primary: Story = {
  args: { label: "Submit", variant: "primary", state: "default" },
};
export const PrimaryLoading: Story = {
  args: { label: "Submitting…", variant: "primary", state: "loading" },
};
export const Secondary: Story = {
  args: { label: "Cancel", variant: "secondary", state: "default" },
};
// ... etc
```

### §4.4 不展開的 combos

不要做笛卡兒積展開（3 variant × 3 state = 9 stories）。只 emit **detection 階段在 `.pen` 觀察到的 combo**。
沒在 `.pen` 出現 = 設計者沒設計 = 沒 BDD 收斂需求。

## §5 與 BDD scenario 的對齊

- 每個 story export 對應一或多個 BDD scenario 的 `Given <state>` 預設條件。
- step-def 透過 story args 派生 locator；同一 component 不同 state 透過切換 story 而非 mutate state。
- Stories 數量超過實際 BDD 涵蓋 → caller 該重新收斂 scenarios 或裁減 variant。

## §6 反例

```tsx
// ❌ clsx 串條件 className
const className = clsx(baseClass, {
  "bg-accent": variant === "primary",
  "opacity-50": state === "disabled",
});

// ❌ 模板字串組合
const className = `${baseClass} ${variant === "primary" ? "bg-accent" : ""}`;

// ❌ 把 variant 邏輯寫進 JSX 內聯三元
return <button className={`btn ${props.disabled ? "btn-disabled" : ""}`}>...</button>;

// ❌ 把 state 邏輯藏到 hook
const className = useVariantClass(props.variant, props.state);  // hooks 禁用

// ❌ 笛卡兒積 stories
// 9 個 stories：PrimaryDefault / PrimaryLoading / PrimaryDisabled / SecondaryDefault / ...
// 但 .pen 只設計了其中 4 個 → 多 emit = 偽 truth
```
