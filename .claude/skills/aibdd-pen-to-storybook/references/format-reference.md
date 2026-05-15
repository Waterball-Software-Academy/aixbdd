# Format Reference — `.pen` v2.x JSON schema + framework version locks

> 純 declarative reference。Phase 2 LOAD 取 schema 結構作 PARSE 守門；Phase 7 RENDER 時對照 type → React idiom 映射。
>
> Source of truth：`https://docs.pencil.dev/for-developers/the-pen-format#typescript-schema`。

## §1 檔案性質

- `.pen` 為 **UTF-8 plain-text JSON**（非 binary、非 zip）；可用 `python3 scripts/python/pen_query.py` / `node` / `cat` 直接讀。本 skill SOP 一律走 `pen_query.py` wrapper，不再依賴 `jq` 命令。
- `Document.version` 為 `"2.x"` 字串；新增屬性向後相容。當前文件版本為 `"2.10"`，真實檔案可能已 `"2.11"`+。
- 任何 `id` **MUST NOT** 含 `/` — slash 在 `ref.descendants` path 內保留。

## §2 Top-level document

```ts
export interface Document {
  version: "2.10";
  themes?: { [key: string]: string[] };
  imports?: { [key: string]: string };
  variables?: {
    [key: string]:
      | { type: "boolean"; value: BooleanOrVariable | { value: BooleanOrVariable; theme?: Theme }[] }
      | { type: "color";   value: ColorOrVariable   | { value: ColorOrVariable;   theme?: Theme }[] }
      | { type: "number";  value: NumberOrVariable  | { value: NumberOrVariable;  theme?: Theme }[] }
      | { type: "string";  value: StringOrVariable  | { value: StringOrVariable;  theme?: Theme }[] };
  };
  children: (
    | Frame | Group | Rectangle | Ellipse | Line | Polygon | Path
    | Text | Note | Context | Prompt | IconFont | Ref
  )[];
}
```

`children[*]` 即 top-level frames / screens / detached groups。Phase 4 從這裡選 `screen_id`。

## §3 Variable binding 語法

- 變數綁定為 **dollar-prefixed string**：`"fill": "$accent-cyan"`（NOT `{ ref: "accent-cyan" }`）
- Phase 3 抽 token 時，**只**讀 `Document.variables`；frame 內 `$xxx` reference 不入 `@theme`，僅作為 CSS 變數查表用。
- `variables[*].value` 可為 scalar 或 theme-aware array：`[{value: "#000", theme: {device: "phone"}}, ...]`。本 skill
  目前只取第一個 scalar 值；多主題需求需擴 reference。

## §4 Node types — TypeScript schema verbatim

