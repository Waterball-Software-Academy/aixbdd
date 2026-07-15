# kind: identity — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 identity 的依賴（SSO／IdP：Keycloak 等）。entry 樣板：assets/dependencies.template.yml（identity 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/identity.yml。

## 測試範圍與保真度天花板（先於一切）

1. 測試面以 A（seed 身分：建 user／簽 token／備 claims）為主；SUT 自驗 JWT 時
   的 stub JWKS 為 B 特例（騎 api 形態，複用 api kind 常數句式）。
2. 保真度天花板（必讓使用者知情）：bypass 替身測的是「SUT 的授權邏輯」，
   永遠不是「SSO 整合本身」——token parsing／signature／audience／scope／
   過期皆測不到，補位是 BDD 層之外的真 IdP 整合測試。
3. SSO redirect 流程面為範圍外（E2E 層）。

## truth 取得分流（依序嘗試，取得即停）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 realm export／
   OIDC discovery 文件，優先採用。
2. native：專案的 IdP 可匯出 realm（Keycloak realm-export.json）或有
   OIDC discovery endpoint 文件者採用。
3. authored：依 feature truth 推導測試身分約定（alias／roles／claims），
   `evidence: assumed`；推不出角色／claims 者收 `$ASK_BATCH`。

## testability 與 wiring

1. double 二擇一且必須記錄選擇理由（此為 per-dependency 抉擇，寫入 entry 的
   testability_overrides 或經 clarify 拍板）：real-product（Keycloak container
   ＋realm import，保真高、慢）或 generic-stub（bypass 替身，快、受天花板限制）。
   預設住 kind-constants（generic-stub），偏離才 override。
2. `sut_property_overrides`：real-product 時必填（issuer-uri 類 config key）；
   bypass 時免列。

## truth 檔內容

1. 只收本批次 feature truth 會用到的身分（alias／roles／claims），不整包
   照抄 realm；佔位對得上 feature 資料別名。
2. 憑證與 client secret 不落檔（credential 不管理）。
