---
name: hierarchical-skill-creator
description: "Hierarchical skill 撰寫格式。"
metadata:
  user-invocable: true
  source: project-level
---

# Hierarchical Skill 撰寫格式 — 九大特徵

每條規則以 bullet + 強情態定義 + 行內 `✗`／`✓` 對照呈現；先把規則本身定義清楚再貼具象正反例，避免脫錨。

## 1. 雙層 SKILL.md / sub-SOP 結構

頂層 `SKILL.md` 只負責 PRINCIPLE 宣告 + Phase 路由；實際步驟一律下放到 `NN-<slug>/SOP.md`。

頂層 `SKILL.md` 的允許內容（且僅這些）：

```text
# <skill-title>                       ← H1 一個
<一句話開場>                          ← optional
## PRINCIPLE: <name1>                 ← H2，name 必為命名式
  - <bullet>
## PRINCIPLE: <name2>
  - <bullet>
...
# SOP                                 ← H1 一個
<延遲控制 boilerplate 兩條>           ← 見 §6
0. <參數綁定步驟>                     ← optional，唯一允許在頂層的 non-EXECUTE 步驟
1. EXECUTE the sub-sop: `NN-<slug>/SOP.md`
2. EXECUTE the sub-sop: `NN-<slug>/SOP.md`
...
N. <告知使用者語句>                   ← optional，single-line
```

- 頂層 SOP 步驟動詞限制：除 phase 0 之 parameter binding（`grep` / `READ arguments.yml`）外，禁止業務動詞（`READ` / `WRITE` / `CREATE` / `DERIVE` / `THINK` / `FAITHFUL REASONING` 等）直接出現於頂層 SOP 編號步驟。落盤動作一律下放至 sub-SOP。
  - ✗ `1. READ ${PLAN_SPEC} 拆解每段話為 $P …`（落盤動詞洩漏到頂層）
  - ✓ `1. EXECUTE the sub-sop: 01-sourcing-and-packaging/SOP.md`

- 一對一綁定：頂層 `EXECUTE` 必須一步對一個 `NN-<slug>/SOP.md`；禁止一步同時對應多個 sub-SOP 或多個 sub-SOP 對應同一步。
  - ✗ `1. EXECUTE 01-xxx/SOP.md 與 02-yyy/SOP.md`
  - ✓ `1. EXECUTE 01-xxx/SOP.md` + 另起一行 `2. EXECUTE 02-yyy/SOP.md`

- 頂層膨脹禁區：頂層 SOP 不得內嵌 30+ 步細節流程，必須透過 sub-SOP 分散。違反時 lazy load 失效，首回應 latency 拉高、context 浪費。
  - ✗ 頂層連續寫 `READ / WRITE / THINK` 30 步細項
  - ✓ 頂層只 3–5 步 `EXECUTE` 路由，每個 sub-SOP 自己長到 8–12 步

## 2. `## PRINCIPLE: <名稱>` 前置區 + `# SOP` 主體區的硬切分

全域不變式只放在 SKILL.md 的 PRINCIPLE 區；`# SOP` 區只列流程步驟，不重述 principle。

```text
# <skill-title>
[<開場一句>]

## PRINCIPLE: <命名式 name 1>
- <atomic rule bullet>

## PRINCIPLE: <命名式 name 2>
- …

# SOP
< SOP 步驟 >
```

- 位置強制：`## PRINCIPLE:` block 必須全部出現在 `# SOP` heading 之前；禁止在 `# SOP` 區下再開 `## PRINCIPLE:` 子節。
  - ✗ `# SOP\n## PRINCIPLE: 後置補充 …`
  - ✓ 所有 `## PRINCIPLE:` 集中在 `# SOP` 之前

