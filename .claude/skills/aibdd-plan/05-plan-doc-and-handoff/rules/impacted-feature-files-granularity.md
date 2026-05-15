# Impacted Feature Files 顆粒度

- **計列單位**：以「**單一 `.feature` 檔**」為單位，**逐檔一行 bullet**；不**跨檔**合併、不**按 rule** 拆開。
- **canonical 路徑**：每行 bullet 必為 repo-relative path，且能在 `${FEATURE_SPECS_DIR}` 下解析；絕對路徑／symlink／鏡像副本一律不收。
- **order = 預期 TDD phase order**：list 之順序代表下游 `/aibdd-tasks` 之 RED→GREEN→REFACTOR 推進順序，**不是**字母排序、**不是** `ls` 順序。
- **scope 衍生**：list 必由本輪 `$BOUNDARY_DELTA`／`$DSL_DELTA`／`$IMPLEMENTATION_MODEL` 推導；**禁止**整包 `${FEATURE_SPECS_DIR}/` 全列除非本輪 plan 真的涵蓋全包。
- **共享 operation**：多 `.feature` 共用一條 operation slice 時，仍**逐檔列**；下游每檔自有 TDD phase。
- **partial 不收**：若本 plan 無法確定 narrowing 到某子集（譬如 `$IMPLEMENTATION_MODEL` 證據不足以分檔），**列全部**比列模糊子集更可被下游處理；連 narrowing 都做不到時請改回頭 `DELEGATE /clarify-loop`。
- **rationale 為選用**：path 之後可接 ` — ` 短說明，**不影響** path 本身之 canonical 性。

# 反例

- 把 `submit.feature` 與 `cancel.feature` 合成一條 bullet 寫成 `submit-and-cancel.feature`——下游 TDD 無法分檔推進。
- 一條 bullet 寫成 `submit.feature - 主要 happy path`（用「主要 happy path」當 scope qualifier）——rule-level scope 不屬本節，違反「逐檔」單位；如需強調，改寫 path 後的 rationale 文字，**不**改 path 本身。
- 用 `ls` 順序排——order 必須對齊 TDD phase，否則下游 task 規劃會亂序。
- 列了 `${FEATURE_SPECS_DIR}/draft/foo.feature` 但該檔屬 Discovery 草稿尚未 accepted——只有已 accepted 之 feature 才算 impacted。

# 禁止自生

- **不得**列 `${FEATURE_SPECS_DIR}` 下不存在之 path；列前先 ASSERT 路徑可解析。
- **不得**列 Discovery 階段尚未生成 rule-only `.feature` 之候選——「impacted」之定義是「本輪 plan 實際驅動且已存在於 boundary 真相中之 feature」。
- **不得**自加 `${FEATURE_SPECS_DIR}` 以外之 path（譬如 archived features 或其他 boundary 之 feature 路徑）。
