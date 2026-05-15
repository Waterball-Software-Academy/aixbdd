# DSL parameters & readability coverage

所有的 DSL 都一定要傳入完整的目標「operation 呼叫／data 建構」之相等必要參數。兩種主要做法：要求 DSL 撰寫時必須透過句中參數／datatable／docstring 管道傳入參數，又或者在 dsl entry 中制定 **default** parameters（預設參數）的方式補足；**無論如何必要參數必須完整傳入**。如此一來之後在實作 DSL 之對應 step def 的時候，實作才不會腦補參數的值而讓測試意圖偏掉。

---

## 1. 「覆蓋度夠」在本 phase 的意義

此處**不是**「多綁幾個欄位差不多就好」的鬆弛覆蓋，而是 **集合相等**：

令 **S_contract** = 該 entry 所綁之 contract 上（例如 API contract），此 operation **必須**由呼叫端提供之輸入集合，包含：

- path／query：**`request.params`** 中 **required** 者；
- body：**`request.body.fields`** 中 **required** 者；
- headers：**required = true** 且**非** gate policy 排除之 transport／ambient header（例如專案約定排除之 `Authorization` 形狀、或僅由 runner 注入之 `X-Request-Id` ——**以你們 `check_dsl_entries`／boundary 政策為準，本檔不鎖定具體鍵名**）。

令 **S_dsl** = 該 entry 的 `param_bindings` + `datatable_bindings` + `default_bindings` 中，**映射到上述同一 operation 輸入表面**之 target 集合（對應 `contracts/...request...` 下之欄位鍵）。

**通過條件**：**S_dsl 與 S_contract 在鍵／欄位層級恰好一一對應**——**少一個** required（缺綁）或 **多一個** 無端多出之 input surface，皆 **fail**。

- **例（少一個，fail）**：contract 上 `request.body.fields` 有 **四個** required：`roomCode`、`hostUserId`、`maxPlayers`、`status`，前置與 invocation 已就緒，但 operation entry 只綁其中三個——**exact coverage 失敗**（與 `check_dsl_entries.py` 預期一致）。

- **例（多一個，fail）**：contract **沒有** required `discountCode`，DSL 卻在 `param_bindings` 多綁「自以為常用」之欄——**多餘 target**，fail（除非該欄在 contract 上確為 required，或可論證為機械檢查接受之同義 alias）。

---

## 2. `default_bindings` 定義

每一筆 `default_bindings`（若存在）必含四鍵，缺一不可：`target`、`value`、`reason`（指回 atomic rule 或 majority-behavior 依據）、`override_via`（允許何種覆寫／或明示不可 override）。

- **例（合法）**：如在 reason 中寫「建構基本資料時，大多數資料都不影響遊戲的業務規則，因此可以設定預設值，來減少 dsl 參數負擔」。

  對應一筆 **operation entry**（示意；`target` 須與你們真實 `contracts/...` 一致）：

  ```yaml
  entries:
    - id: example.create-room.when-host-ready
      L1:
        when:
          - 主辦「{hostUserId}」以代號「{roomCode}」建立遊戲房間
      L2:
        context: Host opens a room; only rule-carrying inputs stay on the sentence line.
        actor: host
      L3:
        part: operation-invoke
      L4:
        surface_id: rooms.create
        surface_kind: operation
        callable_via: http
        preset:
          name: web-backend
          handler: operation-invoke
          variant: python-e2e
        param_bindings:
          hostUserId:
            target: contracts/rooms.openapi.yml#/components/schemas/CreateRoomRequest/properties/hostUserId
          roomCode:
            target: contracts/rooms.openapi.yml#/components/schemas/CreateRoomRequest/properties/roomCode
        datatable_bindings: {}
        default_bindings:
          - target: contracts/rooms.openapi.yml#/components/schemas/CreateRoomRequest/properties/maxPlayers
            value: 4
            reason: >-
              建構基本資料時，大多數資料都不影響遊戲的業務規則，因此可以設定預設值，來減少 dsl 參數負擔。
            override_via: same-step DataTable 欄位 maxPlayers
        assertion_bindings: {}
        source_refs:
          contract: contracts/rooms.openapi.yml
          data: null
          boundary: null
          test_strategy: null
  ```

---

## 3. Readability pressure（可讀性壓力）

- 單一 operation entry 之 **L1 句內**顯式 sentence-level parameters **≤ 3**。
- **datatable** 之 DSL-facing 業務欄位數（套用 `default_bindings` 後仍須由 scenario／datatable 餵者）**≤ 6**。
- 違反時：**拆分 entry** 或將非句型關鍵輸入推入 `default_bindings`／datatable（仍須滿足 **§1** 集合相等）。

- **例（fail）**：單一 `When` 句擠進 **六個**句內顯式參數（對應六個綁定槽位），超過上限 3——應改寫、併入 datatable，或拆成多個 operation entry（每 entry 仍遵 entry／rule 顆粒度）。

  ```gherkin
  Scenario: Host creates a room
    Given a registered host "host-user-01"
    When the host creates a room with code "FRIDAY-01", title "Friday lobby", max players 8, visibility "private", region "ap-northeast-1", and tags "casual"
    Then the create room response status is 201
  ```