- 命名強制：每個 PRINCIPLE 必須有命名（`PRINCIPLE: CWD 為產出錨點`），禁止裸 `## PRINCIPLE` 或泛稱（如 `PRINCIPLE: 一些重要原則`）。
  - ✗ `## PRINCIPLE` 或 `## PRINCIPLE: 注意事項`
  - ✓ `## PRINCIPLE: STRICT SOP`

- Atomic 強制：PRINCIPLE 區內條文須是 atomic rule（一句話一條），不講脈絡敘事、不夾雜歷史決策。
  - ✗ `因為之前發生過 X 問題，所以我們現在會 Y …`（脈絡敘事）
  - ✓ `產出物一律落在 CWD 內，禁止寫到 CWD 外的絕對路徑。`

- 不重述強制：同一 invariant 禁止在 SOP 個別步驟以括號提示反覆出現。
  - ✗ `1. EXECUTE 01-xxx/SOP.md （提醒：路徑不要寫到 CWD 外面喔）`
  - ✓ 把該 invariant 寫成一條 `## PRINCIPLE: CWD 為產出錨點`，SOP 步驟保持乾淨

必備內建 PRINCIPLE（任一 hierarchical skill 都必須含這三條，逐字或語意等價）：

- `PRINCIPLE: STRICT SOP` — 鎖死「依序不漏步 + 明示步號 + 限縮延長推理」；完整 boilerplate 見 Appendix A。
- `PRINCIPLE: 長流程待辦（兩層）` — 跨對話 compact 後可還原進度；完整 boilerplate 見 Appendix B。
- `PRINCIPLE: Artifact output contract` — Deny-by-default 的 side-effect 契約，唯 CREATE/WRITE/UPDATE 明標的 artifact 才能落盤；完整 boilerplate 見 Appendix C。

三條皆逐字 / 語意等價複製到頂層 SKILL.md PRINCIPLE 區；缺一即視為非合規 hierarchical skill。這三條是「條款化」的版本，分別對應 §6（延遲控制）／§7（編號鏡像 + Todo 實體化）／§4（授權白名單）的形式約束 — §4/§6/§7 是約定，這三條 PRINCIPLE 是寫入產物。

其他常見但 optional 的 PRINCIPLE：

- `PRINCIPLE: CWD 為產出錨點` — 凡有 filesystem 產出物必備。

## 3. 步驟以 D/S/I 大寫動詞起首

每個 SOP 步驟以封閉動詞集合內的 ALL-CAPS 動詞鎖頭，同一語意永遠用同一動詞。

動詞表（封閉集合）：

- Data ingress: `READ` / `SEARCH` / `PARSE`
- Data egress: `WRITE` / `UPDATE` / `CREATE` / `CREATE DIR` / `CREATE DIRS ONLY`
- Data derive: `DERIVE` / `ASSERT`
- Reasoning: `THINK` / `FAITHFUL REASONING`
- Control flow: `EXECUTE` / `DELEGATE` / `LOOP` / `FOR EACH` / `IF` / `END`

步驟句型：`<整數編號>. <ALL-CAPS 動詞> [<目標物 = 路徑/變數/集合>][：補充描述]`

- 動詞位置強制：動詞必須出現於步驟編號 `N.` 與一個空格之後，緊接步驟句首；禁止動詞嵌在描述中段。
  - ✗ `1. 先看一下 layout 規則檔，了解一下路徑怎麼解析。`
  - ✓ `1. READ rules/specs-root-layout.md 作為路徑解析 SSOT。`

- 同義 lock：同一動作必須永遠用同一動詞 — 「讀取／閱讀／查看」一律寫成 `READ`，「想／看／了解／補充／記得」禁止出現於 SOP。
  - ✗ `2. 想想看命名語系該選哪個，可以對齊既有的 package 命名。`
  - ✓ `2. DERIVE $package_naming_language：對齊既有 plan package 命名慣例。`

- 單一主動詞：一個步驟禁止混兩個主動詞；「READ X 並 WRITE Y」必須拆成兩步。
  - ✗ `3. READ template 並 WRITE 報告。`
  - ✓ `3. READ templates/foo.template.md。` + `4. WRITE ${PLAN_REPORTS_DIR}/foo.md（依模板）。`

