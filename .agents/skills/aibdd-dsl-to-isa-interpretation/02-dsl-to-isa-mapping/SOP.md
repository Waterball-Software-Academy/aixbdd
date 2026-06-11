# 目的

把每份 aixbdd 風格 `dsl.yml` in-place 擴充為 runtime 可執行版本（ISA）：補上 `params:` 與 `isa_steps:` 區塊；其餘欄位原樣保留。

緣由：DSL 是推論 SSOT（人讀／planner 寫），ISA 是執行 SSOT（runtime 以專案 `contracts/isa.yml` 的 ISA 指令集之 `format` 對句）。runtime 不認得 `handler`，必須先把每筆 step 機械翻譯成 `isa_steps` 才能跑 red→green。翻譯器與其 Spec Parser 同住本 skill（`scripts/lib/dsl_to_isa/`），共用的 YAML / spec 解析基礎建設則自 aibdd-core 的 `shared.*` 引用、不複製。翻譯規則以翻譯器原始碼 + BDD feature spec 為 SSOT；本檔僅描述呼叫契約、退出碼與 sentinel 處理。

# SOP

1. RESOLVE arguments — 透過 aibdd-core 的 sibling resolver 綁定變數，stdout `KEY=value` 原樣 EMIT；resolver 非 0 退出 → STOP 並透傳 stderr（缺鍵在此一步即擋下）。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   EOF
   ```

2. INVOKE 翻譯器 — 全 phase 機械化，成功時 dsl.yml in-place 更新。翻譯器為單一 web-service 翻譯器，前置檔為專案 `contracts/isa.yml`（必備，ISA 指令集）+ `data/entity_to_table_mapping.yml`（用到 state-* handler 時必備）；兩者皆由專案自備，缺檔即 STOP。退出碼契約：
   1. `0` + stdout `無 dsl.yml 待翻譯`：集合空（idempotent 守則），非錯。
   2. `0` + stdout `summary: first_write_count=X idempotent_skip_count=Y`：翻譯成功。
   3. 非 0 + stderr：STOP，透傳 stderr，不跑後續步驟。常見原因（皆由翻譯器自帶提示訊息）：前置檔缺失（自報路徑與上游修復點，如缺 `contracts/isa.yml`）；handler 不在內建對照表（列出 step `name` 與 unknown handler）；語意檢查失敗（如引用的 entity / 節點不存在）。

   ```bash
   CONTRACTS_DIR=${CONTRACTS_DIR} \
   DATA_DIR=${DATA_DIR} \
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL} \
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR} \
   uv run .claude/skills/aibdd-dsl-to-isa-interpretation/02-dsl-to-isa-mapping/scripts/cli/dsl_to_isa.py
   ```

3. 處理 sentinel — 翻譯後 dsl.yml 若含 `<FILL IN>` sentinel（翻譯器無法自決、須人工補齊的欄位），DELEGATE /clarify-loop 向使用者補齊該欄位並檢查是否有缺漏。sentinel 語意由翻譯器定義：api_call 的 actor 段位，當 operation 帶 `security:` 區塊時出現。
