# Task ID Scheme

## 編號規則

- 統一前綴 `T`，零填補成兩位數：`T01`、`T02`、…、`T99`
- 從 `T01` 起跳，**不跳號**、**不重號**
- 編號順序：先按 Phase 升冪（Phase 1 → Phase 2 → Phase 3），再按 Phase 內依賴拓撲序

## Phase 預期 Task 數量

| Phase | 主題 | 預期 task 數 |
|---|---|---|
| Phase 1 | MSW Layer | 4（Zod schemas / Fixtures / Handlers / API Client functions） |
| Phase 2 | Pages | 1（design-token 全局綁定）+ N（每個 Pencil frame 一條） |
| Phase 3 | Visual Parity Gate | 1 |

對於 1A2B Boss Battle（16 frames）：4 + 1 + 16 + 1 = **22 條 task**，編號從 `T01` 跑到 `T22`。

## Phase 內順序規則

### Phase 1 內順序（嚴格）

```
T01 Zod Schemas
T02 Fixtures
T03 Handlers          ← 依賴 T01 (zod 用於 validate request) + T02 (fixtures 是 handlers 的回應素材)
T04 API Client funcs  ← 依賴 T01 (zod 用於 type 簽名) + T03 (handler 提供的 endpoint shape)
```

### Phase 2 內順序

```
T05 Design Token Binding   ← 全局，必須最先
T06..T<N+5>                ← 每個 frame 一條，順序依 .pen 內 frame 命名升冪（"01 Lobby" → "16 Defeat"）
```

frame 之間若有 navigation 依賴（例：lobby 導向 waiting room），順序仍依**命名升冪**而非 navigation 順序，理由：
- 命名升冪 = 設計師排版的人類直覺順序
- navigation 圖在實作層常有 cycle（lobby → room → game → 終局 → 回 lobby），不能拓撲排序

### Phase 3 內順序

```
T<last> Visual Parity Gate   ← 必為最後一條
```

## Dependency 表達

每條 task 在 markdown body 內必須有 `**依賴**：` 行，列出**直接前置 task ID**（不需要列 transitive 依賴）。例：

```markdown
## T03 — MSW Handlers

**依賴**：T01, T02
```

無依賴的 task（例：T01）寫 `**依賴**：無`。

## Task ID 與其他位置的綁定

- Task ID 出現在：
  - 頂部「任務地圖」表格的最左欄
  - 每條 task 標題（`## T01 — <task name>`）
  - 其他 task 的 `**依賴**：` 行
- 不在其他位置出現（避免漂移）

## 重新編號的時機

如果 .pen 設計增加 frame、或 contract 增加 endpoint，重跑這個 skill 時 **整份重新編號**（保留結構、不嘗試 diff-merge）。手動編輯後的 tasks.md 若再跑 skill，**會被覆蓋**——這是有意設計（tasks.md 是 derived artifact，不是 SSOT）。
