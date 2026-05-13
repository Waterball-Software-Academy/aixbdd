# Pattern — `.pen` 節點樹 → 巢狀 JSX + Tailwind 4 utility class

> 純 declarative reference。Phase 6 DERIVE render plan 與 Phase 7 RENDER component 時 LOAD 取規則。
>
> 目標：把已偵測為 component 的 `.pen` 子樹翻成**可直接 ship 的視覺實作**（React 19 + Next.js 16 + Tailwind 4），
> caller 不需要再給 `render_hints`。

## §1 .pen node type → JSX tag mapping

| `.pen` type | JSX tag | 備註 |
|---|---|---|
| `frame` (root of detected component) | `<section>` / `<div>` / `<form>` / `<label>` / `<button>` | 依 §1.1 root inference 規則 |
| `frame` (nested container) | `<div>` | 預設容器 |
| `group` | `<div>` | 純 grouping，無語意意涵 |
| `rectangle` (純色塊背景，無 children) | `<div>` | 視為 visual chrome；若有子節點則升為 container |
| `text` | `<span>` (default) / `<h1>..<h6>` / `<p>` / `<label>` | 依 §1.2 text role inference |
| `icon_font` | `<span aria-hidden="true">` + lucide-react 字元 / Material symbol | 詳見 §5 |
| `ellipse` / `polygon` / `line` / `path` | `<svg>` 內 `<circle>` / `<polygon>` / `<line>` / `<path>` | inline SVG；caller 視需求自決是否抽 `<Icon>` |
| `note` / `prompt` / `context` / `script` | **SKIP** | author-time annotation，不渲染 |
| `ref` (instance) | `<${refComponentId} {...props} />` | 巢狀引用其他 detected component |

### §1.1 Root element inference（detected component 的根 JSX 元素）

依下列順序套用，先命中即用：

1. component 子樹根節點 `name` 含 `form` / 含 `<input>` text 子節點 → `<form>`
2. component 子樹根節點 `name` 含 `button` 或 `cta`，且整個子樹只有一個可見 text → `<button type="button">`
3. component 子樹根節點 `name` 含 `label` 且包一個 input-like 子樹 → `<label>`
4. component 子樹根節點為單一可互動 input（`name` 含 `input` / `field` / `entry`） → `<input>` (`<label>` 包外層)
5. 子樹含 heading-like 大字 text + 多個 children → `<section aria-label="<name>">`
6. 其他 → `<div>`

### §1.2 Text role inference

依字級 / 字重 / 父節點推導：

| 條件 | JSX tag |
|---|---|
| `fontSize >= 32` 且為 component 內最大字級 | `<h2>` |
| `fontSize >= 24` 且為子段標題 | `<h3>` |
| `fontSize >= 16` 且 fontWeight >= 600 | `<strong>` |
| 父節點為 `<label>` 且 text 為其首個 child | `<span>` (visible label 文字；瀏覽器自動關聯 `<input>`) |
| 父節點為 `<button>` | `<>` (button child text，無額外 tag) |
| 多行段落文字（textGrowth=fixed-width 且 content 含換行） | `<p>` |
| 其他 | `<span>` |

## §2 .pen layout → Tailwind flex / spacing utility

| `.pen` 屬性 | Tailwind 4 class |
|---|---|
| `layout: "horizontal"` | `flex flex-row` |
| `layout: "vertical"` | `flex flex-col` |
| `layout: "none"` | _(無 flex；absolutely positioned children；本 skill 推薦避開)_ |
| `gap: <n>` | `gap-[<n>px]` 或對齊 token：`gap-<token-name>`（若 `--spacing-<name>` 存在） |
| `padding: <n>` | `p-[<n>px]` 或對齊 token：`p-<token-name>` |
| `padding: [h, v]` | `px-[<h>px] py-[<v>px]` |
| `padding: [t, r, b, l]` | `pt-[..] pr-[..] pb-[..] pl-[..]` |
| `justifyContent: "start"` | `justify-start` |
| `justifyContent: "center"` | `justify-center` |
| `justifyContent: "end"` | `justify-end` |
| `justifyContent: "space_between"` | `justify-between` |
| `justifyContent: "space_around"` | `justify-around` |
| `alignItems: "start"` | `items-start` |
| `alignItems: "center"` | `items-center` |
| `alignItems: "end"` | `items-end` |

