# Example 重構判斷（抽變數 / 抽 DataTable）

觸發：在 loop 邊界 —— 完成一個 example（其涉及 dsl_step 經 d 確認全部 `# done`）後、
**進入下一個 example 或結束 loop 前**，做一次重構判斷。獨立步，不併入 DSL→ISA（c）。
範圍：**限該 FP 內，可跨 feature**；不跨 FP。
最高原則：**禁止過於複雜** —— 只在明顯提升「重用／可讀」時才重構；拿不準是否更簡單就不重構。
凡因此變更 `.feature` 或搬移 dsl_step，一律經 `/clarify-loop`（帶完整 Example）確認後才改。

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

### 3. 抽 DataTable（放進 dsl example）
- 一句帶很多變動欄位、或同 FP 多個 example 僅「資料不同」→ 考慮把變化抽成
  **DataTable 放進該 `.dsl.feature` 的 step**（dsl_step `params` 以欄位清單 `[a, b]` 宣告），讓業務句保持簡潔。
- 僅在「明顯更清楚／收斂重複」時才做。

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
