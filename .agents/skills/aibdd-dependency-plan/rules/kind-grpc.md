# kind: grpc — truth 取得、testability、entry 填寫規定

適用 SOP step 7 對 kind 為 grpc 的依賴。entry 樣板：assets/dependencies.template.yml（grpc 條目）；kind 常數：.claude/skills/aibdd-core/references/kind-constants/grpc.yml。

## 測試範圍（先於一切）

1. 與 api kind 同形的契約測試兩句式：Given 設定 rpc 預期回應（B）＋Then 驗證
   rpc 被呼叫／不被呼叫（E 正反面）。
2. 已知斷言天花板：gRPC 騎 HTTP/2 形態，不得斷言 grpc-status／trailer；
   streaming rpc 的順序語意為範圍外。
3. 句式素材屬 kind 常數，registry 不收。

## truth 取得分流（依序嘗試，取得即停）

1. user-provided：SEARCH `${DEPENDENCIES_DIR}/<name>/` 既有 proto 檔，優先採用。
2. web-official：自 vendor 官方 repo／文件取得 proto（`origin_url` 必填）。
   proto 為原生機器可讀，取得即 `evidence: verified`。
3. 皆無：不得憑印象撰寫 proto，收 `$ASK_BATCH`。

## testability 與 wiring

1. 替身預設住 kind-constants：grpcmock（in-process 或 container），
   需掛載 proto descriptor（由 truth 檔編譯產生）。
2. `sut_property_overrides` 必填（SUT 指向該服務 target 位址的 config key，
   如 grpc.client.<name>.address）。

## truth 檔內容

1. proto 原檔唯讀整包保留（user-provided／web-official 皆同）；本批次相關
   service/rpc 由 feature truth 判定，不另立清單。
2. 認證（TLS／metadata token）語意若真相載明，以註記留在 <name>/ 資料夾，
   憑證不落檔。
