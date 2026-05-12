# Feature File 撰寫規則

## 1. 句型最少化，但剛好必要

句型數量 = 行為形狀數量，不是操作數量。一個句型覆蓋所有「形狀相同但資料不同」的操作。但當行為形狀 genuinely 不同時，給它專屬句型，不強行塞進同一個。

## 2. Data Table 承載結構化輸入與驗證

- When 的參數不寫進句型字串，放進 Data Table 欄位。
- Then 的多欄位驗證不用多行 And，用一張 Data Table。
- Data Table 欄位放橫向（欄位名為 header row，資料為 data row）。
- 欄位名與規格文件中的欄位名保持 1:1 對應。

## 3. Data Driven——守衛條件：前置狀態必須相容

同一個行為、不同的資料 → 同一個 Scenario Outline。差異全部在 Examples table 裡。

**但前提是：所有 Examples 行能共用同一組 Given（前置狀態）。** 若某些行需要額外的 Given 步驟，它們不能與不需要這些 Given 的行放在同一個 Scenario Outline 中——因為 Scenario Outline 的所有行共用同一個 scenario body（含 Given）。

## 4. Examples 覆蓋精準

每一行 Example 都有存在的理由——覆蓋一個等價類別或一個邊界條件。不窮舉所有可能值，選擇能代表該等價類的最小資料集。

- 每個 precondition 的拒絕路徑至少 1 行。
- 每個 postcondition 的驗證至少 1 行。
- 型別變異各 1 行。

## 5. Scenario 結構決策——Outline vs 獨立 Scenario

從句型.md 的 Examples 規劃表，經兩步分群決定每個 Scenario 的結構：

### 非 Flow 決策樹

```
Scenario 結構決策樹：

Step 0: 句型結構分群（前提）
┌─ 所有行的 When+Then 句型結構相同？
│  ├─ 否 → 按句型結構分群（如：成功路徑 vs 失敗路徑）
│  │       每群各自進入 Step 1
│  └─ 是 → 全部一起進入 Step 1

Step 1: 前置狀態分群
┌─ 群內所有行前置狀態相同？
│  ├─ 是 → Outline（若 ≥2 行）或 Scenario（若 1 行）
│  └─ 否 → 按前置狀態再分群
│       ├─ 「（無）」群 → Outline（若 ≥2 行）或 Scenario（若 1 行）
│       ├─ 群 A（相同前置狀態）→ Outline（若 ≥2 行）或 Scenario（若 1 行）
│       └─ 群 B（不同前置狀態）→ 各為獨立 Scenario，各自帶 Given
```

**關鍵：Scenario Outline 的所有行必須共用相同的 scenario body——包括 Given、When、Then 句型。** 句型結構不同的行（如成功路徑 vs 失敗路徑）絕不能合併為同一個 Outline，即使前置狀態相同。

**絕不在 Scenario Outline 中用註解標註「此行需額外 Given」。** 如果需要額外 Given，就必須拆為獨立 Scenario。

**1 行 Example 不用 Scenario Outline。** 若分群後某群只有 1 行，用普通 Scenario 而非 Outline。

## 6. Placeholder 邊界——只參數化資料值，不參數化句型

Scenario Outline 的 `<placeholder>` 只能出現在：
- Data Table 的值欄位（`| <from> | <to> |`）
- Then 斷言中的具體值（`violation_type 為 "<violation>"`）
- Examples table 的資料行

**不可用 placeholder 替換 Given/When/Then 的句型本身。**

## 7. Spec by Example——用具體資料，不用白話描述

Then 斷言必須是具體的值（`version 為 2`），不可是行為描述（`version 增加 1`）。Background 建立的初始狀態必須有明確的值，後續步驟的驗證值都基於這個已知的初始狀態推算。

## 8. Rule 前綴與排序

Rule 命名的 SSOT 為 `aibdd-form-feature-spec/references/format-reference.md`。摘要：

- 4 類前綴：`前置（狀態）` / `前置（參數）` / `後置（回應）` / `後置（狀態）`
- 後置（狀態）可選用子類：`後置（狀態：資料）` / `後置（狀態：外發）` / `後置（狀態：資源）` / `後置（狀態：行為）`
- 前置 Rule 排在後置 Rule 上方
- 每條 Rule 遵循原子化原則（單一主詞 + 單一條件）
- 後置（回應）須通過可測試閘門：能寫成 `Then <主詞> 應為 <具體值>`；不能則改寫為結果值斷言

## 9. Rule 底下用 `Example` 不用 `Scenario`

在 `Rule:` 區塊內，單行測試案例使用 `Example` 關鍵字，不用 `Scenario`。`Scenario Outline` 保持不變。

```gherkin
Rule: 前置（參數）- 房間代碼必須為四位數字
  Example: 房間代碼格式不正確時操作失敗
    ...

  Scenario Outline: 多種格式驗證
    ...
    Examples:
      | ... |
```

## 10. 變數參照用 `$entity.property` 風格

當 Data Table 或 Examples 中需要引用前置步驟建立的實體屬性時，一律使用 `$entity.property` 語法，不用中文白話描述。

- 引用 ID：`$使用者.id`、`$A.id`、`$lead.id`
- 引用其他屬性：`$學員.email`、`$journey.name`
- `entity` 為該實體在 Given 步驟中的名稱或 name 參數值
- 此風格同時適用於 When Data Table、Then Data Table、Examples table
