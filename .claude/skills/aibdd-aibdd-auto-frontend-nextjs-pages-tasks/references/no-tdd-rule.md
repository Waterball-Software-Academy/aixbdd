# 前端 No-TDD 規則

本 skill 產出的 tasks.md **絕對不可**包含任何 BDD red→green 流程的描述。前端的 quality gate 走「視覺一致 + 行為符合」，不走 cucumber red→green。

## 禁止字眼清單

SOP Phase 3 step 7 會逐字檢查 tasks.md 內**禁止**出現以下任一字串（不分中英）：

| 禁止字串 | 為什麼禁 |
|---|---|
| `red→green` / `red 紅 / green 綠 cycle` | TDD 紅綠重構流程，前端不走 |
| `.feature` 檔（**作為 task 產物時**） | 前端不寫 cucumber feature；唯一例外是**讀 backend feature** 作參考 |
| `step definitions` | 前端不寫 step definition |
| `cucumber` | 前端不跑 cucumber test runner |
| `behave` | 後端 BDD runner，前端碰不到 |
| `aibdd-red-execute` / `aibdd-green-execute` / `aibdd-refactor-execute` | TDD pipeline skill，前端不 invoke |

**例外白名單**（出現以下情境算合法引用，不會被擋）：

- "讀 `specs/backend/packages/.../features/*.feature` 作為 fixture 參考"（中錨內提到 backend feature，OK）
- "前端不走 cucumber red→green"（在 acceptance 段或備註裡聲明，OK）

## 取代方案

| 原本 TDD 會做的事 | 前端的取代方案 |
|---|---|
| 寫 .feature 描述行為 | 在 task 末尾的 **Acceptance** 段用 markdown checkbox 列「視覺一致檢查」+「行為驗收檢查」 |
| 跑 cucumber red 確認失敗 | 用 Playwright 跑視覺截圖比對 + 互動腳本，看「啟動時是否一片白 / 報錯」 |
| 跑 cucumber green 確認成功 | 截圖跟 `${UIUX_PREVIEW_DIR}/*.png` diff <5%，互動跑通 |
| step definition 綁 page object | React component 直接 mount + Playwright `getByTestId` |

## Acceptance 段格式範例

每個 Phase 1 / 2 / 3 task 末尾必須附 acceptance 段，格式如下（這就是「不走 TDD 的取代方案」具體形狀）：

```markdown
**Acceptance**：
- [ ] 視覺：截圖比對 `<UIUX_PREVIEW_DIR>/<frame-png>`，token / 排版 / glow 一致（差異 <5%）
- [ ] 行為：<具體互動行為描述，例：4 位 0-9 不重複才啟用 CTA；按 CTA 後成功導向 /rooms/{code}>
- [ ] 邊界：<具體 edge case，例：違反規則 inline 提示，不發 API call>
- [ ] 整合：<與 MSW handler / api client 串接驗證點，例：handler 在 Network 被命中且回 200>
```

至少有 `視覺` + `行為` 兩條 checkbox；`邊界` / `整合` 看 task 性質決定要不要加。
