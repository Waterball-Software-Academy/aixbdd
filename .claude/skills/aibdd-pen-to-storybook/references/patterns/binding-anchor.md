# Pattern — Story export 作為 boundary I4 binding anchor

> 純 declarative reference。Phase 6 DERIVE render plan 與 Phase 8 RENDER stories 時 LOAD 取規則。
>
> 與 [`variants-and-states.md`](variants-and-states.md) 配合：每個 detected variant / state 都要在 story
> 端 expose 對應 `role` + `accessible_name`，否則 step-def 無法 locate。

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
→ 缺 args 不是 legal red — 是 missing truth。本 skill 在 Phase 6 即 dispatch `accessible-name-prop-missing`，
要求 caller 回 `.pen` 補可見文字節點後重試。

## §2 從 `.pen` 推導 accessible-name 來源

依下列順序套用，先命中即用：

1. component 子樹根節點是 `<button>` → 取按鈕內可見 text 節點為 accessible-name source；prop 命名為 `label`
2. component 子樹根節點是 `<label>` 包 `<input>` → 取 `<label>` 內可見 text 為 accessible-name source；prop 命名為 `label`
3. component 子樹根節點是 `<input>` 但無 `<label>` 包覆 → caller 必須在 `.pen` 補一個 label-like 可見字串子節點，否則 Phase 6 fail
4. component 子樹根節點是 `<form>` / `<section>` / `<dialog>` → 取最大字級 heading text 為 accessible-name source；prop 命名為 `title`
5. 其他容器型 component → 取首個可見 text 為 accessible-name source；prop 命名為 `title` 或 `name`

每個 detected component **必須**有一個 prop 對應到該可見字串（在 Phase 6 step 6.5 推導為 `$accessible_name_field`）。

## §3 正例

```tsx
// detected component: LobbyRoomEntry
// canonical .pen 子樹根：<section>，內含 <h2> "1A2B 猜數字魔王" + <input> + <button>
// $accessible_name_field = "title"（取 <h2> 文字為 source）

export type LobbyRoomEntryProps = {
  title: string;
  roomCodeLabel: string;
  buttonLabel: string;
  // ...
};

export function LobbyRoomEntry(props: LobbyRoomEntryProps) {
  return (
    <section aria-label={props.title} className="...">
      <h2 className="...">{props.title}</h2>
      <label className="...">
        <span>{props.roomCodeLabel}</span>
        <input type="text" />
      </label>
      <button type="button">{props.buttonLabel}</button>
    </section>
  );
}
```

對應 story（Phase 8 RENDER）：

```ts
export const Default: Story = {
  args: {
    title: "1A2B 猜數字魔王",
    roomCodeLabel: "四位房號",
    buttonLabel: "開房",
    // ...
  },
};
```

對應 step-def：

```ts
await page.getByRole("region", { name: "1A2B 猜數字魔王" });
await page.getByRole("textbox", { name: "四位房號" }).fill("1234");
await page.getByRole("button", { name: "開房" }).click();
```

## §4 多 role component

若 component 在不同 args / variants 下會渲染為不同 role（例：`<Field type="textbox" | "combobox">`），請：

- 為每個 role 拆出獨立 component（detection 階段命中 H5 應已拆）
- 不要在同一 component 內動態切換 role

本 skill 偵測到同 component 內 role 不一致 → warn caller，建議拆 component。

## §5 反例

```tsx
// ❌ accessible name 寫死在 component file，沒落到 args；
//    BDD example 想換名稱（"Submit" → "送出"）時無法 override
export function SubmitButton(props: SubmitButtonProps) {
  return <button>Submit</button>;  // ← hardcoded
}

// ❌ 用 data-testid 取代 accessible name
export const Default: Story = {
  args: { "data-testid": "submit-btn" },
};
// → 違反 nextjs-playwright variant 「優先 role/label 才退 testid」的順序

// ❌ accessible-name args 與 component 實際 prop 名不一致
//   component 接 `label`，story args 寫 `text` → TypeScript 編譯失敗 / step-def 取錯欄位
export const Default: Story = {
  args: { text: "Submit" },  // ← 應為 label
};
```

## §6 Phase 6 / 8 ASSERT 清單

Phase 6（DERIVE render plan）：
- ASSERT 每個 detected component 找得到 `$accessible_name_field`；找不到 → dispatch `accessible-name-prop-missing`
- ASSERT `$accessible_name_field` ∈ `$plan.props[].name`

Phase 8（RENDER stories）：
- ASSERT `story.accessible_name_arg.field == $plan.accessible_name_field`
- ASSERT `story.accessible_name_arg.value == story.accessible_name`
- ASSERT `story.role` 與 component root JSX element 對應的 ARIA role 一致
