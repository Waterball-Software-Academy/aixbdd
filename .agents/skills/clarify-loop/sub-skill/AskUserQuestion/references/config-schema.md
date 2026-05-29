# Config Schema — `arguments.yml` 欄位

> 純 declarative schema reference。Phase 1 ASSERT 題目數時 LOAD 此檔取上限值。
>
> 來源：原 `clarify-loop/SKILL.md` `## Config` section。

## §1 必填欄位

| 參數 | 說明 |
|---|---|
| `SPECS_ROOT_DIR` | 便條紙掃描根目錄 |

## §2 選填欄位

| 參數 | 預設 | 說明 |
|---|---|---|
| `CLARIFY_DIR` | `${SPECS_ROOT_DIR}/clarifications` | 澄清紀錄目錄 |
| `MAX_QUESTIONS_PER_ROUND` | 10 | 每回合題目上限（不含 Sub-question）|
| `MAX_OPTIONS_PER_QUESTION` | 4 | AskUserQuestion 的結構限制 |
| `MAX_ROUNDS` | 5 | 同一 payload 最多進行 N 個 Round 後 escalate |

## §3 讀取慣例

呼叫方傳入 `arguments.yml` 路徑或內容；本 skill 不直接讀檔，由 caller 解析後在 DELEGATE payload 內傳值。

## §4 缺值處理

- 必填缺：Phase 1 ASSERT 失敗 → STOP + REPORT
- 選填缺：套預設值
