# Pattern — Story export 作為 boundary I4 binding anchor

## §1 為什麼這條 pattern 是 hard gate

`aibdd-core::preset-contract/web-frontend.md` boundary invariant **I4** 規定：
UI handler（`ui-action` / `ui-readmodel-then`）的 `L4.source_refs.component` **必須**指向 Story export 層
（`<file>.stories.@(ts|tsx)::<ExportName>`），不接受 component file 本身。

Step-def 的 locator 派生方式：

1. 解析 Story export 的 `args`，找出 accessible-name 欄位（`label` / `aria-label` / `name` / `title` 等）
2. 用 `page.getByRole(role, { name: <accessible-name 值> })` 鎖定 DOM 節點
3. 若 component 來自設計系統（如 shadcn / mui），AI 必須先用 `${PROJECT_SLUG}-sb-mcp` MCP 查文件確認 role 與
   accessible-name 對應方式，再寫 locator

→ Story 若沒有 accessible-name args，step-def **無法**派生 locator。
→ 缺 args 不是 legal red — 是 missing truth。本 skill 在 Phase 1 即 stop，要求 caller 先補。

## §2 正例

```ts
// component: <Button label={...} primary={...} />
//   <Button label="Submit"> 渲染為 <button>Submit</button>，accessible name = "Submit"

export const Primary: Story = {
  args: {
    label: "Submit",        // ← accessible name 來源
    primary: true,
  },
};
```

對應 step-def：

```ts
await page.getByRole("button", { name: "Submit" }).click();
```

## §3 多型 component（multiple roles per render）

若 component 在不同 args 下會渲染為不同 role（例如 `<Field type="textbox" | "combobox">`），請：

- 為每個 role 拆出獨立 Story export（`AsTextbox` / `AsCombobox`）
- 在每個 export 的 `args` 補對應的 accessible-name 欄位
- `role` 由 caller 在推理包顯式指定（本 skill 不從 args 推導 role）

## §4 反例

```ts
// ❌ 沒 label / aria-label / name；step-def 無法生 locator
export const Primary: Story = {
  args: { primary: true },
};

// ❌ accessible name 寫死在 component file，沒落到 args；
//    BDD example 想換名稱（"Submit" → "送出"）時無法 override
export const Primary: Story = {
  args: { primary: true },  // component 內部 hardcode "Submit"
};

// ❌ 用 data-testid 取代 accessible name
export const Primary: Story = {
  args: { "data-testid": "submit-btn", primary: true },
};
//   → 違反 nextjs-playwright variant 「優先 role/label 才退 testid」的順序
//   → testid 無法被 BDD example value 自然替換（無語意映射）
```

## §5 caller 推理包應提供的繫結欄位

```yaml
stories:
  - export_name: Primary
    role: "button"                          # ARIA role
    accessible_name: "Submit"               # 步驟句中可能出現的可見字串
    accessible_name_arg:
      field: "label"                        # component prop 名（產出到 args）
      value: "Submit"                       # 同 accessible_name，避免兩處不一致
    args:
      primary: true
```

- `accessible_name` 與 `accessible_name_arg.value` 必須相等（本 skill ASSERT）
- `field` 名稱必須是 component 真實接受的 prop（caller 自證；本 skill 不查 component 檔）
