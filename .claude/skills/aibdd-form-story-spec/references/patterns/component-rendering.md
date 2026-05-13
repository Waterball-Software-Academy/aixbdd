# Pattern — React component .tsx 渲染規約

> 純 declarative reference。Phase 2A RENDER 時 LOAD 取規則。
>
> 對齊 `aibdd-pen-to-storybook` Phase 7 的 component 渲染慣例（Next.js 16 + React 19 + Tailwind 4），但本 skill 走 caller-driven payload 路徑，不直接讀 .pen。

## §1 為什麼一檔包 component + Props + 函式 export

`aibdd-form-story-spec` 必須產出兩個共生檔，story 端用相對 import 引用 component：

```ts
// <identifier>.stories.tsx
import { RoomCodeInput } from "./RoomCodeInput";
```

→ component 端必須 named export 同名 PascalCase 函式 + Props interface。
→ 兩檔同 target_dir co-located；caller 推導 `target_dir` 為 `${TRUTH_BOUNDARY_ROOT}/contracts/components/<ComponentId>/`，story import 路徑固定為 `./<ComponentId>`。

## §2 必備檔案結構

```tsx
export type RoomCodeInputProps = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function RoomCodeInput(props: RoomCodeInputProps) {
  return (
    <input className="bg-surface-2 text-text rounded-sharp" />
  );
}
```

### 強制條款

| 條款 | 說明 |
|---|---|
| `export type ${id}Props` | TypeScript Props interface；命名固定為 `<Identifier>Props` |
| `export function ${id}(props: ${id}Props)` | named export 函式；不用 `export default`、不用 `React.FC` |
| 無 `import React` | React 19 + Next 16 自動 JSX runtime；多餘的 import 由 ESLint flag |
| 無 `import { clsx }` / `import { cn }` | className 字串由 caller 在 `render_hints.base_class` 預先解析；本 skill 不引入 utility lib |
| 無 hooks (`useState` / `useEffect` / `useMemo` / `useReducer` / `useContext`) | form-story-spec 只寫純展示元件；stateful 行為屬 `/aibdd-green-execute` |
| 無 IO (`fetch` / `axios` / `XMLHttpRequest`) | 同上；data fetching 屬 green-execute |
| 無 default param assignment | `props.value ?? "default"` 也禁；default value 進 Props comment 即可 |

## §3 children_layout = "labeled-input"

當 `render_hints.children_layout == "labeled-input"`，render 出 `<label>` 包 `<input>` 結構。
`render_hints.accessible_name_prop` 指明哪個 prop 是可見 label 文字。

```tsx
// caller payload:
//   render_hints:
//     root_element: "label"        # ignored；labeled-input 強制用 <label>
//     children_layout: "labeled-input"
//     base_class: "flex flex-col gap-2"
//     accessible_name_prop: "label"
//   props:
//     - { name: "label", type: "string", required: true }
//     - { name: "value", type: "string", required: true }
//     - { name: "onChange", type: "(value: string) => void", required: true }

export type RoomCodeInputProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
};

export function RoomCodeInput(props: RoomCodeInputProps) {
  return (
    <label className="flex flex-col gap-2">
      <span>{props.label}</span>
      <input
        type="text"
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
      />
    </label>
  );
}
```

### labeled-input 規則

- `<label>` 為 root（不論 `root_element` 設什麼，labeled-input 強制 `<label>`）
- `<label>` 套 `base_class`
- `<span>{props[accessible_name_prop]}</span>` 為 visible text；對應的 prop 必須 `type: "string"`
- `<input>` 預設 `type="text"`、`value={props.value}`、`onChange={(e) => props.onChange(e.target.value)}`；
  caller 必須提供 `value: string` 與 `onChange: (value: string) => void` 兩個 props，否則 ASSERT 失敗
- DOM accessible name 由瀏覽器從 `<label>` 自動關聯到 `<input>`；step-def 用 `getByRole("textbox", { name: <label value> })` 鎖定

## §4 children_layout = "button"

```tsx
// caller payload:
//   render_hints:
//     children_layout: "button"
//     base_class: "bg-accent text-text-on-accent rounded-sharp px-4 py-2"
//     accessible_name_prop: "label"
//     button_type: "submit"
//   props:
//     - { name: "label", type: "string", required: true }
//     - { name: "onClick", type: "() => void", required: false }
//     - { name: "disabled", type: "boolean", required: false }

export type SubmitButtonProps = {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
};

export function SubmitButton(props: SubmitButtonProps) {
  return (
    <button
      type="submit"
      className="bg-accent text-text-on-accent rounded-sharp px-4 py-2"
      onClick={props.onClick}
      disabled={props.disabled}
    >
      {props.label}
    </button>
  );
}
```