- 目標物單一明確：動詞之後若有目標物，必為單一明確 entity（檔案路徑／`$var`／`${VAR}`／集合名）；禁止目標物模糊（「相關檔案」「對應位置」）。
  - ✗ `5. UPDATE 相關檔案。`
  - ✓ `5. UPDATE ${PLAN_SPEC}：追加 pointer 與摘要。`

## 4. 每一步的「授權產出物」白名單條款

任何會改變檔案系統的步驟必須夾白名單尾句，未列入名單者一律視為禁止。

凡步驟動詞 ∈ { `WRITE`, `UPDATE`, `CREATE`, `CREATE DIR`, `CREATE DIRS ONLY` } 必須符合以下兩條件：

- 目標路徑明指：用 `${VAR}` placeholder 鎖定，禁止裸路徑、禁止模糊量詞（「相關檔案」「需要的話」「順便」「適當地」「合理範圍內」）。
  - ✗ `把 sourcing 報告寫好，順便更新 spec.md 和相關檔案。`
  - ✓ `WRITE ${PLAN_REPORTS_DIR}/function-packaging.md（章節以 template 為準）。`

- 句末白名單聲明：三種句型擇一，不得省略：
  1. 「本步僅允許 <動詞> <目標> [與 <動詞> <目標>]。」
  2. 「禁止建立／更新 <列舉物>。」
  3. 「不在 <路徑> 下新建 <類型>，除非 <明文條件>。」
  - ✗ `5. CREATE function package 目錄結構，需要的話一起把 dsl / feature / activity 骨架補起來。`
  - ✓ `5. CREATE DIRS ONLY：於 ${TRUTH_BOUNDARY_PACKAGES_DIR} 建立各 ${TRUTH_FUNCTION_PACKAGE}，僅建 ${ACTIVITIES_DIR}、${FEATURE_SPECS_DIR} 骨架。禁止建立 dsl.yml、.feature、.activity、${CONTRACTS_DIR} / ${DATA_DIR} 內容或其它規格檔。`

- READ/SEARCH/THINK/DERIVE 純觀察：搭配頂層 PRINCIPLE「READ/SEARCH/THINK/DERIVE 觀察到的路徑只可作為分析依據，不得被順手建立、寫入、更新或補骨架」，杜絕「LLM 看到就建」。
  - ✗ `READ contracts/foo.openapi.yml；如不存在則自動建立空骨架。`
  - ✓ `READ contracts/foo.openapi.yml。若不存在則 DELEGATE /clarify-loop 詢問是否新建。`

- 多 artifact 必逐項授權：一步若輸出 ≥ 2 個 artifact，必須列舉每個都允許；禁止只給概述。
  - ✗ `WRITE 報告與相關檔案。`
  - ✓ `WRITE ${PLAN_REPORTS_DIR}/foo.md 與 UPDATE ${PLAN_SPEC}。本步僅允許 WRITE 該報告與 UPDATE ${PLAN_SPEC}。`

## 5. `${UPPER_VAR}` 外綁路徑 vs `$lower_var` 內推變數

兩套變數命名必須各司其職：`${UPPER_SNAKE}` ＝外部綁定；`$lower_snake` ＝ SOP 內 `DERIVE`。

- `${...}`（UPPER_SNAKE）＝外部綁定
  - 來源: `arguments.yml` / `rules/*-layout.md`
  - 用途: 路徑、常數
  - 範例: `${PLAN_SPEC}`、`${ACTIVITIES_DIR}`
- `$...`（lower_snake 或 MixedCase）＝ SOP 內 `DERIVE`
  - 來源: SOP 內 `DERIVE`
  - 用途: 中間值、集合
  - 範例: `$package_naming_language`、`$UAT_FLOWS`、`$Actions`

