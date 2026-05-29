# DSL key locale（`$DSL_KEY_LOCALE`）

決定本 phase 產出之 DSL 鍵／佔位語系慣例；結果供後續步驟使用。解析結果下文仍稱 **`$DSL_KEY_LOCALE`**。

1. DERIVE **`$DSL_KEY_LOCALE`**
   1.1 若 arguments 已宣告 `DSL_KEY_LOCALE`，進 **`SOP.md` 步驟 2**。
   1.2 否則自 **`${FEATURE_SPECS_DIR}`**、**`${ACTIVITIES_DIR}`**、**`${PLAN_SPEC}`** 蒐集至多 10 個 basename，依 non-ASCII codepoint 比例分 **`latin-heavy`**／**`non-latin-heavy`**；**`latin-heavy`** → **`$DSL_KEY_LOCALE = en-us`**，進步驟 2。
   1.3 否則 DELEGATE **`/clarify-loop`**、**`phase = dsl-locale`**，**`raw_items`** 含 **`prefer_spec_language`** vs **`en-us`**（說明非英文檔名時鍵 locale 取捨）；**`completed`** 後取得 **`$DSL_KEY_LOCALE`**。
