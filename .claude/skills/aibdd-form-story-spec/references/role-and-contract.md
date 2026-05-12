# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。

## §1 角色定位

Formulation skill。綁定 DSL = Storybook **CSF3**（`*.stories.ts` / `*.stories.tsx`）；綁定 framework =
`@storybook/nextjs-vite`（Storybook 10）。

**做**：把 caller 推理包翻成 CSF3 語法、寫檔、自檢結構。
**不做**：

- 不挑 component 顆粒度（一檔一組件 vs. 多 variant 拆檔由 caller 決定）
- 不發明 props / argTypes / args（缺值 → 回 caller 補）
- 不挑 component 來源檔（`import_path` 由 caller 指定）
- 不選 design system 元件、不引入 wrapper
- 不在 story 裡寫業務邏輯、不替 caller 做 BDD 分析

## §2 入口契約 — 推理包 schema

```yaml
target_path: <string, required>          # e.g. "src/stories/Login.stories.ts"
format: ".stories.ts" | ".stories.tsx"   # 必須與 target_path 副檔名一致
mode: "create" | "overwrite"             # 預設 "create"；已存在檔案非 overwrite → 衝突回退

design_source:                            # OPTIONAL — design-aware 入口；缺省走純 caller reasoning 流程
  kind: "pen" | "none"                    # 預設 "none"；未來可加 "figma" / "penpot" 等 sibling adapter
  path: <string?>                          # kind != "none" 時必填；e.g. "${PACKAGE_ROOT}/design.pen"
  screen_id: <string?>                     # 選擇 .pen 內哪個 screen（缺則由 adapter Phase 4 由 user 確認）
  style_profile_path: <string?>            # 補充 token 來源（e.g. design/style-profile.yml；目前僅入 Story `parameters.designTokens`）

reasoning:
  component_modeling:
    framework: "@storybook/nextjs-vite"  # caller-allowed list 之一
    exit_status: "complete"              # caller 推理閉合的訊號

    component:
      identifier: <PascalCase>           # e.g. "LoginForm"；JS identifier
      import_path: <string>              # e.g. "./LoginForm" / "@/components/login/LoginForm"
      title: <string>                    # Storybook sidebar 路徑，e.g. "Auth/LoginForm"
      tags: ["autodocs"] | []            # 預設啟用 autodocs，由 caller 顯式禁用才省略
      parameters: <object?>              # 例：{ layout: "centered" }
      argTypes: <object?>                # 例：{ backgroundColor: { control: "color" } }
      shared_args: <object?>             # 跨 stories 共享 args（meta 層）

    stories:
      - export_name: <PascalCase>        # e.g. "Empty" / "Submitting" / "Disabled"
        role: <string>                   # ARIA role；e.g. "form" / "button" / "alert"
        accessible_name: <string>        # I4 hard gate；e.g. "Login form"
        accessible_name_arg:             # 落到 args 的欄位 + 值（caller 指定）
          field: "label" | "aria-label" | "name" | "title" | <string>
          value: <string>
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

## §3 缺項處理

推理包不完整或 `target_path` 未指定 → Phase 1 RETURN「推理包不完整」回退呼叫 caller 補齊；
本 skill 不推測缺值。

`accessible_name` 與 `role` 缺一即 stop —— I4 binding anchor 是 step-def locator 的 SSOT，偽造會在 red-execute
時把錯誤推遲到下游難以歸因。