```ts
/** Each key must be an existing theme axis. E.g. { 'device': 'phone' } */
export interface Theme { [key: string]: string; }

export type Variable = string;
export type NumberOrVariable = number | Variable;

/** 8-digit RGBA (#AABBCCDD) | 6-digit RGB (#AABBCC) | 3-digit (#ABC → #AABBCC) */
export type Color = string;
export type ColorOrVariable = Color | Variable;
export type BooleanOrVariable = boolean | Variable;
export type StringOrVariable = string | Variable;

export interface Layout {
  /** None = absolute children. Frames default horizontal, groups default none. */
  layout?: "none" | "vertical" | "horizontal";
  gap?: NumberOrVariable;
  layoutIncludeStroke?: boolean;
  padding?:
    | NumberOrVariable
    | [NumberOrVariable, NumberOrVariable]
    | [NumberOrVariable, NumberOrVariable, NumberOrVariable, NumberOrVariable];
  justifyContent?: "start" | "center" | "end" | "space_between" | "space_around";
  alignItems?: "start" | "center" | "end";
}

/** fit_content / fill_container, with optional fallback like 'fit_content(100)' */
export type SizingBehavior = string;

export interface Position { x?: number; y?: number; }
export interface Size {
  width?: NumberOrVariable | SizingBehavior;
  height?: NumberOrVariable | SizingBehavior;
}
export interface CanHaveRotation { rotation?: NumberOrVariable; }

export type BlendMode =
  | "normal" | "darken" | "multiply" | "linearBurn" | "colorBurn"
  | "light"  | "screen" | "linearDodge" | "colorDodge" | "overlay"
  | "softLight" | "hardLight" | "difference" | "exclusion"
  | "hue" | "saturation" | "color" | "luminosity";

export type Fill =
  | ColorOrVariable
  | { type: "color"; enabled?: BooleanOrVariable; blendMode?: BlendMode; color: ColorOrVariable }
  | {
      type: "gradient";
      enabled?: BooleanOrVariable; blendMode?: BlendMode;
      gradientType?: "linear" | "radial" | "angular";
      opacity?: NumberOrVariable;
      center?: Position;
      size?: { width?: NumberOrVariable; height?: NumberOrVariable };
      rotation?: NumberOrVariable;
      colors?: { color: ColorOrVariable; position: NumberOrVariable }[];
    }
  | {
      type: "image";
      enabled?: BooleanOrVariable; blendMode?: BlendMode;
      opacity?: NumberOrVariable;
      url: string;
      mode?: "stretch" | "fill" | "fit";
    }
  | {
      type: "mesh_gradient";
      enabled?: BooleanOrVariable; blendMode?: BlendMode;
      opacity?: NumberOrVariable;
      columns?: number; rows?: number;
      colors?: ColorOrVariable[];
      points?: ([number, number] | {
        position: [number, number];
        leftHandle?: [number, number]; rightHandle?: [number, number];
        topHandle?: [number, number]; bottomHandle?: [number, number];
      })[];
    };

export type Fills = Fill | Fill[];

export interface Stroke {
  align?: "inside" | "center" | "outside";
  thickness?:
    | NumberOrVariable
    | { top?: NumberOrVariable; right?: NumberOrVariable; bottom?: NumberOrVariable; left?: NumberOrVariable };
  join?: "miter" | "bevel" | "round";
  miterAngle?: NumberOrVariable;
  cap?: "none" | "round" | "square";
  dashPattern?: number[];
  fill?: Fills;
}

export type Effect =
  | { enabled?: BooleanOrVariable; type: "blur"; radius?: NumberOrVariable }
  | { enabled?: BooleanOrVariable; type: "background_blur"; radius?: NumberOrVariable }
  | {
      type: "shadow";
      enabled?: BooleanOrVariable;
      shadowType?: "inner" | "outer";
      offset?: { x: NumberOrVariable; y: NumberOrVariable };
      spread?: NumberOrVariable;
      blur?: NumberOrVariable;
      color?: ColorOrVariable;
      blendMode?: BlendMode;
    };
export type Effects = Effect | Effect[];

export interface CanHaveGraphics { stroke?: Stroke; fill?: Fills; effect?: Effects; }
export interface CanHaveEffects  { effect?: Effects; }

export interface Entity extends Position, CanHaveRotation {
  /** Unique string. MUST NOT contain `/`. */
  id: string;
  name?: string;
  context?: string;
  /** If true, this object can be duplicated via `ref`. */
  reusable?: boolean;
  theme?: Theme;
  enabled?: BooleanOrVariable;
  opacity?: NumberOrVariable;
  flipX?: BooleanOrVariable;
  flipY?: BooleanOrVariable;
  layoutPosition?: "auto" | "absolute";
  metadata?: { type: string; [key: string]: any };
}

export interface Rectangleish extends Entity, Size, CanHaveGraphics {
  cornerRadius?:
    | NumberOrVariable
    | [NumberOrVariable, NumberOrVariable, NumberOrVariable, NumberOrVariable];
}

export interface Rectangle extends Rectangleish { type: "rectangle"; }

export interface Ellipse extends Entity, Size, CanHaveGraphics {
  type: "ellipse";
  /** Inner-to-outer radius ratio for ring shapes. 0 = solid, 1 = fully hollow. */
  innerRadius?: NumberOrVariable;
  startAngle?: NumberOrVariable;
  /** Arc length in degrees, -360..360. Default 360. */
  sweepAngle?: NumberOrVariable;
}

export interface Line extends Entity, Size, CanHaveGraphics { type: "line"; }

export interface Polygon extends Entity, Size, CanHaveGraphics {
  type: "polygon";
  polygonCount?: NumberOrVariable;
  cornerRadius?: NumberOrVariable;
}

export interface Path extends Entity, Size, CanHaveGraphics {
  fillRule?: "nonzero" | "evenodd";
  /** SVG path */
  geometry?: string;
  type: "path";
}

export interface TextStyle {
  fontFamily?: StringOrVariable;
  fontSize?: NumberOrVariable;
  fontWeight?: StringOrVariable;
  letterSpacing?: NumberOrVariable;
  fontStyle?: StringOrVariable;
  underline?: BooleanOrVariable;
  lineHeight?: NumberOrVariable;
  textAlign?: "left" | "center" | "right" | "justify";
  textAlignVertical?: "top" | "middle" | "bottom";
  strikethrough?: BooleanOrVariable;
  href?: string;
}

export type TextContent = StringOrVariable | TextStyle[];

export interface Text extends Entity, Size, CanHaveGraphics, TextStyle {
  type: "text";
  content?: TextContent;
  /** auto = grows, no wrap. fixed-width = fixed w, wraps, h grows. fixed-width-height = both fixed. */
  textGrowth?: "auto" | "fixed-width" | "fixed-width-height";
}

export interface CanHaveChildren { children?: Child[]; }

export interface Frame extends Rectangleish, CanHaveChildren, Layout {
  type: "frame";
  clip?: BooleanOrVariable;
  placeholder?: boolean;
  /** When an array, this frame is a "slot" — children customized in instances. */
  slot?: false | string[];
}

export interface Group extends Entity, CanHaveChildren, CanHaveEffects, Layout {
  type: "group";
  width?: SizingBehavior;
  height?: SizingBehavior;
}

export interface Note    extends Entity, Size, TextStyle { type: "note";    content?: TextContent; }
export interface Prompt  extends Entity, Size, TextStyle { type: "prompt";  content?: TextContent; model?: StringOrVariable; }
export interface Context extends Entity, Size, TextStyle { type: "context"; content?: TextContent; }

export interface IconFont extends Entity, Size, CanHaveEffects {
  type: "icon_font";
  iconFontName?: StringOrVariable;
  /** Valid: 'lucide' | 'feather' | 'Material Symbols Outlined/Rounded/Sharp' | 'phosphor'. */
  iconFontFamily?: StringOrVariable;
  weight?: NumberOrVariable;
  fill?: Fills;
}

export interface Ref extends Entity {
  type: "ref";
  /** Another object's id. Target must have `reusable: true`. */
  ref: string;
  /** Slash-separated descendant path → property override or full subtree replacement (if `type` present). */
  descendants?: { [key: string]: {}; };
  [key: string]: any;
}

export type Child =
  | Frame | Group | Rectangle | Ellipse | Line | Path | Polygon
  | Text | Note | Prompt | Context | IconFont | Ref;

export type IdPath = string;
```