### §2.1 width / height

| `.pen` value | Tailwind class |
|---|---|
| 數字 `<n>` | `w-[<n>px]` / `h-[<n>px]` |
| `fit_content` | `w-fit` / `h-fit` |
| `fill_container` | `w-full` / `h-full`（parent 為 flex 時）；若 parent flex 軸 main = horizontal，子節點實際渲染為 `flex-1` |
| `fit_content(<fallback>)` | `w-fit min-w-[<fallback>px]`（容器約束 fallback） |

## §3 .pen graphics → Tailwind utility

### §3.1 Fill

| `.pen` fill | Tailwind class |
|---|---|
| `Color "$<token>"` | `bg-<token>`（必須 `--color-<token>` 存在於 `@theme`） |
| `Color "#RRGGBB"` | `bg-[#RRGGBB]` |
| `Color "#RRGGBBAA"` | `bg-[#RRGGBBAA]` |
| `gradient` linear | `bg-gradient-to-<dir> from-<start> to-<end>`（取 colors[0] 與 colors[-1]；中段 stop 略） |
| `gradient` radial / angular | 退化為 first color：`bg-<color>`（複雜漸層不在自動派生範圍，warn caller） |
| `image` | `bg-[url('<url>')] bg-<mode>`（mode 對應 `stretch/fill/fit` → `bg-cover/bg-contain/bg-fill`） |
| `mesh_gradient` | 退化為 colors 平均：取 colors[0]；warn caller |

### §3.2 Stroke

| `.pen` stroke | Tailwind class |
|---|---|
| `thickness: <n>` + `fill: $<token>` | `border-[<n>px] border-<token>` |
| `align: "inside"` | _(Tailwind 預設即 inside；無對應 class)_ |
| `align: "outside"` | `box-content`（讓 padding 不含 border） |
| `dashPattern: [4,4]` | `border-dashed`（pattern 精度退化；warn caller） |

### §3.3 Corner radius

| `.pen` cornerRadius | Tailwind class |
|---|---|
| 數字 `<n>` | `rounded-[<n>px]` 或對齊 token：`rounded-<token>` |
| `[tl, tr, br, bl]` | `rounded-tl-[..] rounded-tr-[..] rounded-br-[..] rounded-bl-[..]` |
| `9999` 或 `width / 2` | `rounded-full` |

### §3.4 Effect

| `.pen` effect | Tailwind class |
|---|---|
| `blur radius: <n>` | `blur-[<n>px]` |
| `background_blur radius: <n>` | `backdrop-blur-[<n>px]` |
| `shadow type: outer` | `shadow-[<offset>_<blur>_<color>]` 或對齊 token：`shadow-<token>` |
| `shadow type: inner` | `shadow-inner` (簡化；複雜 inner shadow warn caller) |

## §4 Text style → Tailwind typography

| `.pen` TextStyle | Tailwind class |
|---|---|
| `fontFamily: "$<name>"` | `font-<name>`（`--font-<name>` 須存在） |
| `fontSize: <n>` | `text-[<n>px]` |
| `fontWeight: "700"` | `font-bold`（500=`medium`、600=`semibold`、700=`bold`、800=`extrabold`） |
| `fontStyle: "italic"` | `italic` |
| `underline: true` | `underline` |
| `strikethrough: true` | `line-through` |
| `letterSpacing: <n>` | `tracking-[<n>px]` |
| `lineHeight: <n>` | `leading-[<n>]`（multiplier）或 `leading-[<n>px]` |
| `textAlign: "center"` | `text-center` |
| `textAlign: "right"` | `text-right` |
| `textAlign: "justify"` | `text-justify` |
| `fill: "$<token>"` | `text-<token>` |
| `fill: "#RRGGBB"` | `text-[#RRGGBB]` |

## §5 IconFont 處理

`.pen` `icon_font` 節點（`iconFontFamily: "lucide" / "Material Symbols Rounded" / "phosphor"` 等）：

```tsx
import { Check } from "lucide-react";
...
<Check className="w-4 h-4 text-accent" aria-hidden="true" />
```