### button 規則

- `<button>` 為 root；`type` 從 `render_hints.button_type` 取（default `"button"`）
- `{props[accessible_name_prop]}` 為按鈕文字；step-def 用 `getByRole("button", { name: <label value> })` 鎖定
- caller 提供的 `onClick` / `disabled` 等 optional props 自動 wire 到 button attributes（若 prop 名稱對齊 HTML attribute 名稱）

## §5 children_layout = "leaf"

最簡單形式 — 自閉節點，無 children。

```tsx
// caller payload:
//   render_hints:
//     root_element: "input"
//     children_layout: "leaf"
//     base_class: "border border-border rounded-sharp"
//   props:
//     - { name: "value", type: "string", required: true }
//     - { name: "placeholder", type: "string", required: false }

export type RoomCodeInputProps = {
  value: string;
  placeholder?: string;
};

export function RoomCodeInput(props: RoomCodeInputProps) {
  return (
    <input className="border border-border rounded-sharp" />
  );
}
```

注意：leaf pattern 不自動 wire props 到 attributes —— 因為本 skill 不知道 prop 是否對應 HTML attribute。
caller 若需要 `value` / `placeholder` attribute binding，請改用更具體的 layout（如 `labeled-input`），或在 green-execute 階段補完。

## §6 children_layout = "container"

```tsx
// caller payload:
//   render_hints:
//     root_element: "section"
//     children_layout: "container"
//     base_class: "flex flex-col gap-4 p-6"
//   props:
//     - { name: "children", type: "React.ReactNode", required: true }

export type CardProps = {
  children: React.ReactNode;
};

export function Card(props: CardProps) {
  return (
    <section className="flex flex-col gap-4 p-6">
      {props.children}
    </section>
  );
}
```

container 強制 `props.children` 存在；ASSERT `children: React.ReactNode` 在 props list 中。

## §7 children_layout = "text"

最寬鬆形式 — 容器 + optional children。

```tsx
export type LabelProps = {
  children?: React.ReactNode;
};

export function Label(props: LabelProps) {
  return <span className="text-dim">{props.children ?? null}</span>;
}
```

## §8 className 處理規則

- `base_class` 為**完整 Tailwind class 字串**（caller 預先從 design tokens 解析）
- 本 skill **不**做 token resolution；不認識 `--color-accent` 之類的 CSS variable
- 本 skill **不**注入 `clsx` / `cn` / `tw` utility；className 直接寫字串字面量
- 本 skill **不**做條件 className（如 `disabled ? "opacity-50" : ""`）；那屬 green-execute

## §9 反例

```tsx
// ❌ 引入 React（React 19 自動 JSX runtime）
import React from "react";

// ❌ default export
export default function Button() { ... }

// ❌ 用 React.FC
export const Button: React.FC<ButtonProps> = (props) => { ... };

// ❌ hooks（屬 green-execute）
import { useState } from "react";
export function Counter() {
  const [n, setN] = useState(0);
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}

// ❌ data fetching（屬 green-execute）
export function UserCard({ id }: Props) {
  const [user, setUser] = useState(null);
  useEffect(() => { fetch(`/api/users/${id}`).then(...).then(setUser); }, [id]);
  return <div>{user?.name}</div>;
}

// ❌ clsx / 條件 className
import { clsx } from "clsx";
export function Button({ disabled }: Props) {
  return <button className={clsx("btn", disabled && "btn-disabled")}>...</button>;
}

// ❌ default param assignment
export function Card({ title = "Untitled" }: Props) {
  return <div>{title}</div>;
}

// ❌ token name 寫進 className（caller 沒解析）
return <div className="bg-[var(--color-accent)]" />;
//      ↑ caller 應在 base_class 預先解析為 "bg-accent"
```

## §10 對齊 boundary I4

component 端的 prop 名稱必須包含 caller 在 stories 端宣告的 `accessible_name_arg.field`。
否則 story 寫 `args: { label: "Submit" }` 但 component 沒 `label` prop → TypeScript 編譯失敗。

Phase 1 step 21.7 ASSERT 此一致性。
