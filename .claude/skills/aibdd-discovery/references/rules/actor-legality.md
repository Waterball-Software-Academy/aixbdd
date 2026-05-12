# Discovery — Actor 合法性

Feature / Activity 顆粒度與 Actor 合法性規則。`check_actor_legality.py` 依本檔比對 `@Actor` 標記；非法 Actor 須收回觸發者的上游 Rule。

核心等式：**1 Feature File = 1 API Endpoint = 1 外部觸發動作**。

## §合法 Actor 清單

Activity Diagram 的 STEP / BRANCH 只允許以下兩類 Actor：

| 類別 | 定義 | 範例 |
|------|------|------|
| **外部使用者** | 透過 UI / CLI 主動操作系統的人類角色 | 行銷人員、客服夥伴、助教 |
| **第三方系統** | 自有系統控制範圍**以外**的外部服務 | 影片平台（Webhook）、金流系統（Callback） |

判別「第三方系統 vs. 內建系統」的唯一標準：**該系統是否在我方控制範圍之外？**

> 注意：`discovery.03-activity-analyze` 的 Activity model 採 UI-first action 顆粒度。若第三方系統只是 UI 行動完成過程中的下游處理邊界，必須依 [`activity-action-granularity.md`](activity-action-granularity.md) 收入該 Action 的 postcondition，不建立 Actor。第三方系統只有在它本身就是此 Activity 的外部觸發來源（例如 webhook / callback flow）時，才適用本節合法 Actor 判斷。

- 影片平台 Webhook → 第三方 ✓
- 金流系統回呼 → 第三方 ✓
- 自有系統判斷是否建立 Journey → 內建 ✗（收入上游 Rule）

## §非法 Actor 清單

**內建系統**（自有系統內部的自動化邏輯）一律禁止作為 Actor：無外部觸發 → 無 API Endpoint → 無獨立 Feature File。

`DEFAULT_BLOCKLIST` 檢出詞彙：`系統` / `內建系統` / `自有系統` / `System` / `Backend` / `Server` / `Service`。

## §判斷步驟

```
收到一個業務動作 →
  Q1: 誰觸發？
    → 外部使用者 / 第三方系統 → 建立獨立 STEP + Feature File ✓
    → 內建系統自動執行 →
      Q2: 被哪個外部觸發的 STEP 連鎖引發？
        → 找到上游 → 收入該觸發者的 Feature 作為 Rule ✓
        → 找不到 → 標 CiC(GAP)
```

**轉化範例**

❌ 錯誤（內建系統作為獨立 STEP）：
```
[STEP:1] @行銷人員 {features/lead/手動新增Lead.feature}
[STEP:2] @系統 {features/journey/判斷是否建立Journey.feature}  ← 無外部觸發
[STEP:3] @系統 {features/sop/自動綁定SOP.feature}              ← 無外部觸發
```

✅ 正確（內建邏輯收入觸發者的 Feature）：
```
[STEP:1] @行銷人員 {features/lead/手動新增Lead.feature}
  手動新增Lead.feature 中以 Rule 表達：
    Rule: 後置（連鎖）- 已購課 Lead 自動建立 Journey 並設定 Stage 為等待開課
    Rule: 後置（連鎖）- Journey 建立後自動綁定對應 SOP
```

## §allow-list YAML schema

當專案確有特殊例外（例：該詞彙在此 domain 實為外部服務）→ 於 `${SPECS_ROOT_DIR}/.actors.yml` 明列：

```yaml
# specs/.actors.yml
allow:
  - "Webhook"     # 第三方通知通道
  - "Callback"    # 第三方回呼

block:
  - "內部排程器"  # 額外補強 domain-specific 內建系統詞彙
```

`check_actor_legality.py` 會以 `DEFAULT_BLOCKLIST ∪ block` 作為阻擋集、`allow` 作為例外放行。

## §下游視圖傳播

| 視圖 | 影響 |
|------|------|
| Activity | 不得出現 @內建系統 作為 STEP Actor；內建邏輯從圖上移除 |
| .feature | 內建系統邏輯以 Rule 呈現在觸發者的 Feature 中 |
| api.yml | 不為內建系統邏輯建立獨立 Endpoint |
| erm.dbml | 不受直接影響（資料模型由 Feature 的 datatable 決定） |