對照規則：

| `.pen` iconFontFamily | import 來源 |
|---|---|
| `lucide` / `feather` | `lucide-react`（icon name PascalCase from `iconFontName`） |
| `Material Symbols *` | `<span className="material-symbols-rounded">...</span>`（caller scaffold 須引入 webfont） |
| `phosphor` | `@phosphor-icons/react`（icon name PascalCase） |

icon 不擔任語意角色：補 `aria-hidden="true"`，accessible name 由旁邊 text / 容器 aria-label 提供。

## §6 Token 引用規則

- Tailwind class **優先**用 token name（`bg-accent` / `text-text` / `rounded-cipher`），fallback 才用 arbitrary value（`bg-[#00E5FF]`）。
- 本 skill 在 Phase 3 已抽 `$$tokens`；Phase 6/7 LOOK UP 對應 token name；找不到對應 token 時降級 arbitrary value。
- **不**寫 CSS variable 名（`--color-accent`）進 className — Tailwind 4 utility 直接吃 token base name。

## §7 巢狀規則

- parent `.pen` 用 flex → JSX className 加 `flex flex-{row|col}`；child JSX 不需自己加 flex（除非 child 本身也是 layout container）。
- parent `.pen` 用 `layout: "none"`（絕對定位）→ JSX className 加 `relative`，child 加 `absolute left-[..] top-[..]`。**不推薦**，本 skill 在無法用 flex 時才退此路。
- 巢狀 `frame` → 巢狀 `<div>`，逐層套 class；不展平。
- `ref` 節點 → 該檔內以「同檔 import 鄰近 component」的方式渲染：
  ```ts
  import { ChildComponent } from "../ChildComponent/ChildComponent";
  ```
  本 skill 假設 `ref.ref` 指向的也是 detected component（在同次 batch 寫出）。若 `ref` 指向 non-detected node，warn caller。

## §8 命名與檔案規則

- Component identifier：PascalCase from `.pen` node name（去掉 `comp/` / `Component/` / `cmp/` 前綴、駝峰化、首字母大寫）。
- 檔案路徑：`${target_dir}/<Identifier>/<Identifier>.tsx`（**目錄與檔名同名**，無 `index.tsx`）。
- Props 名：camelCase from heuristics 推導的 `derived_from` 線索；不出現 React 內建型別字串如 `React.FC`。
- 強制條款：
  - `export type ${id}Props = { ... };` named export
  - `export function ${id}(props: ${id}Props)` named export
  - 無 `import React`
  - 無 `import { clsx } from "clsx"` / `import { cn } from "..."`（className 為純字串字面量 join）
  - 無 hooks / 無 IO / 無 default param assignment（這些屬 green-execute）

## §9 反例

```tsx
// ❌ JSON.stringify(props) placeholder — 本 skill 不接受 fallback placeholder
return <pre>{JSON.stringify(props, null, 2)}</pre>;

// ❌ 用 clsx / cn 串 className
return <div className={clsx("flex", disabled && "opacity-50")}>...</div>;

// ❌ 寫死 CSS variable 進 className
return <div className="bg-[var(--color-accent)]">...</div>;

// ❌ 引入 React
import React from "react";

// ❌ default export
export default function LobbyRoomEntry() {...}

// ❌ React.FC
export const LobbyRoomEntry: React.FC<Props> = (props) => {...};

// ❌ 寫 hooks（屬 green-execute）
const [code, setCode] = useState("");

// ❌ 寫死 IO（屬 green-execute）
useEffect(() => { fetch("/api/rooms"); }, []);

// ❌ default param assignment
export function LobbyRoomEntry({ title = "1A2B" }: Props) {...}
//                                    ^^^ runtime default 屬 green
```

## §10 對齊 boundary I4

- 每個 detected component 的根 JSX 元素必須能 expose 一個 ARIA role（`<button>` / `<input>` / `<form>` 等天然帶 role；自訂容器加 `aria-label` 或 role attribute）。
- accessible-name 必須來自 props 而非寫死 — Phase 6 step 6.5 已 ASSERT。
- 違反此規則的 component → Phase 6 dispatch `accessible-name-prop-missing`，caller 需回 `.pen` 補可見文字節點。
