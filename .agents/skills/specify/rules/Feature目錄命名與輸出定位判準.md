# Rule 1 - 每次 specify 都必須建立新的 plan package

- Level: `MUST`
- `/specify` 每次執行都必須在 `specs/plans/` 下建立新的 `NNN-<slug>` plan package。
- `NNN` 使用現有 plan package 最大編號加一，不得回頭覆寫既有 package。
- 即使本次需求是修改或刪除既有行為，也建立新的 plan package，讓舊 plan 保持歷史。

## Good Example

- 這個例子是好的，因為修改既有配對規則仍建立新迭代。

```text
specs/plans/004-change-match-rule/spec.md
```

## Bad Example

- 這個例子是壞的，因為回頭改舊 plan package。

```text
specs/plans/001-online-pvp-1a2b/spec.md
```

# Rule 2 - specify 只可寫 plan artifacts

- Level: `MUST`
- `/specify` 只能寫入 `spec.md`、`checklists/requirements.md` 與初始化 `truth-delta.md`。
- `/specify` 不得新增、修改或刪除 `specs/truth/**`。
- 涉及既有 truth 的需求可在 spec 中描述預期新增、修改或刪除意圖，但實際 truth 變更交給 truth owner skill。

## Good Example

- 這個例子是好的，因為輸出全在 plan package 內。

```text
specs/plans/004-room-game-chat/spec.md
specs/plans/004-room-game-chat/checklists/requirements.md
specs/plans/004-room-game-chat/truth-delta.md
```

## Bad Example

- 這個例子是壞的，因為 specify 直接改 truth。

```text
specs/truth/contracts/openapi.yaml
```
