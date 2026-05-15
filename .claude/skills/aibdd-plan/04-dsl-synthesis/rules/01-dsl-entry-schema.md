# DSL entry schema

**operation 請求面集合相等**（`S_contract`／`S_dsl`）、**`default_bindings` 四鍵**、**L1／datatable 可讀性壓力**：**`02-dsl-parameters-coverage.md`**。

---

## Schema Def

- **必備 keys**：`id`／`L1`／`L2`／`L3.part`／`L4.{surface_id, surface_kind, callable_via, param_bindings, datatable_bindings, default_bindings, assertion_bindings, source_refs, preset}`。**不**強制頂層 `source`；`entries` 即 registry 條目本體。

### L2 / L3 / L4 分層語意
- `L1` ＝ 業務句（自然語言，BDD reader 可讀）

- `L2` ＝ 語意脈絡（`context`／`actor`）
  - **`actor`**：此 entry 對應 L1 句中**主導該動作或陳述**的一方，填**業務角色名**（例如 `學員`、`顧問`、`店長`）。**不是** IAM／技術 principal、**不是** `param_bindings` 的鍵名、**不必**與 OpenAPI `*Id` 欄位字面相同——識別子仍由 L1 佔位符與 bindings 表達。

- **`L3.part`**：本 entry 在 boundary **handler routing** 中的 **part 名**（分流／履約語意）之 **SSOT**，**必須**與該次載入之 routing 檔定義**逐字一致**；**禁止**自造名、縮寫、或與已定義 part 名不符。
  - **反例**：`L3.part: api-call`（或任何**未**出現在當前 boundary `handler-routing.yml` 之 `routes`／`dsl-writing-rules-for-each-part` 的名稱）——違反 part 嚴格映射；web-backend 須為 `operation-invoke` 等已定義 part。

- **`L4` 各鍵**（與示範 YAML 同序可讀；細部 **`default_bindings` 四鍵**見 **`02-dsl-parameters-coverage.md` §2）：
  - **`surface_id`**：此 entry 在 DSL registry 內之**穩定識別名**（與實際 URL／method 字面無需相同；用於對齊「同一個可被呼叫的作用面」）。
  - **`surface_kind`**：`state-builder`／`operation`／`state-verifier`／`operation-response-success-and-failure`／`operation-response-success-readmodel`／`time-control`／`external-stub`／`fixture-upload`／`internal-decision` 之一；決定 handler／preset 期望的履約形狀（例如 `operation` 對應 API 呼叫面）。值必須與當前 boundary `handler-routing.yml` 之 `routes[].part`／`handler` 對齊；不得自造別名（譬如 `loader` 為已淘汰名稱——前置狀態之 Given 應為 `state-builder`）。
  - **rule kind → surface_kind 對應**（與 `${SKILL_DIR}/04-dsl-synthesis/SOP.md` 步驟 4.3.2 之分流表互為 SSOT；若兩處不一致以 SOP 為準）：
    | atomic rule 開頭語意 | 必出 `surface_kind` |
    |---|---|
    | `Rule: 前置（參數）…` | 併入 `operation` entry 之 `param_bindings`（不獨立成 entry） |
    | `Rule: 前置（狀態）…` | `state-builder`（每個參與 entity／DBML table 各一筆） |
    | `Rule: 前置（時間）…` | `time-control` |
    | `Rule: 前置（外部）…` | `external-stub` |
    | feature 之操作目標 | `operation`（每 feature 至少一筆） |
    | `Rule: 後置（狀態）…` | `state-verifier` |
    | `Rule: 後置（回應）…` | `operation-response-success-and-failure` 或 `operation-response-success-readmodel` |
  - **`callable_via`**：作用面**具現化通道**（例如 `http`）；實際允許值以 boundary／runner 契約為準。
  - **`preset`**：堆疊與 routing 對齊用物件。**`name`**＝所用 boundary preset（例如 web-backend）；**`handler`**＝該 routing 檔在 **`L3.part`** 對應項上的 `handler` 名，逐字一致；**`variant`**＝工具鏈／stack 變體 id。**不得**再寫 **`part`**（`part` 僅 **`L3.part`**）。
  - **`param_bindings`**：由 L1 句内佔位符 **key** 對應到 registry **`target`**（contract／data 等錨點）之 map；**`target` 前綴**見下方 **Binding allow-list**。
  - **`datatable_bindings`**：DataTable 業務欄與 **`target`** 之對應；無則空 map（示範 `{}`）。
  - **`default_bindings`**：以 atomic rule（或等價依據）背書之預設輸入列表；每一筆**須**含 **`target`**、**`value`**、**`reason`**、**`override_via`**。
  - **`assertion_bindings`**：Then／斷言面之 map（鍵須遵守 **identity opacity ban**）；無則空 map。
  - **`source_refs`**：向外規格之指針物件——**`contract`**（OpenAPI 等）、**`data`**（DBML／entity YAML）、**`boundary`**（handler-routing 等）、**`test_strategy`**；未使用之鍵填 `null`。

