# Planner Contract

所有 Planner 共用的推理與落地契約。每個 Planner 以 `==> LOAD aibdd-core::report-contract.md` 載入本檔，不得複製本檔內容至自身 references。

---

## §REPORT 匯報

Planner Step 5（Quality Gate）通過後，**主匯報**以白話文 1–3 句在終端機回報使用者；**不**用 JSON / YAML 包裝主匯報內容。

**成功主匯報格式**（範例，依本次實際內容組句）：

> {Planner 簡稱} 完成。產出 {主要 artifact 列表（1 行可述完）}。{若有未解決疑問則一句帶過；無則省略}

**失敗主匯報格式**：

> {Planner 簡稱} 卡關於 {失敗的 check 名稱}：{一句白話原因}。建議下一步：{回 Step N 補 X / 改 Y}。

**規則**：
- 主匯報全程白話中文，不用 code fence、不用 JSON / YAML、不列欄位 schema
- 產物清單以一行內或短 bullet 表達；具體路徑由實際 artifact 落地處告知
- Planner 之間若需傳結構化資料，已透過 artifact 落地（activity / feature / coverage 等），不靠 REPORT 攜帶

**便條紙附件（若本回合有產生 / upstream backtrack 提議）**：

主匯報後可附一段結構化便條紙清單，給 carry-on / orchestrator 機讀（**不取代主匯報，只是附件**）。沿用 CiC 便條紙格式：

```yaml
new_sticky_notes:
  - kind: "GAP | ASM | BDY | CON"
    scope: "local | upstream_backtrack"
    target_planner: "<downstream proposal 指向之 upstream planner id；scope=local 時省略>"
    content: "<description>"
    # upstream_backtrack 提議可額外攜帶 backtrack-proposal-protocol §2 欄位
```

無便條紙 → 整段省略；不寫空清單。

---

## §User-Facing Message Style

Planner 與 user 對話的所有訊息（含中途進度、ASCII preview、決策請求、REPORT）一律遵循以下五條：

1. **不洩漏 SOP 內部術語**：禁出現 `Step 2a` / `Step 2b` 等子活動編號、「靜默完成」「progressive disclosure」「推理包」「三問自檢」「reason-to-change」「diff_set」「axis_unit_mapping」「CiC」「便條紙 KIND」等內部機制詞。對 user 請改用白話描述（例：「便條紙」→「待釐清的疑問」、「靜默」→不必說、「進入 2c」→「下一步準備預覽架構圖」）。

2. **專有名詞首次出現附白話註解**：技術術語允許使用，但首次出現須加括號白話說明。格式：`術語（＝白話解釋）`。例：`Common-Closure Principle（＝把會因為類似原因一起改的功能放一起）`、`Spec Package（＝一個會一起變動的功能分區）`、`Application-wise（＝以整個應用視角命名，不混入功能名稱）`。

3. **Pattern id / 技術縮寫允許直用 + 白話補充**：archetype pattern id（如 `spa-rest-3rd`、`web-service`、`browser-web-app`）可直接在 ASCII / 文字中使用，但首次出現時補一句白話（例：「`spa-rest-3rd`（＝前端 SPA + 後端 REST + 第三方服務）」）。

4. **狀態提示行例外保留**：每次回應結尾的狀態行 `> {SkillName}（Step N/M — <任務名>）— K 張便條紙待解決` 是 user-facing 進度條，允許保留 Step N/M 編號與「便條紙」一詞（已是 user 熟悉的進度語）。**僅此一處例外**。

5. **詢問 user 做決策時先講背景再給選項**：先用 1–2 句白話說明「我為什麼問你這題」「不選會發生什麼」，再列選項；不暴露 SOP 出處（如「依 §3.1 payload schema」「2b 子活動要求」）。選項本身可帶技術 id，但每選項配一句白話描述。

**判準**：把 SKILL.md / reason.md 的章節編號、子活動代號、機制術語當作**作者視角**的工程備忘，不當作可向 user 廣播的內容。User 只需要看到「現在在做什麼、下一步要他決定什麼、為什麼」。

---

## §scope 欄位（optional）

Planner 的 `assets/registry/entry.yml` 可選填 `scope`，標註「本 Planner 不 cover 的部分」：

```yaml
scope:
  in: ["command 定義", "query 定義"]
  out: ["DTO 實際 schema（交 form-api-spec）"]
```

- **optional**：多數 Planner 的職責已由 `core-decision` + `writes` 清楚刻畫，不必填
- 僅在存在易混淆之跨 Planner 邊界時填寫（如 service-contract vs form-api-spec）
- 填寫後 `relevance.md` 應呼應 `scope.out` 作為 irrelevant 範例
