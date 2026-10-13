# Rule 1 - 每次 specify 都必須建立新的 plan package

- Level: `MUST`
- `/specify` 每次執行都必須在 `specs/plans/<slug>/` 下建立新的 plan package。
- `<slug>` 必須使用 kebab-case，且不得有數字前綴。
- 建立前必須確認 `<slug>` 尚未存在於 `specs/plans/` 資料夾，且尚未出現在 `specs/plans/index.yaml` 的 `plan` 欄位。
- 若發生衝突，必須改用更具體的 slug；無法判定時詢問使用者。不得覆寫既有 package。
- 即使本次需求是修改或刪除既有行為，也必須建立新的 plan package，讓舊 plan 保持歷史。

## Good Example

- 這個例子是好的，因為它使用沒有數字前綴的新 slug 建立獨立 package。

```text
specs/plans/change-match-rule/spec.md
```

## Bad Example

- 這個例子是壞的，因為第一個路徑的 `online-pvp-1a2b` 已存在於 index（重用 package），第二個路徑則有數字前綴。

```text
specs/plans/online-pvp-1a2b/spec.md
specs/plans/004-change-match-rule/spec.md
```

# Rule 2 - specify 只可寫 plan artifacts

- Level: `MUST`
- `/specify` 只能寫入當前 plan package 內的 `spec.md`、`checklists/requirements.md`、初始化 `truth-delta.md`，以及在 `specs/plans/index.yaml` 新增本 plan 的一筆項目。
- `/specify` 不得新增、修改或刪除 `specs/truth/**`。
- 涉及既有 truth 的需求可在 spec 中描述預期新增、修改或刪除意圖，但實際 truth 變更交給 truth owner skill。

## Good Example

- 這個例子是好的，因為輸出只包含 plan package 產物與新增本 plan 的 index 項目。

```text
specs/plans/room-game-chat/spec.md
specs/plans/room-game-chat/checklists/requirements.md
specs/plans/room-game-chat/truth-delta.md
specs/plans/index.yaml
```

## Bad Example

- 這個例子是壞的，因為 specify 修改了其他 plan 的 index 項目並直接改 truth。

```text
specs/plans/index.yaml（修改既有 plan: earlier-plan 的 title）
specs/truth/contracts/openapi.yaml
```

# Rule 3 - plan index 必須記錄排序與基本資料

- Level: `MUST`
- `specs/plans/index.yaml` 必須是 YAML 清單；檔案不存在時，依 Rule 5 與 Rule 6 從既有 plan packages 重建；只有完全沒有既有 package 時才建立空清單。
- 每筆資料必須包含 `created`、`plan` 與 `title`：`created` 是含秒與 `Z` 的 UTC ISO 8601 時間（例如 `2025-06-12T14:30:05Z`），且必須以引號儲存成字串，避免 YAML 工具將其自動解析為日期時間物件；`plan` 是與資料夾名稱相同的 slug，`title` 是功能標題。
- 清單必須依 `created` 遞增排序；時間相同時依 `plan` 字母順序排序。
- 計畫順序只由此檔案定義，不得以資料夾名稱或檔案系統時間推斷。

## Good Example

- 這個例子是好的，因為欄位完整，並依建立時間遞增排列。

```yaml
- created: "2025-06-12T10:00:00Z"
  plan: room-game-chat
  title: 房間即時聊天
- created: "2025-06-12T14:30:05Z"
  plan: change-match-rule
  title: 調整配對規則
```

## Bad Example

- 這個例子是壞的，因為清單沒有依 `created` 遞增排序，也缺少必要欄位。

```yaml
- created: "2025-06-12T14:30:05Z"
  plan: change-match-rule
- created: "2025-06-12T10:00:00Z"
  plan: room-game-chat
  title: 房間即時聊天
```

# Rule 4 - 新 plan 必須按建立時間插入 index

- Level: `MUST`
- 建立 plan package 時只取得一次當下 UTC 時間，並保留為 `CREATED_AT`；寫入 `spec.md` 時，將同一值寫入 `建立時間 (UTC)` 與 index 項目的 `created`。
- 新項目必須插入依 `created` 排序後的正確位置，不得一律附加到清單末尾；其他分支合併後可能已有較晚時間的項目。
- 若現有 index 未依本規則排序，必須回報使用者，不得靜默重排。
- 不得為了插入新項目而修改或刪除其他項目。