- 路徑錨定強制：任何路徑必須以 `${...}` 開頭錨定；禁止裸路徑（`./specs/`、`specs/plans/`、絕對路徑）。
  - ✗ `1. READ specs/plans/001-foo/spec.md。`
  - ✓ `1. READ ${PLAN_SPEC}。`

- `${...}` 不可 DERIVE：`${...}` 必為「外部已綁定」的鍵；SOP 內不得 `DERIVE` 出新的 `${...}`。新中間值一律用 `$lower_var`。
  - ✗ `2. DERIVE ${NEW_SLUG}：對齊既有命名。`（不該創造新 `${...}`）
  - ✓ `2. DERIVE $plan_package_slug：形式 NNN-<slug>。`

- 大小寫 lock：`${...}` 與 `$...` 前綴與大小寫必須綁定；禁止 `${lower_case}` 或 `$UPPER_CASE`。
  - ✗ `${naming_lang}` 或 `$NEW_SLUG`
  - ✓ `${PLAN_PACKAGES_DIR}` + `$package_naming_language`

- 單一寫法：同一個值在不同步驟禁止同時用 `${X}` 與 `$x` 兩種寫法。
  - ✗ Step 2 寫 `${PLAN_SPEC}`、Step 5 寫 `$plan_spec`
  - ✓ 全檔一致用 `${PLAN_SPEC}`

## 6. 「禁止提早閱讀」+「沒授權不准 EXTENDED THINKING」的延遲控制條款

SKILL.md `# SOP` heading 之後、第一個步驟之前，必須出現兩條延遲控制 boilerplate。

位置：緊接 `# SOP` heading 下方、Step `0.` 或 `1.` 之前。

Boilerplate（語意鎖死，可改文字）：

```text
# SOP

請執行到哪讀到哪，千萬不要提早閱讀後續文件，這會讓用戶起始體驗到的延遲度
很久，SOP 寫啥就做啥，沒叫你 [THINK/REASONING] 就絕對不准啟用 EXTENDED THINKING。

0. <parameter binding>
1. EXECUTE …
```

- 條款 1：lazy-load 強制：禁止提早讀後續檔案（後續 sub-SOP / rules / templates）；只在當步授權範圍內 READ。
  - ✗ `# SOP\n開始前請先：讀完所有 sub-SOP 與 rules 目錄下全部規則檔 …`
  - ✓ `# SOP\n請執行到哪讀到哪，千萬不要提早閱讀後續文件 …`

- 條款 2：限縮延長推理：未標 `THINK` / `FAITHFUL REASONING` 的步驟禁止啟用 extended thinking；該步以最直接可做之 `READ`／`PARSE`／`DERIVE`／`WRITE`／`UPDATE`／工具呼叫達成。
  - ✗ `1. EXECUTE 01-xxx/SOP.md（先對整個流程做一次完整推演，列出所有可能 edge case 再開始）`
  - ✓ `1. EXECUTE 01-xxx/SOP.md`（直接執行，不額外深思）

- sub-SOP THINK 步驟自帶停損：sub-SOP 內 `THINK` 必為明文標頭，且必須附「本步只產出判斷，不寫檔」之類短句呼應。
  - ✗ `4. 想一下 function package 數量該怎麼拆 …`
  - ✓ `4. THINK：拆解 function package 數量（1..*）；bottom-up 規則見 rules/function-package.md。本步只產出判斷，不寫檔。`

- 預讀禁區詞：以下開場語全部禁止 — 「開始前請先讀完所有 sub-SOP / rules」「對整體流程做一次完整推演」「列出所有可能 edge case」「心中先有藍圖再開始第 1 步」。
  - ✗ 任一上列開場
  - ✓ 直接寫 boilerplate 兩條後接 Step 0/1

## 7. Phase 編號 = 資料夾名 = TodoWrite Tier 0 編號

三件事必須保持鏡像並且強制以工具實體化 Tier 0 Todo。

