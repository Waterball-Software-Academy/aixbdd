# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。

## §1 角色定位

Formulation skill — **caller-driven pipeline 專用**。綁定 DSL = Storybook **CSF3**（`*.stories.tsx`）+ React
**TSX** component（`*.tsx`）；綁定 framework = `@storybook/nextjs-vite`（Storybook 10）。

**做**：

- 把 caller 推理包翻成 React TSX（Props interface + named export function）+ CSF3 stories
- 兩個檔寫入 caller 指定的 `target_dir`（co-located）
- 自檢結構（component 不含 hooks/IO；story CSF3 結構正確）

**不做**：

- 不挑 component 顆粒度（一檔一組件 vs. 多 variant 拆檔由 caller 決定）
- 不發明 props / argTypes / args（缺值 → 回 caller 補）
- 不挑 component 來源檔位置（`target_dir` 由 caller 指定）
- 不選 design system 元件、不引入 wrapper
- 不在 component 寫業務邏輯（hooks / fetch / state machines）— 這屬 `/aibdd-green-execute`
- 不在 story 裡寫業務邏輯、不替 caller 做 BDD 分析
- 不替 caller 解析 design tokens 為 Tailwind classes（caller 預先決定 base_class 字串）
- **不處理設計來源（`.pen` / Figma / Penpot）** — 那是 `/aibdd-pen-to-storybook` 等 producer sibling 的職責。
  本 skill 收到 `design_source.kind != "none"` 一律 STOP，建議 caller 改走對應 producer skill。

## §1.5 與 `/aibdd-pen-to-storybook` 的邊界

| 場景 | skill |
|---|---|
| 已有 `.pen` 設計檔 | `/aibdd-pen-to-storybook`（一條龍：讀 `.pen` → 直接寫 `.tsx` + `.stories.tsx`） |
| 無 `.pen`，純 caller-driven 推理 | **本 skill** |
| 後端 boundary widget / 設計不適用的元件 | **本 skill** |

同一 component 不該兩條路徑同時寫；caller 二選一。產物落同一 `target_dir`（`${TRUTH_BOUNDARY_ROOT}/contracts/components/<id>/`）；
本 skill 為產出檔的 owner，視覺修改應該回上游推理包後重跑（`mode: "overwrite"`），而不是在下游手改。

## §2 入口契約 — 推理包 schema

```yaml
target_dir: <string, required>           # 寫兩個檔的目錄（caller 必須預先存在或允許 skill 建立）
                                          # 慣例：${TRUTH_BOUNDARY_ROOT}/contracts/components/<ComponentId>/
                                          # 例：specs/boss-fe/contracts/components/RoomCodeInput/
                                          #
                                          # 寫出檔案：
                                          #   ${target_dir}/<identifier>.tsx
                                          #   ${target_dir}/<identifier>.stories.tsx

mode: "create" | "overwrite"             # 預設 "create"；任一檔已存在且非 overwrite → 衝突回退
                                          # overwrite 對兩檔同時生效

design_source:                            # OPTIONAL — 僅接受 kind: "none"；其他值一律 STOP（design pipeline 改走 /aibdd-pen-to-storybook）
  kind: "none"                            # 唯一合法值；任何 "pen" / "figma" / "penpot" 等請改呼對應 producer skill

reasoning:
  component_modeling:
    framework: "@storybook/nextjs-vite"  # caller-allowed list 之一
    exit_status: "complete"              # caller 推理閉合的訊號

    component:
      identifier: <PascalCase>           # e.g. "RoomCodeInput"；JS identifier；同檔名前綴
      title: <string>                    # Storybook sidebar 路徑，e.g. "Components/RoomCodeInput"
      tags: ["autodocs"] | []            # 預設啟用 autodocs，由 caller 顯式禁用才省略
      parameters: <object?>              # 例：{ layout: "centered" }
      argTypes: <object?>                # 例：{ backgroundColor: { control: "color" } }
      shared_args: <object?>             # 跨 stories 共享 args（meta 層）

      # ============================================================
      # NEW（雙產出版）：component .tsx 渲染所需資訊
      # 沒這些 → 只有 stories 沒有 component；不接受
      # ============================================================
      props:                              # required；可為空 list（純展示 component）
        - name: <camelCase>               # e.g. "value" / "onChange" / "disabled"
          type: <string>                  # TypeScript type literal，e.g. "string" / "(value: string) => void" / "boolean"
          required: <bool>
          default: <any?>                 # required=false 時可設；JSON-serialisable
                                          # 注意：default 只進 Props comment，不寫成 default param
                                          # （runtime default 屬 green-execute 的職責）

      render_hints:                       # OPTIONAL；缺省走最小 stub
        root_element: <string?>           # JSX 根元素名（"div" / "button" / "input" / "form" / "section" ...）
                                          # default: "div"
        children_layout:                  # JSX 結構模式 enum
          "leaf"         |                # 單一自閉節點：<root />
          "text"         |                # 容器 + children: <root>{props.children ?? null}</root>
          "labeled-input"|                # <label><span>{labelProp}</span><input ...>...</label>
          "button"       |                # <button type="...">{labelProp}</button>
          "container"                     # <root>{props.children}</root>（強制 children prop）
                                          # default: "leaf"
        base_class: <string?>             # Tailwind 4 class string；caller 從 design tokens 預先解析
                                          # e.g. "bg-surface text-text rounded-sharp px-4 py-2"
                                          # default: ""（空字串；scaffold 純結構，無樣式）
        accessible_name_prop: <string?>   # children_layout="labeled-input" 或 "button" 時必填
                                          # 指明哪個 prop 提供 visible text / aria-label
                                          # 必須 ∈ props[*].name
        button_type: "button" | "submit" | "reset"  # children_layout="button" 時 optional；default "button"

    stories:
      - export_name: <PascalCase>        # e.g. "Empty" / "Submitting" / "Disabled"
        role: <string>                   # ARIA role；e.g. "form" / "button" / "alert"
        accessible_name: <string>        # I4 hard gate；e.g. "Login form"
        accessible_name_arg:             # 落到 args 的欄位 + 值（caller 指定）
          field: "label" | "aria-label" | "name" | "title" | <string>
                                          # 必須 ∈ component.props[*].name
                                          # （否則 component prop interface 無此欄位 → story args 無法傳）
          value: <string>                # 必須 == accessible_name
        args: <object?>                  # 該 story 的 props override
        has_action_args: <bool>          # true → 注入 `import { fn } from "storybook/test"`
        has_play: <bool>                 # true → 渲染 play function
        play_steps:                      # 僅 has_play=true 時必填
          - kind: "type" | "click" | "select" | "press" | "expect"
            target:                       # 從 canvas 取元素的方式
              query: "getByRole" | "getByLabelText" | "getByTestId" | "getByText" | "getByPlaceholderText"
              args: [<string>, <object?>] # e.g. ["textbox", { name: "Email" }]
            value: <string?>             # type / select 時必填
            assertion: <string?>         # expect 時必填，e.g. "toBeInTheDocument" / "toHaveValue"
            expected: <any?>             # assertion 比對值
```

