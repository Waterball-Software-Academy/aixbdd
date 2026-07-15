# kind: store — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 store 的依賴。entry 樣板：assets/dependencies.template.yml（store 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/store.yml。

## 測試範圍（先於一切）

1. store kind 的測試面是外部儲存版的 entity 指令：Given 資料狀態預存（後門寫入）、
   Then 資料狀態驗證（後門讀取斷言，非同步引擎帶 eventually）。
2. 讀寫一律走測試側後門 client，不經 SUT 的 HTTP API。
3. 與 RDB 同構的 NoSQL 不屬本 kind（見 scope-discriminant 範圍判別式 3）。

## truth 取得分流（per-engine）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 truth 檔，有則優先採用。
2. per-engine native truth（專案內找得到即採，`source: native`）：
   - mongodb：collection 的 `$jsonSchema` validator（`format: json-schema`）
   - elasticsearch：index mapping 或 index template（`format: index-template`）
   - redis：RediSearch `FT.CREATE` schema 或 redis-om 宣告（`format: ft-schema`；少見）
3. authored 約定檔（上述皆無時自產，`source: authored`、`evidence: assumed`）：
   依樣板 surface 區塊撰寫 convention.md——redis 為 keyspaces
   （pattern／value_schema／ttl，pattern 用 colon 分隔慣例）、s3/minio 為
   buckets（name／object_key_pattern／content_type）、document store 為
   collections（name／doc_schema_ref）。約定內容必須從 feature truth 與
   `${PLAN_SPEC}` 推得；推不出的 key 佈局收進 `$ASK_BATCH`。

## testability 與 wiring

1. double 恆為 real-product；per-engine container 預設（image／ports／
   service_connection）住 .claude/skills/aibdd-core/references/kind-constants/store.yml，entry 依 engine
   查表不重抄，偏離才填 testability_overrides。custom step 模版（A 預存／
   D 驗證）同樣內建於 kind-constants，registry 不收句式素材。
2. `@ServiceConnection` 不支援的 engine（如 minio）`sut_property_overrides` 必填。
3. elasticsearch 的 index refresh 延遲：對應 collections 條目標 `refresh_lag: true`，
   驗證句素材強制 eventually。

## 約定檔內容（surface 由 truth 檔承載，entry 不抄）

1. 只收本批次 feature truth 會預存或驗證的 keyspace／bucket／collection，
   不做全庫盤點。
2. 每條 pattern 的佔位變數（如 {userId}）必須對得上 feature 中的資料別名。
3. TTL 只在業務語意需要（過期行為）時宣告。
4. 真相未載明的 value 內容不得斷言——約定檔明注保守約束（只斷言存在性／TTL）。
