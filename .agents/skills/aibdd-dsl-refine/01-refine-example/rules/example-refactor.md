# Example 重構判斷（抽變數 / 抽 DataTable）

觸發：在 loop 邊界 —— 完成一個 example（其涉及 dsl_step 經 d 確認全部 `# done`）後、
**進入下一個 example 或結束 loop 前**，做一次重構判斷。獨立步，不併入 DSL→ISA（c）。
範圍：**限該 FP 內，可跨 feature**；不跨 FP。
最高原則：**情境好讀優先、禁止過於複雜** —— 只在明顯提升可讀時才重構；拿不準是否更簡單就不重構。
相似但不同的 step 句式**不需要合併或對齊**：合併與共用僅適用於「format 完全相同」的定義（技術唯一性）；語意相近但措辭不同的句子各自保留，不得為收斂語料改寫 `.feature` 句面。
凡因此變更 `.feature`、搬移或**改名** dsl_step，一律經 `/clarify-loop`（帶完整 Example 或衝突清單與擬定名稱）確認後才改；改名方案未經同意不得落檔。

## 判斷項

### 1. 抽變數（format 參數化）
- 把 dsl_step 業務句中、會在「同 FP 其他 example（含跨 feature）」變動的字面值（人名、數字、日期等）
  抽成 format 變數 `{Name}`（搭配 isa_steps 的 `{{Name}}` 內插，或 dsl_step `params` 預設）；
  使後續 example 重用同一條 dsl_step（也讓 worklist 收斂，不必建近乎重複的 dsl_step）。
- 列舉型固定描述（如「一般公司」「季繳」）維持字面、**不抽**。

### 2. 放置：共用 → `{FP}/dsl.yml`，專屬 → `{feature}.dsl.yml`
- 參數化後若該 dsl_step **跨 ≥2 feature（同一 FP）共用** → 寫進 **`{FP}/dsl.yml`**（不存在則以模版建立），
  原 `{feature}.dsl.yml` 不再重複該條。
- 僅單一 feature 用到 → 留在該 `{feature}.dsl.yml`。
- **不跨 FP** —— 別的 FP 不共用此條。

共用偵測有兩個觸發點，避免「逐 feature loop 看不到其它 feature → 漏抽 → 重複」：
- **先找後建（c 步）**：worklist 對某未完成 step 帶 `reuse` 提示（FP 內已有同 format 定義）時，
  c 步不重建——既有定義在別 feature → 當下就 hoist 到 `{FP}/dsl.yml` 共用。
- **收尾去重（主 SOP step 11）**：loop 結束跑 `scripts/cli/detect_shared_dsl.py`，把仍跨 ≥2 feature
  重複的條目補抽到 `{FP}/dsl.yml`。兩者都遵守本節放置規則與「禁過複雜」。
hoist 時**保留 `# done`**（標記是持久真相），刪 `{feature}.dsl.yml` 重複條，兩 feature 共用一條。

### 3. 抽 DataTable（放進 dsl example）
- 一句帶很多變動欄位、或同 FP 多個 example 僅「資料不同」→ 考慮把變化抽成
  **DataTable 放進該 `.dsl.feature` 的 step**（dsl_step `params` 以欄位清單 `[a, b]` 宣告），讓業務句保持簡潔。
- 僅在「明顯更清楚／收斂重複」時才做。

### 3b. 降階（DataTable → 單行）：刪欄位前必過的前置條件

反向操作——SBE 草稿是 DataTable，refine 時為了「降回 4 參數以內的單行句」而刪掉欄位、
把值收進 `params` 預設。這條降階是 fitbook B-66 的**真因**：`累計凍結次數` 明明被同一個
Example 的 Then 直接驗證，卻被當成「未被驗證的欄位」一併刪掉，兩個原本不同的 example
於是塌縮成同一支 `freeze_count: 0` 的 dsl_step，seed 與斷言互相矛盾，拖到 green 才炸。

降階前逐欄位過這三條，任一不過即**不得刪除該欄位**：

1. **被同一個 example 的 Then 直接驗證的欄位不得刪除**——欄位值出現在該 example 任一
   Then／And-after-Then 的斷言裡（含衍生語意，如 `累計凍結次數` → `剩餘凍結次數 = 上限 − 累計`），
   一律保留在句面或 `params`，且值必須與斷言自洽。
2. **被 When 送出的欄位不得刪除**——它是本例的輸入，刪掉即改變測試意圖。
3. **驅動本例行為（driving-only）的欄位不得刪除**——即使沒有 Then 斷言它，只要它是被測
   規則的判斷輸入（見 SBE `rules/pm-writing-rules.md` 可核對性 1 的 driving-only 形態），
   刪掉就換掉了等價類。此類欄位保留時，`{feature}.dsl-intent.md` 須留有「為何不斷言」的記載。

只有「三條皆不成立」的 NOT NULL 陪襯欄位才可收進 `params` 預設並降回單行。

降階後**必跑 `expand_isa.py`**：`seed-assertion-consistency` lint 會比對展開後的 seed 值與
Then 斷言值／Example 標題的數值語意，誤刪被驗證欄位一律在此被攔下（exit 3）。
`{feature}.dsl-intent.md` 若記載了該 example 原始的 DataTable 欄位，降階前後逐欄比對一次，
少掉的欄位都要能對應到上面三條的「皆不成立」。

## 禁止（過於複雜）

- 不為消除重複，把不相關的東西硬塞同一條 dsl_step 或同一張 DataTable。
- 不讓 example 因抽象化而變難讀 —— 讀者要一眼看懂在測什麼。
- **不跨 FP 共用**。
- 拿不準是否更簡單時，就**不重構**，保持現狀。

## Good

```text
同 FP 兩個 feature 各有 example，業務句只差人名與積分：
  feature A："王業務" … 積分 50 分      feature B："李經理" … 積分 80 分
→ 抽變數成 `"{業務}" 提交…積分 {積分} 分`，且因跨 feature 共用 → 寫進 {FP}/dsl.yml，兩 feature 共用一條。
```

## Bad

```text
- 把「提交審核單」與「查詢清單」兩個無關操作硬塞同一條 dsl_step 的 DataTable。
- 為了 DRY 把 example 改成十幾欄大表，讀者看不懂在測什麼（過於複雜）。
- 把參數化 dsl_step 拿去給「別的 FP」共用（違反不跨 FP）。
```