資料夾命名 regex：`^[0-9]{2}[a-z]?-[a-z0-9-]+$`
例：`01-sourcing-and-packaging`、`02-activity-analyze`、`02b-feature-file-list-analyze`、`03-atomic-rules-analyze`。（`02b` 表 phase 2 之內的補丁式分流，仍排在 03 之前。）

鏡像關係：

```text
SKILL.md # SOP step N     →  指向第 N 個（按 NN 前綴排序的）sub-folder
NN-<slug>/                →  filesystem 上的第 N 個資料夾
Todo Tier 0 (N)           →  「(N) 展開並執行至完成：<NN-<slug>>/SOP.md」
```

- 資料夾編號強制：sub-SOP 資料夾必須以 `NN` 前綴開頭（可帶 lowercase 字母如 `02b`）；禁止無編號名（`sourcing/`、`activities/`）。
  - ✗ `sourcing/SOP.md`、`activities/SOP.md`
  - ✓ `01-sourcing-and-packaging/SOP.md`、`02-activity-analyze/SOP.md`

- EXECUTE 順序對齊：SKILL.md 第 N 個 `EXECUTE` 步驟必須指向第 N 個 `NN-*` 資料夾（按字典序）；禁止順序倒置或跳號。
  - ✗ `1. EXECUTE 02-...` + `2. EXECUTE 01-...`（順序倒置）
  - ✓ `1. EXECUTE 01-...` + `2. EXECUTE 02-...`

- Todo Tier 0 工具實體化：進入 sub-SOP 之前必須用 TodoWrite / `TODOCREATE` / `TASKCREATE` 建立 Tier 0 清單；禁止只在 chat 內口頭列點。
  - ✗ `我接下來會做這四步：sourcing、activity、feature、atomic-rules（不開 Todo）`
  - ✓ 開 TodoWrite 列出 `(1)..(4)` 四條 Tier 0 entry，並隨進度勾選

- Tier 1 lazy expand：Tier 1（phase 內細項）只在「進入該 phase」當下展開；不得為後續 phase 預開細項，避免 Todo 與 SOP 脫節。
  - ✗ 一開工就把所有 phase 的 Tier 1 細項全部展開
  - ✓ 進入 (1) 時才展開 (1-1)..(1-N)，其餘 phase 在 Tier 0 維持單列

## 8. 每個 sub-SOP 資料夾的 mini-tree 慣例

每個 sub-SOP 資料夾必須按固定 mini-tree 分層，只允許自內相對引用。

```text
NN-<slug>/
  SOP.md                            ← 必，流程主文
  rules/                            ← optional：規則檔（雙段式，見 §9）
    <topic>.md                      ← 任何規則主題（命名規則、邊界規則、欄位規則 …）
  templates/                        ← optional：結構骨架（fenced block 逐字複製對象）
    <name>.template.md
  assets/                           ← optional：非規範性附件
    templates/<name>.example.md     ← 語感對照範例
  reasoning/                        ← optional：被 SOP THINK 步驟 READ 的延伸推理
    <topic>.md
```

- 檔案分層強制：規則類檔放 `rules/`；模板類檔放 `templates/`；範例放 `assets/templates/*.example.md`；推理腳本放 `reasoning/`。禁止不同類檔平鋪在同一層。
  - ✗ `02-x/actor.md` + `02-x/initial-feature.md` + `02-x/control-flow.md`（規則／模板／推理混平鋪）
  - ✓ `02-x/rules/activity-actor.md` + `02-x/templates/initial-feature-file.template.md` + `02-x/reasoning/activity-control-flow.md`

- 自內相對引用強制：sub-SOP 內所有 link 必為自資料夾根的相對路徑（例：`rules/foo.md`、`templates/bar.template.md`）。
  - ✗ `READ /Users/foo/notes/actor-tips.md`（絕對路徑破壞 CWD 錨點）
  - ✓ `READ rules/activity-actor.md`

