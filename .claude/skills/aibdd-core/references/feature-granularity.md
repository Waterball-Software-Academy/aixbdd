# Feature 粒度 — Anti-pattern Token 篩檢 + 命名規範

> 純 declarative reference。`/aibdd-form-feature-spec` 寫檔前的兩層守門用此檔判定。
>
> 來源：原 `aibdd-form-feature-spec/SKILL.md` line 47-55 anti-pattern token 清單。
> 跨 skill 共用 → 提升至 aibdd-core hub。

## §1 設計原則

每個 `.feature` 檔對應**單一 operation**（單一 UI click / HTTP call / worker event / domain-service method / utilities function），而非「主流程」「使用者體驗」「策略集合」這類多 operation aggregate。

理由：
- BDD example 必繫於可被驅動的 operation；多 operation 一個檔會讓每條 example 無法獨立執行
- DSL L4 的 callable surface 是 1:1 對應到 `.feature`；多 operation 一個檔會破壞 physical mapping
- Discovery `Step 6` Operation Partition 已把需求拆到 atomic operation 粒度，feature 命名應反映此拆分

## §2 Anti-pattern Token 清單（machine-only prefilter）

寫檔前對 `target_path` 的檔名（去 `.feature` 副檔名）做 token 篩檢，命中任一即拒絕。

注意：**這只是 machine-only prefilter，不是 atomic 判定的充分條件。**
- 命中 token = 一定有問題，直接退回 caller。
- **未命中 token ≠ 一定 atomic**；像 umbrella 名稱、同回合下多種招式、同一檔混多個 command/event，仍需由上游 operation partition 與 semantic gate 判斷。

### 中文 token

- `主流程`
- `流程`
- `體驗`
- `處理`
- `重試`
- `策略`
- `邏輯`

### 英文 token

- `-flow`
- `_flow`
- `experience`
- `handling`
- `management`
- `retry`
- `fallback`
- `policy`
- `logic`

## §3 命中後的處理

由呼叫方 Planner（通常是 `/aibdd-discovery`）回 Operation Partition 重拆，或重命名為 atomic operation 名。

`/aibdd-form-feature-spec` 不對檔名做推測性修正 — REPORT 退回 caller 後由 caller 重新 DELEGATE。

## §4 合格命名範例

- ✅ `提交申請.feature`（單一 UI click → submit-application HTTP call）
- ✅ `驗證會員等級.feature`（單一 domain-service method）
- ✅ `送出 OTP 簡訊.feature`（單一 worker event）

## §5 不合格命名範例（會被拒絕）

- ❌ `電商結帳主流程.feature`（含 `主流程` token）
- ❌ `登入體驗.feature`（含 `體驗` token）
- ❌ `錯誤處理.feature`（含 `處理` token）
- ❌ `payment-fallback.feature`（含 `fallback` token）

## §6 與 §5.1 filename convention 守門的關係

本檔提供的是**命名層 / machine-only prefilter**（§2 anti-pattern token）。
另有**schema 層**守門：`${BDD_CONSTITUTION_PATH}` §5.1 declared `filename.convention` / `filename.title_language`，由各 Planner Step 0/1 抽 axes 後由 `/aibdd-form-feature-spec` last-line guard 強制。

真正的**語意層**「一個 feature = 一個 operation」判定，應由上游 planner 的 operation partition 與 semantic gate 負責，而不是單靠 token list。

兩層獨立、皆須通過。