## §5 Type → React idiom 映射（Phase 7 RENDER）

| `.pen` `type` | Render as | Notes |
|---|---|---|
| `frame` | `<div>` 走 flex / absolute children | Honor `layout` / `gap` / `padding` / `justifyContent` / `alignItems` |
| `group` | `<div>`（無語義） | 編輯器分組用 |
| `rectangle` | `<div>` + `width`/`height`/`background` | `cornerRadius` → `border-radius` |
| `ellipse` | `<div>` + `border-radius: 50%` | `innerRadius > 0` → 兩層 layered ring |
| `line` | `<div>` 邊框 or `<svg><line>` | unconnected line 走 `align: center` |
| `path` | `<svg><path>` | 用 `geometry` (SVG path) + viewBox |
| `polygon` | `<svg>` 正多邊形 | `polygonCount` = 邊數 |
| `text` | `<p>` / `<span>` / `<h*>` | 看 `textGrowth`：`auto` = inline-block，`fixed-width` = block w/ width |
| `icon_font` | Icon component (`lucide-react` / `phosphor-react` 等) | `iconFontFamily` 決定 lib |
| `ref` | Component instance `<ComponentName />` | `descendants` map → prop overrides |
| `note` / `prompt` / `context` | **SKIP** | author-time annotation，非 UI |
| `script` | **SKIP** 或 pre-evaluate | procedural generator；展開後再進 Phase 5 |