- 跨 phase 反向引用禁區：引用同 skill 內其他 phase 須透過 SKILL.md 路由或 sibling skill 的 `references/`；禁止 `../NN-other/...` 直連，會造成 phase 之間循環依賴。
  - ✗ `READ ../01-sourcing-and-packaging/rules/shared-naming.md`
  - ✓ 把共享規則上提到 SKILL.md 同層或 sibling reference hub（e.g. `aibdd-core::FILENAME.md`），各 phase 各自 LOAD

- 跨 skill 直連禁區：禁止 `../../other-skill/...` 直連；跨 skill 必須用 sibling skill 的 reference hub 慣例（e.g. `aibdd-core::FILENAME.md` 載入）。
  - ✗ `READ ../../aibdd-core/references/ssot/spec-package-paths.md`
  - ✓ 在當 phase 引用 `aibdd-core::ssot/spec-package-paths.md`（由 host 解析）

## 9. 規則檔的 `# <規則主題>` + `## Good` + `## Bad` 三段式

所有 `rules/*.md` 必須用固定三段骨架：H1 寫規則主題與正向條款、H2 `## Good` 與 H2 `## Bad` 給具象正反例。

```markdown
# <規則主題>

- <強情態 bullet 1>
- <強情態 bullet 2>
...

## Good

- <具象正例 1>
- <具象正例 2>
...

## Bad

- <具象違例情境 1>
- <具象違例情境 2>
...
```

- H 階層強制：規則主題用 `#` (H1)、`Good` 與 `Bad` 必為 `##` (H2) 子節；禁止 Good/Bad 用 `#` (H1) 與主題同階，兩者必須從屬於主題之下。
  - ✗ `# Actor 命名規則` 之後再開 `# Good` 或 `# Bad`（H1 同階）
  - ✓ `# Actor 命名規則` 之後接 `## Good` 與 `## Bad`（H2 子節）

- 強情態詞強制：H1 body 每條 bullet 必須含強情態詞之一作為條款主動詞 —「得 / 不得 / 禁止 / 僅當…才 / 必須 / 不准」；禁止 hedging 詞（「通常」「一般來說」「有時候」「建議」「最好」「可以」「應該」）。
  - ✗ `Actor 通常是使用者，也可以是其他系統。一般來說建議畫人類角色 …`
  - ✓ `不得將產品內建系統、自有後端、排程、worker、資料庫列為獨立 Actor。`

- Atomic 強制：H1 body 一條 bullet 必為一條 atomic rule，禁止混合多條件；多條件必須拆成多條 bullet。
  - ✗ `Actor 是 UI-facing 人類，且第三方系統若入口為 Webhook 也可以是 Actor，並且名稱要唯一 …`（一條塞三條規則）
  - ✓ 三條 bullet 各寫一條 atomic rule

- Good/Bad 具象強制：`## Good` 與 `## Bad` 區每 bullet 必為「具象情境」；禁止抽象陳述（「要寫清楚」「不要亂寫」），LLM 無法反向偵測。Bad bullet 尤須是「會被誤判為合規但實際違例」之具象情境。
  - ✗ `Bad：不要把不適合的東西畫成 Actor。`
  - ✓ `Bad：使用者在 UI 按下付款後，另立金流閘道、寄信服務為 Actor，把非入口的下游互動當成圖上獨立身分。`

- 三段完整性：禁止缺任一段（規則主題 / `## Good` / `## Bad`）；`## Bad` 條數 ≥ H1 body 條款的關鍵 case 數，讓 LLM 能反向偵測自己輸出。
  - ✗ 只有 `# Actor 命名規則` + `## Bad`，無 `## Good`
  - ✓ 三段齊備，Good 與 Bad 覆蓋每條關鍵正向規則

## 一句話總結

