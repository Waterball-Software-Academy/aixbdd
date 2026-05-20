# `discovery-sourcing.md` Template

> 使用方式：
> 1. 保留章節結構。
> 2. 將所有 `<...>` placeholder 替換成當輪內容。
> 3. 若某列不適用，刪除整列，不要留空白占位。
>
> 用語（寫進 discovery report 時請遵守）：
> - **`function package`**：boundary 底下 `packages/NN-<slug>/` 這一層模組單位（內含 `features/`、`dsl.yml` 等）。
> - **slug 語系**：所有 `<plan-package-slug>` 與 `<function-package-slug>` 之 `<slug>` 主體**必須**以 `${PROJECT_SPEC_LANGUAGE}` 自然語撰寫（zh-hant 寫繁中、en-us 寫英文 kebab-case…）。技術 token（API field／DSL token／domain acronym）可保留英文。**嚴禁** romanization（漢語拼音／kana／romaji／romaja）或無理由整段英譯作為 fallback；詳細 IF/THEN guards 見 `01-sourcing-and-packaging/SOP.md` 步驟 0.6。

## Impact scope

- 本輪問題一句：<用一句話描述這輪 discovery 要補強、修改或新增什麼；寫現在式，不要寫 implementation 細節>
- 納入範圍：<列出本輪明確納入的行為、規則、資料或契約範圍>
- 明確排除：<列出這輪刻意不處理的相鄰需求，避免 scope 漂移>

## Impact matrix

> **唯一**承載處：這輪 specified raw idea 對 boundary 內既有規格檔（含 function package 下 `.feature`、`dsl.yml`，以及 `data/`、`contracts/` 等）造成什麼 **impact**。
> **每個檔案至多一列**：`變更類型` 寫本輪對該檔的最終狀態；`impact 描述` 用一句話寫滿「對齊依據；本輪對規格內容的影響」，必要時用分號串接，**禁止**再開第二張表重述同一批檔案。
> **逐檔列舉（尤其 `.feature`）**：第一欄須為**單一規格檔**之相對路徑（見表內列名），**禁止**以單列 `packages/.../features/*.feature` 之 **glob** 代替多個實際檔案列，以免下游（例如 plan phase 之 DSL synthesis）無法機械建立「每檔一迭代」之 workset。若專案刻意約定「僅用目錄 glob 閉包、不展開逐檔」，**必須**在下方 `Notes` **明文化**該約定與風險，不得依預設留白。
> **`變更類型` 即語意標籤**：`新增`／`更新`／`條件式更新`／`讀取對照` 已涵蓋「本輪新產出規格檔」vs「在既有檔上變更」之區分；**不要**重複另加第三欄或其它平行欄承載同一語意。
> `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${PLAN_SPEC}` 等 plan-side artifacts **不**進此表。

| 既有規格檔（相對 `${TRUTH_BOUNDARY_ROOT}`） | 變更類型 | impact 描述 |
|---|---|---|
| `<packages/<function-package-slug>/features/<feature>.feature>` | `讀取對照`／`更新`／`新增`／`條件式更新` | <先用既有規格界定邊界；再寫本輪要加／要改的規格句子> |
| `<packages/<function-package-slug>/dsl.yml>` | `讀取對照`／`更新`／`新增` | <同上> |
| `<data/<file>.dbml>` | `讀取對照`／`更新`／`新增` | <同上> |
| `<contracts/<file>.yml>` | `讀取對照`／`更新`／`新增`／`條件式更新` | <同上> |

## Function package charters

> 這一節回答：**每個涉及的 function package 的定義與職責邊界是什麼？**
> `Packaging decision` 裡列到的每一個 function package，**都必須**在這裡有一張對應小卡。

### `<packages/<function-package-slug>>`

- **職責一句**：<用一句話定義這個 function package 對外行為主軸>
- **納入**：<列出這個 package 負責承載的規格切片>
- **排除**：<列出刻意不承載的相鄰能力，避免邊界漂移>
- **本輪變更型態**：`impact-only`／`new-package`／`mixed`
- **本輪規格增量**：<這輪要補哪些規格增量；一句話，不要寫實作步驟>

### `<packages/<第二個-function-package-slug>>`（若本輪涉及多包，複製此小卡）

- **職責一句**：<...>
- **納入**：<...>
- **排除**：<...>
- **本輪變更型態**：<...>
- **本輪規格增量**：<...>

## Packaging decision

- 新 plan package：`<NNN-<plan-package-slug>>`
- 本輪涉及的 function packages：
  - `<packages/<function-package-slug>>`（`<沿用 | 新開>`）
  - `<packages/<function-package-slug>>`（`<沿用 | 新開>`）
- function package 決策：<明確寫「本輪只新開 plan package；既有 function package 僅 impact」或「本輪需新開 function package，原因是 ...」>

## Resolved sourcing decisions（已拍板）

- <決策一句>：**<是／否／選項>**；<依據一句，指到既有 truth 檔名或訪談事實>
- <決策一句>：**<是／否／選項>**；<依據一句>

## Notes

- `Impact matrix`：**唯一**表格；每列對應**一個**規格檔與本輪 raw idea 的 impact（含只讀對照與實際變更，統一寫在 `impact 描述`）；**`.feature`** 與其它將被後續 phase 機械對拍之檔案**必須**各佔一列並填 **`變更類型`**，**不得以 glob 省略展開**。若確採 glob 閉包策略，須於本節第一句明載。
- `Function package charters`：每個 function package 的職責邊界與本輪增量；**與** `Packaging decision` **必須一致**。
- 若本輪只新開 plan package、沿用既有 function package，請在 `Packaging decision` **明寫**：「**新開的是 plan package，不是 function package**」。
