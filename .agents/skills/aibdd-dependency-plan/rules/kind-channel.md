# kind: channel — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 channel 的依賴。entry 樣板：assets/dependencies.template.yml（channel 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/channel.yml。

## 測試範圍（先於一切）

1. channel kind 的測試面只有兩個：When 事件發生（往 topic/queue 發測試訊息
   驅動 SUT 消費，inbound）、Then 驗證有發送事件到 topic（test consumer 收
   SUT 發布的訊息並斷言，outbound，恆帶 eventually）。
2. 訊息順序、exactly-once、重投遞語意為範圍外，truth 檔與句面素材皆不得涉及。
3. direction 以 SUT 視角判定：SUT 消費＝inbound、SUT 發布＝outbound；
   同一 topic 對 SUT 雙向使用時兩個 direction 各立 channels 條目。

## truth 取得分流（依序嘗試，取得即停）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 truth 檔，有則優先採用。
2. asyncapi（首選 native）：專案或團隊已有 AsyncAPI 文件者採用，
   `format: asyncapi`。
3. schema registry 匯出：專案有 registry（avro／json-schema subject）者，
   匯出對應 subject 落檔，`format: avro` 或 `json-schema`。
4. authored：皆無時依 feature truth 推導 message 形狀撰寫約定
   （event_type／key／headers／payload 欄位），`evidence: assumed`；
   推不出 payload 欄位者收進 `$ASK_BATCH`。

## testability 與 wiring

1. double 恆為 real-product；per-broker container 預設與 prehandling 骨架
   （含 topic 預建、test consumer 註冊兩條固定註記）住
   .claude/skills/aibdd-core/references/kind-constants/channel.yml，entry 依 broker 查表不重抄，
   偏離才填 testability_overrides。custom step 模版（C 發訊／E 收訊斷言）
   同樣內建於 kind-constants，registry 不收句式素材。
2. Spring Boot Kafka／RabbitMQ 皆支援 `@ServiceConnection`，
   `sut_property_overrides` 通常免列。

## truth 檔內容（channels/messages 由 truth 檔承載，entry 不抄）

1. authored 約定只收本批次 feature truth 會觸發或驗證的 channel 與 message
   （name／direction／event_type／key／payload 欄位）；AsyncAPI 等 native
   truth 原檔保留。
2. key 表達式（如 orderId）必須對得上 feature 中的資料別名。
3. headers 只在契約語意需要時宣告。
