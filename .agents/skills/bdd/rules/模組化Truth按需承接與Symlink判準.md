# Rule 1 - 必須由 feature 路徑承接同模組 DSL 與實際使用的共用 rows

- Level: `MUST`
- 對 `{介面}/{模組}/{能力}.feature`，必須以同一個 `{介面}/{模組}/dsl.md` 作為模組 DSL，不可從能力名稱猜測其他 DSL 來源。
- 模組 DSL 必須完整讀取；介面根 `{介面}/dsl.md` 只補讀該 feature 實際使用的共用 DSL rows，不可為單一 feature 預先載入全部共用 rows。
- 查找每個 feature step 時，候選定義集合必須由「同模組 DSL」與「該 step 實際使用的介面根共用 rows」合併而成。

## Good Example

- 這個例子是好的，因為它由 feature 所在模組推導 DSL，且只補入實際使用的共用 row。

```md
目標：
- `features/backend/三連猜/三連猜一次出手與換手.feature`

必讀：
- `features/backend/三連猜/dsl.md`

按 feature steps 補讀：
- `features/backend/dsl.md` 內「回應包含錯誤碼 {code}」row

不載入：
- 根 DSL 內未被此 feature 使用的房間查詢與聊天共用 rows
```

## Bad Example

- 這個例子是壞的，因為它忽略同模組 DSL，並把整份介面根 DSL 當成所有 feature 的預設上下文。

```md
目標：
- `features/backend/三連猜/三連猜一次出手與換手.feature`

處理：
- 不讀 `features/backend/三連猜/dsl.md`
- 只讀完整的 `features/backend/dsl.md`
- 從其他模組找看起來相似的句型
```

# Rule 2 - 合併查找必須得到唯一 DSL 定義

- Level: `MUST`
- 每個 feature step 在同模組 DSL 與實際使用的介面根共用 rows 合併查找後，必須恰好得到一個可落地定義。
- 合併後為零定義，代表 DSL 缺失；合併後為多重定義，代表 DSL 邊界或詞彙不唯一。兩者都必須停止受影響範圍並回交 `/dsl-refine`。
- `/bdd` 不得自行新增、改寫或擇一採用 DSL 定義來解除零定義或多重定義。

## Good Example

- 這個例子是好的，因為它只承接唯一結果，遇到零定義則停止並回交。

```md
案例 A：
- step：`那麼回應包含錯誤碼 "INVALID_GUESS"`
- 模組 DSL：0 筆
- 根共用 DSL 的實際使用 rows：1 筆
- 合計：1 筆
- 決策：依唯一 DSL 定義進入 `/bdd red`

案例 B：
- step：`那麼對手看見新的密文`
- 模組 DSL：0 筆
- 根共用 DSL 的實際使用 rows：0 筆
- 合計：0 筆
- 決策：停止受影響範圍並回交 `/dsl-refine`
```

## Bad Example

- 這個例子是壞的，因為它遇到多重定義後仍在下游自行挑選。

```md
step：
- `當玩家送出猜測`

合併查找：
- 模組 DSL：1 筆
- 根共用 DSL：1 筆
- 合計：2 筆

決策：
- 挑參數較少的定義繼續實作
- 不回交 `/dsl-refine`
```

# Rule 3 - 不得在 BDD 重新分類模組與共用句型

- Level: `MUST`
- 句型應屬模組 DSL 或介面根共用 DSL，已由 `/dsl-refine` 的 truth ownership 決定；`/bdd` 只能承接，不得重新分類。
- 即使某句型看似可被其他模組重用，也不得在本輪把它搬到介面根 DSL、複製到另一個模組 DSL，或以 step definition 的共用程度反推 truth 歸屬。
- 若既有歸屬造成缺失、重複或無法唯一落地，必須回交 `/dsl-refine`，不能以下游目錄整理取代上游決策。

## Good Example

- 這個例子是好的，因為它把 DSL 歸屬問題交回 truth owner。

```md
觀察：
- 「拒絕空白訊息」只存在於 `房間聊天/dsl.md`
- 新 feature 位於另一模組，且合併查找為零定義

處理：
- 停止受影響範圍
- 回交 `/dsl-refine` 判斷句型應維持模組專屬或提升為根共用
```

## Bad Example

- 這個例子是壞的，因為它以實作方便為由自行改變 DSL truth 歸屬。

```md
處理：
- `/bdd` 認為句型以後可能共用
- 把 row 從 `{介面}/{模組}/dsl.md` 搬到 `{介面}/dsl.md`
- 繼續撰寫 step definitions
```

# Rule 4 - Truth symlink 只在專案已採用時按模組投影

- Level: `MUST`
- Symlink 是條件式的專案承接策略；只有專案已採用 truth symlink 時才套用本 Rule，不得要求所有專案新增 symlink。
- 已採用時，功能 truth 必須以 `{介面}/{模組}` 資料夾為單位投影，讓該模組的 feature files 與 `dsl.md` 一起承接。
- 介面根共用 `dsl.md` 可以獨立投影，供多個已投影模組承接共用 rows。
- 禁止複製 truth 內容、逐一為 feature 建立 symlink，或在已投影的模組資料夾內再為 feature 或 `dsl.md` 建立逐檔連結。

## Good Example

- 這個例子是好的，因為既有 symlink 專案以模組資料夾維持 feature 與 DSL 的同一 truth 邊界。

```md
專案現況：
- 測試樹已採用 `specs/truth/features/**` symlink

投影：
- `backend/features/三連猜` -> `specs/truth/features/backend/三連猜`
- `backend/features/dsl.md` -> `specs/truth/features/backend/dsl.md`

結果：
- 模組內 feature files 與模組 `dsl.md` 一起投影
- 根共用 DSL 維持單一來源
```

## Bad Example

- 這個例子是壞的，因為它複製內容並在模組內建立逐檔連結，破壞資料夾級 truth 邊界。

```md
投影：
- 複製 `specs/truth/features/backend/三連猜/dsl.md` 到測試樹
- 對三連猜的每一個 `.feature` 分別建立 symlink
- 已連結 `backend/features/三連猜` 後，再在其中連結 `dsl.md`
```

# Rule 5 - Focused runner 必須支援模組、單一 feature 與 scenario name

- Level: `MUST`
- 承接模組化 truth 的 focused runner 必須能分別以模組、單一 feature，以及 scenario name 執行測試。
- 三種入口都必須沿用同一套專案測試樹與 step definitions，不得為了 focused rerun 複製 feature 或另建平行 runner。
- 若現有 runner 缺少任一層級，必須先把該缺口列為測試入口阻塞或待補能力，不得宣稱模組化 truth 已完整承接。

## Good Example

- 這個例子是好的，因為同一 runner 能逐層縮小回饋範圍。

```md
focused 入口：
- 模組：`./run-bdd.sh 三連猜`
- 單一 feature：`./run-bdd.sh 三連猜/三連猜一次出手與換手.feature`
- scenario name：`./run-bdd.sh --name "玩家一次出手成功提交"`
```

## Bad Example

- 這個例子是壞的，因為它只有整包入口，並以複製 feature 規避 runner 能力缺口。

```md
現況：
- runner 只能執行全部 features

處理：
- 把目標 feature 複製到暫存目錄
- 以另一套命令只跑該副本
- 宣稱已支援 focused rerun
```