- **L1 為業務句**：寫法為一句可被 BDD reader 讀懂的自然語言；**禁止**寫成技術 request shape 之 mirror。
  - **反例**：`L1: "POST /orders 回傳 201"`——把 request shape mirror 進 L1，破壞業務可讀性。

- **stateless 句讀**與「一 entry 一 atomic rule」：見 **Naming policy 第 5 點**。
- **identity opacity ban**：ID-like binding target 之 key 必含 `XXX ID`（譬如 `旅程 ID`、`stage ID`）；**禁止**把 identity 藏在 `旅程`／`階段`／`預約單` 等抽象名後。
  - **反例**：`L4.assertion_bindings` 用 key `旅程` 指向 `data/journeys.dbml#journeys.id`——identity 不顯式，違反本 ban；應改 key 為 `旅程 ID`。

- **dynamic ID**（系統於 scenario 內產生之 id 占位）：見 **Naming policy 第 6 點**。

### Example dsl.yml
**示範**（單一 `entries` 條目，無情景代入；`contracts/...` 為占位）。

```yaml
# 單一 entry 形狀示範（無情景代入）。其餘見同檔所引 `02-dsl-parameters-coverage.md`。

entries:
  - id: example.entry.shape
    L1:
      when:
        - 學員 "{學員Id}" 對資源 "{資源Id}" 送出請求
    L2:
      context: 佔位說明；須可對回真實 atomic rule。
      actor: 學員
    L3:
      part: operation-invoke
    L4:
      surface_id: example.invoke
      surface_kind: operation
      callable_via: http
      preset:
        name: web-backend
        handler: operation-invoke
        variant: stack-variant-id
      param_bindings:
        學員Id:
          target: contracts/example.openapi.yml#/components/schemas/ExampleRequest/properties/actorId
        資源Id:
          target: contracts/example.openapi.yml#/components/schemas/ExampleRequest/properties/targetId
      datatable_bindings: {}
      default_bindings:
        - target: contracts/example.openapi.yml#/components/schemas/ExampleRequest/properties/mode
          value: standard
          reason: |
            出處：`specs/features/example-resource-request.feature`；
            對應 atomic rule（建議以檔內錨點對齊）：`#當請求未帶入-mode-時以-standard-模式處理`。
            該規則載明未指定 mode 時履約語意等同 standard，與多數呼叫端未顯式傳入 mode 的常態高頻情境一致，
            故此 `default_bindings.value` 取 `standard`，並非無依據的黑箱預設。
          override_via: same-step DataTable 欄位 mode
      assertion_bindings: {}
      source_refs:
        contract: contracts/example.openapi.yml
        data: null
        boundary: null
        test_strategy: null