### 不允許在 caller payload 出現的東西

- 私有 CSS class selector / nth-child（違反 boundary I4，locator 必須來自 accessible name + role）
- `decorators` 寫死全域可變狀態（每個 story 應 self-contained；跨 story 共享狀態 → 用 args / parameters）
- 直接 import product service 的 mock 實作（mock 屬 `features/steps/fixtures.ts` SSOT，不屬 story 檔）
- `render_hints.base_class` 內含 token 名稱（e.g. `--color-accent`）— caller 必須預先解析為實際 Tailwind class（e.g. `bg-accent`）；本 skill 不做 token resolution
- `component.props` 含 React 內建型別字串如 `"React.FC"`、`"FunctionComponent"` — 不接受
- `component.props` 含 `useState` initial value、effect 等 runtime 行為提示 — 屬 green-execute

## §3 缺項處理

推理包不完整或 `target_dir` 未指定 → Phase 1 RETURN「推理包不完整」回退呼叫 caller 補齊；
本 skill 不推測缺值。

`accessible_name` 與 `role` 缺一即 stop —— I4 binding anchor 是 step-def locator 的 SSOT，偽造會在 red-execute
時把錯誤推遲到下游難以歸因。

`accessible_name_arg.field` 不在 `component.props[*].name` 即 stop —— story args 傳給不存在的 prop 會在 TypeScript 編譯失敗。

`render_hints.children_layout == "labeled-input"` 或 `"button"` 但未指定 `accessible_name_prop` 即 stop ——
無法決定哪個 prop 注入 accessible name。

## §4 路徑慣例（caller 應對齊）

`target_dir` 由 caller 決定，但 `/aibdd-plan` 應依以下慣例推導：

```
target_dir = ${TRUTH_BOUNDARY_ROOT}/contracts/components/<ComponentId>/
```

對應 `arguments.yml` 中的 `CONTRACTS_DIR`（= `${TRUTH_BOUNDARY_ROOT}/contracts`），加上慣例子目錄 `components/<ComponentId>/`。

例：
```
specs/boss-fe/contracts/components/RoomCodeInput/
├── RoomCodeInput.tsx              ← component 實作
└── RoomCodeInput.stories.tsx      ← I4 binding anchor SSOT
```

`src/` 端透過 tsconfig path alias `@/components/* → specs/<TLB>/contracts/components/*` 引用：

```ts
// src/app/page.tsx
import { RoomCodeInput } from "@/components/RoomCodeInput/RoomCodeInput";
```

Storybook 端在 `.storybook/main.ts` 加 glob：

```ts
stories: [
  "../specs/<TLB>/contracts/components/**/*.stories.@(ts|tsx)",
  "../specs/<TLB>/contracts/components/**/*.mdx"
]
```

本 skill 不修改 tsconfig / Storybook config / vitest config —— 那是 `aibdd-auto-starter` 的 template 職責。
