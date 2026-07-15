# kind: websocket — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 websocket 的依賴。entry 樣板：assets/dependencies.template.yml（websocket 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/websocket.yml。

## 測試範圍（先於一切）

1. 兩型依 sut_role 分流：第三方 feed（SUT 是 client）——Given 替身將推送 frame（B）
   ＋Then 觀測點收到 frame（E）；第一方 endpoint（SUT 是 server）——When 測試
   client 送 frame（C，與 channel inbound 同形）＋Then frame 斷言（E）。
2. 連線重試、心跳、重連等協定語意為範圍外（scope-discriminant 範圍判別式 2）。
3. 句式素材屬 kind 常數，registry 不收。

## truth 取得分流（依序嘗試，取得即停）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 truth 檔，優先採用。
2. asyncapi（native 首選，2026-07-14 拍板）：vendor 或團隊已有 AsyncAPI
   ws binding 者採用，`format: asyncapi`。
3. authored：依 feature truth 推導 frames 約定（direction／event／payload 欄位），
   `evidence: assumed`；推不出 payload 者收 `$ASK_BATCH`。

## testability 與 wiring

1. 替身預設住 kind-constants：client 型＝MockWebServer（in-process，無 container）；
   需獨立行程時 MockServer container。WireMock 3 不支援 ws，不得選用。
2. client 型 `sut_property_overrides` 必填（SUT 指向 feed URL 的 config key，
   prehandling 改指替身）；server 型免列（SUT 自帶 endpoint）。
3. entry 需帶 `sut_role: client|server`（此為 per-dependency 事實，非常數）。

## truth 檔內容（frames 由 truth 檔承載，entry 不抄）

1. 只收本批次 feature truth 會推送或斷言的 frame（direction 以 SUT 視角：
   in＝SUT 收、out＝SUT 送）；每筆 payload 欄位指得回真相。
2. 佔位變數對得上 feature 資料別名。