## Good Example

- 新項目 `room-game-chat` 依 `created` 插在 `earlier-plan` 與 `later-plan` 之間，且同一時間寫入 spec。

```yaml
- created: "2025-06-12T08:00:00Z"
  plan: earlier-plan
  title: 較早的功能
- created: "2025-06-12T10:00:00Z"
  plan: room-game-chat
  title: 房間即時聊天
- created: "2025-06-12T14:00:00Z"
  plan: later-plan
  title: 較晚的功能
```

```text
spec.md：**建立時間 (UTC)**: 2025-06-12T10:00:00Z
```

## Bad Example

- 這個例子是壞的，因為新項目的時間早於既有項目，卻仍被附加在清單末尾。

```yaml
- created: "2025-06-12T08:00:00Z"
  plan: earlier-plan
  title: 較早的功能
- created: "2025-06-12T14:00:00Z"
  plan: later-plan
  title: 較晚的功能
- created: "2025-06-12T10:00:00Z"
  plan: room-game-chat
  title: 房間即時聊天
```

# Rule 5 - index 衝突與損毀時必須保全並復原資料

- Level: `MUST`
- (a) 解決 `index.yaml` 衝突時，必須先取雙方項目的聯集。
- (b) 若同一 `plan` 出現不同的 `created`，這是 slug 衝突；不得去重，必須進入改名流程。
- (c) 只有完全相同的項目才能去重。若只有 `title` 不同，保留與該 plan 的 `spec.md` 標題相符的一側。
- (d) 衝突處理後依 `created` 遞增、再依 `plan` 字母順序排序；不得丟棄任何項目。
- (e) 改名流程必須先取得使用者確認，再將 `created` 較晚的 plan 改為新 slug；重新命名其資料夾、index 的 `plan` 欄位、`spec.md` 的 `**Plan**` 值，以及 package 內每一處參照。
- (f) 重建 index 時，`plan` 取自資料夾名稱、`created` 取自 `spec.md` 的 `建立時間 (UTC)`、`title` 取自 spec 標題 `# 功能規格：…`；legacy plan package 依 Rule 6 處理。

## Good Example

- 這個例子是好的，因為它保留雙方聯集中的兩個項目，並依 `created` 排序。

```yaml
- created: "2025-06-12T10:00:00Z"
  plan: room-game-chat
  title: 房間即時聊天
- created: "2025-06-12T14:00:00Z"
  plan: change-match-rule
  title: 調整配對規則
```

## Bad Example

- 這個例子是壞的，因為合併前兩側各有一個項目，合併後卻丟掉了另一側的 `change-match-rule`。

```yaml
before:
  ours:
    - created: "2025-06-12T10:00:00Z"
      plan: room-game-chat
      title: 房間即時聊天
  theirs:
    - created: "2025-06-12T14:00:00Z"
      plan: change-match-rule
      title: 調整配對規則
```

```yaml
after:
  - created: "2025-06-12T10:00:00Z"
    plan: room-game-chat
    title: 房間即時聊天
```

# Rule 6 - 舊版 plan package 遷移

- Level: `MUST`
- 既有 legacy `NNN-<slug>` package 必須保留原資料夾名稱，不得重新命名；Rule 1 的數字前綴禁令只適用於新 package。
- 若 `index.yaml` 不存在但有 legacy package，必須先依既有 package 重建 index，再插入新 plan。
- legacy spec 只有 `建立日期` 日期時，`created` 必須使用 `<date>T00:00:00Z`；同日項目依 `NNN` 數字順序排序。

## Good Example

- 這個例子是好的，因為它保留 legacy 資料夾名稱，並把日期補成 UTC 午夜；同日依原數字順序排列。

```yaml
- created: "2025-06-12T00:00:00Z"
  plan: 002-old-feature
  title: 舊功能
- created: "2025-06-12T00:00:00Z"
  plan: 004-another-feature
  title: 另一個舊功能
```

## Bad Example

- 這個例子是壞的，因為它重新命名 legacy package，且未先從舊 packages 重建遺失的 index。

```text
既有資料夾：specs/plans/002-old-feature/
錯誤重新命名為：specs/plans/old-feature/
index.yaml：直接建立空清單
```
