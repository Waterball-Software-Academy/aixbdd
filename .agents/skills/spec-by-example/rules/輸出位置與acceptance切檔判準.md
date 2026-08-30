# Rule 1 - Acceptance feature files 必須留在 plan package

- Level: `MUST`
- `/spec-by-example` 的輸出位置固定為 `specs/plans/NNN-<slug>/features/acceptance/*.feature`。
- Acceptance Gherkin 是本次迭代的業務驗收旅程，不是 interface truth。
- 不得把 acceptance feature files 寫入 `specs/truth/features/**`。

## Good Example

- 這個例子是好的，因為 acceptance 留在當次 plan package。

```text
specs/plans/004-room-game-chat/features/acceptance/雙方在場即時互傳.feature
```

## Bad Example

- 這個例子是壞的，因為把 journey acceptance 寫成 truth interface feature。

```text
specs/truth/features/backend/房間聊天/雙方在場即時互傳.feature
```

# Rule 2 - Acceptance 切檔以業務 journey 為準

- Level: `SHOULD`
- 每份 acceptance feature 應描述 PM 可 review 的完整業務 journey 或明確業務規則。
- 不應按 API endpoint、資料表、前端元件或 step definition 技術邊界切檔。
- 若同一 journey 有多個重要變體，可用多個 Rule / Example，而非過度拆檔。

## Good Example

- 這個例子是好的，因為檔名描述業務旅程。

```text
features/acceptance/開局後同一串延續且不擋對戰.feature
```

## Bad Example

- 這個例子是壞的，因為用 endpoint 切 acceptance。

```text
features/acceptance/post-room-message-api.feature
```