## §6 Schema gotchas

- **`id` MUST NOT contain `/`** — slash 留給 `ref.descendants` path resolution。
- **Variable binding = dollar-prefixed string**：`"fill": "$accent-cyan"`，**不是** `{ ref: "accent-cyan" }`。
- **Flex layout 下 Position 被忽略** — `x`/`y` on `frame.layout: "vertical"|"horizontal"` 的 child 不生效。
- **`Text` 必設 `textGrowth` 才會 honor width/height** — 否則 width/height 被忽略、文字 auto-size。
- **8-digit Color 為 RGBA**（`#AABBCCDD` 的 `DD` = alpha）— 寫進 Tailwind arbitrary value 時保留：`bg-[#5BFF8A22]`。

## §7 Framework version locks（本 skill 鎖定，與 `aibdd-auto-starter` template 對齊）

| 套件 | 鎖定版 | 變更影響 |
|---|---|---|
| `next` | `16.2.6` | 變更 → 須重審 SWC 整合 / JSX runtime 假設 |
| `react` / `react-dom` | `19.2.4` | 變更 → 須重審 `import React` 省略前提 |
| `@storybook/nextjs-vite` | `^10.3.6` | 必選；`@storybook/nextjs` (webpack 路徑) 在 Next 16 下會撞 `swc.isWasm` not a function |
| `@storybook/addon-docs` | `^10.3.6` | autodocs page 渲染必備（搭配 `tags: ["autodocs"]`） |
| `storybook` | `^10.3.6` | 與 `@storybook/nextjs-vite` 同步 |
| `vite` | `^8.0.11` | nextjs-vite framework 依賴 |
| `tailwindcss` | `^4` | CSS-first；不再使用 `tailwind.config.js`；走 `@theme` + `@utility` |
| `@tailwindcss/postcss` | `^4` | PostCSS 整合 |
| `typescript` | `^5` | 對齊 React 19 type defs |
| `@types/node` | `^20` | 對齊 Next 16 |
| `@types/react` / `@types/react-dom` | `^19` | 對齊 React 19 |

Storybook 10 specific imports：

- Story 檔：`import type { Meta, StoryObj } from "@storybook/nextjs-vite";`（**不用** `@storybook/react-vite`）
- Test API：`import { fn, expect, userEvent, waitFor } from "storybook/test";`（**不用** `@storybook/test`）
- Preview type：`import type { Preview } from "@storybook/nextjs-vite";`

升級任一鎖定版前，先讀 [`anti-patterns.md`](anti-patterns.md) §2。

## §8 Source links

- `.pen` schema：`https://docs.pencil.dev/for-developers/the-pen-format`
- Pencil CLI：`https://docs.pencil.dev/for-developers/pencil-cli`
- Tailwind 4 theme：`https://tailwindcss.com/docs/theme`
- Storybook + Next.js (Vite)：`https://storybook.js.org/docs/get-started/frameworks/nextjs`