「Phase router + 授權白名單 + 強情態動詞 + 外綁變數 + 編號鏡像 Todo」 — 形式上把 LLM agent 當成嚴格受限狀態機在寫：每一步授權什麼動詞、寫什麼路徑、寫到哪裡，全部在文本層硬編；自由發揮的空間只留在被明確標 `THINK` / `FAITHFUL REASONING` 的格子裡。

# Appendix — 必備 PRINCIPLE Templates

下列三條 PRINCIPLE 為任一 hierarchical skill 之必備內建條款（見 §2 必備內建 PRINCIPLE 清單）。Boilerplate 已外移至 `templates/` 下對應檔案，作為逐字複製對象；建立新 skill 時請從這三個檔逐字 / 語意等價貼進目標 `SKILL.md` 的 PRINCIPLE 區，缺一即視為非合規 hierarchical skill。

## Appendix A — `PRINCIPLE: STRICT SOP`

Template 檔：`templates/principle-strict-sop.template.md`

這條條款做兩件事：

- 第 1 點「依序不漏步 + 明示步號」→ 強制執行可觀測性，對齊 §7 的 Tier 0 / Tier 1 編號鏡像。
- 第 2 點「限縮延長推理」→ 把 §6 的「禁止提早閱讀 / 沒授權不准 EXTENDED THINKING」規範化為產物層條款，sub-SOP 才能在個別步驟以「本步只產出判斷，不寫檔」「依該步授權」之類短句呼應。

使用方式：

1. READ templates/principle-strict-sop.template.md
2. 逐字 COPY 整段（從 `## PRINCIPLE: STRICT SOP` 起到第 2 點末）
3. PASTE 進新 SKILL.md 的 `## PRINCIPLE: …` 區

## Appendix B — `PRINCIPLE: 長流程待辦（兩層）`

Template 檔：`templates/principle-long-process-todo.template.md`

這條條款做兩件事：

- 把 §7 的「Phase 編號 = 資料夾名 = TodoWrite Tier 0 編號」規範化為產物層條款，明指 Tier 0 / Tier 1 的展開時機與工具化義務。
- 解決 compact 後的進度還原問題 — Tier 0 是 phase 級錨點、Tier 1 是該 phase 當下細項，避免一次展平整個流程造成 Todo 與 SOP 脫節。

使用方式：

1. READ templates/principle-long-process-todo.template.md
2. 逐字 COPY 整段（含 Tier 0 / Tier 1 兩個 markdown 範例 fenced block）
3. PASTE 進新 SKILL.md 的 `## PRINCIPLE: …` 區

## Appendix C — `PRINCIPLE: Artifact output contract`

Template 檔：`templates/principle-artifact-output-contract.template.md`

這條條款做兩件事：

- 把 §4 的「授權產出物白名單」規範化為產物層的全域硬限制 — 任何 CREATE/WRITE/UPDATE 必須在某個 SOP 步驟中明文標示，否則禁止落盤。
- 配合 READ / SEARCH / THINK / DERIVE 為「純觀察動詞」的約定：觀察到的路徑不得反向變成寫入目標，杜絕 LLM「順手補骨架」行為。

使用方式：

1. READ templates/principle-artifact-output-contract.template.md
2. 逐字 COPY 兩個 bullet
3. PASTE 進新 SKILL.md 的 `## PRINCIPLE: …` 區
4. 確保 SOP 各步的白名單尾句（§4）與本條 PRINCIPLE 相互呼應

## 檔案佈局

本 skill 的當前 mini-tree（呼應 §8 慣例）：

```text
hierarchical-skill-creator/
  SKILL.md                                           # 本檔；九大特徵 + Appendix
  rules/
    writing-style-principles.md                      # skill 撰寫排版原則
  templates/
    principle-strict-sop.template.md                 # Appendix A 逐字複製對象
    principle-long-process-todo.template.md          # Appendix B 逐字複製對象
    principle-artifact-output-contract.template.md   # Appendix C 逐字複製對象
```