```

---

## Naming policy（precision keystone）

1. **動詞與介面詞**

atomic rule 用業務動詞時，L1 不得自長 HTTP method／API verb／status code／路徑樣式作 placeholder。

- ✗ rule 寫「建立會員資料」，L1 卻以 REST 鏡像句敘述，例如 **`When 使用者呼叫 "POST /members" 且回應狀態碼為 201`**（業務句被 method／path／status 綁架）
- ✓ rule 寫「建立會員資料」，L1 寫 **使用者建立會員資料 `"{會員 ID}"`**；method／path 由 contract 透過 `L4.source_refs.contract` anchor，**不入** L1

2. **數值與技術欄位**

rule 未提之數字／欄位——SLA、retry、timeout、版本號、過期時間、上下限、通道（email／SMS）——DSL 不得自填 placeholder 或 default value。

- ✗ rule 寫「失敗會通知使用者」，DSL 綁 `{重試次數: 3}`／`default: 通道=email`
- ✗ rule 寫「金額不可為負」，DSL 補 `{金額上限: 100000}`
- ✓ rule 寫「失敗會通知使用者」，DSL 只綁 `{通知對象}` 之 assertion，retry／通道留待 rule 明示後再加

3. **與原文衝突的語氣（hedging）**

rule 用「必須／不得／一律／僅」時，DSL 之 expected value 不得弱化為「通常」「視情況」「可能」。

- ✗ rule 寫「**必須**通過二階段驗證」，DSL assertion 寫 `通常會通過二階段驗證`
- ✓ rule 寫「**必須**通過二階段驗證」，DSL assertion `Then 系統應已通過二階段驗證`

4. **識別欄與佔位／key 對齊（勿模糊化單位）**

若 `param_bindings`（或 datatable 業務欄）之 **`target`** 對應 contract 上之**識別子**（例如 `actorId`、`studentId`、`resourceId`、`*Id` 結尾欄），則 L1 `{placeholder}` 與 YAML **key** 必須讓讀者看得出「此處是 id」：`學員Id`、`資源Id`、`會員 ID` 等皆可；**禁止**僅用 **`學員`**、**`標的`**、**`對象`**、**`干係人`** 等籠統詞，彷彿欄位可能是名稱／email／任意 scalar。

- ✗ key `干係人`／`標的` 綁到 `.../properties/actorId`、`.../properties/targetId`——單位不明
- ✓ key `學員Id`／`資源Id` 綁到同上——與識別子語意一致（與上方 **identity opacity ban**、`assertion_bindings` 鍵須含「… ID」同精神）

5. **Stateless 句讀與一 entry 一 atomic rule**

每條 L1／Then／And **單獨讀**必能識別 business subject、lookup identity、expected data／effect；`And` 句**不繼承**上一 `Then` 之 subject。單筆 entry 之 L1 **對應單一 atomic rule**——不得把多條 rule 擠進同一句敘述。

- ✗ 一筆 entry 的 L1：`使用者送出訂單，系統計算金額並扣款並寄信`——多 rule 混在一句
- ✓ **拆成多筆 entry**（每筆 L1 對應一條 atomic rule），承接上例可寫成例如（占位／字串實參形式對齊 **第 7 點**）：
  - entry A／L1：`使用者 "{使用者Id}" 送出訂單 "{訂單Id}"`
  - entry B／L1：`系統依訂單 "{訂單Id}" 計算應付金額並完成扣款`
  - entry C／L1：`系統對訂單 "{訂單Id}" 寄出訂單確認信`
- ✓ **單一 atomic rule 可承載**時：L1 只寫那條 rule 的業務句——若某 rule 只規範「使用者送出訂單」，L1 不得在同一句併入計價／扣款／寄信；其餘行為須另有 atomic rule 與對應 entry。

6. **DSL entry `L1`：字串參數與整數參數**

- **字串參數** 在 **`L1` 句內**須以 **`"…"`** 標出邊界，占位置於引號內，例如 **`"{學員Id}"`**。**禁止**拿 **`「…」`** 充當與 Gherkin 對齊時的字串邊界。
- **整數參數** 在 **`L1` 句內不加**外層 **`"…"`**（例如 **`{上限人數}`**，或模板允許之裸整數 **`8`**、**`201`**）。**禁止**為整數語意寫成 **`"8"`**。

- ✗ `學員 「{學員Id}」對資源 「{資源Id}」送出請求`
- ✓ `學員 "{學員Id}" 對資源 "{資源Id}" 送出請求`（與本檔 Example `dsl.yml` 一致）
- ✗ `房間人數上限為 "{8}"`（整數參數誤用字串引號）
- ✓ `房間人數上限為 {上限人數}`（或你們句型模板中的裸整數 **`8`**）

---

## Binding：`target` 前綴 allow-list

（寫入 registry 之 binding **target** 字串必須落在下列前綴之一；與機械檢查腳本衝突時以腳本／boundary CI 為準。）

- `contracts/<file>.yml#<op>.request.{params|body|headers}.<name>` 或 `...response.<field>`
- `data/<file>.dbml#<table>.<column>`（`web-service` 類 boundary 優先 DBML）
- `data/<file>.yml#<entity_id>.<field>`（legacy YAML）
- `response:$.<jsonpath>`（含 `response:$.__http.*`）
- `fixture:...`／`stub_payload:...`／`literal:...`

## Datatable 業務投影

- cell 為**業務 column**，**禁止** raw JSON／YAML／整顆 DTO／DB row dump；nested aggregate 用 `group` 與 `item_field` 由 handler 還原。
  - **反例**：單一 cell 塞整段結構化 payload（應拆成多欄或 `group`／`item_field`）。

    ```gherkin
    Given 系統已建立下列訂單明細：
      | 訂單代號 | 品項資料 |
      | o-001   | {"items":[{"sku":"A","qty":2}]} |
    ```

---

# 禁止腦補

- **不得**為 raw 未提之欄位開 placeholder（譬如 raw 寫「失敗會通知」，DSL 不得加 `{retry 次數}`／`{timeout 秒數}` 之 L1 placeholder）。
- **不得**為「方便寫 DSL」自加 placeholder 而非 atomic rule 真正需要的——placeholder 必須**對 rule 有意義**或**對 stateless lookup 必要**，二者皆不滿足則不增 placeholder。
- **不得**為「補齊四層」自填 L2／`L3.part` 但無 atomic rule 依據；缺資訊則回頭 `DELEGATE /clarify-loop`。
- **不得**新增無 atomic rule／operation／state 依據之 **binding key**、**datatable 欄**、**`target` 錨點**。
