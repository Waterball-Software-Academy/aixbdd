## PRINCIPLE: 長流程待辦（兩層）

長流程會跨多輪對話；在 **conversation compact**（對話摘要壓縮）之後，執行者仍要靠**同一套待辦**還原：目前卡在哪個 **phase**，該 phase 內細項又到哪一格。底下為**兩層**約定：**外層只列 phase**，**進入該 phase** 再把該 sub-SOP 第一層編號步驟拆成子項。尚未開始的 phase 不必預先展開成檔案級細項，以免待辦與實際 `SOP.md` 脫節。

- **必須工具化**：Tier 0／Tier 1 對應的勾選項，**要以執行環境提供的任務／待辦建立與更新能力實體化**（例如 **`TODOCREATE`**、**`TASKCREATE`** 等 tool；或宿主 IDE／Agent 內與之等效的待辦 API），在跑 sub-SOP **當下**就建好清單並隨步驟推進更新狀態。**禁止**只靠聊天裡口頭列點、不經工具建立的「心裡待辦」——壓縮後無法還原，也無法核對漏步。
- **Tier 0（phase）**：對應本檔 `# SOP` 最外層每一項；每一項對應一個 sub-SOP 目錄（例：`01-sourcing-and-packaging/`）。這一層的勾選語意是「該 phase 的細項已全部展開**且**依 `SOP.md` 跑完」。
- **Tier 1（phase 內細項）**：僅在目前執行中的 phase 建立；對應該 phase `SOP.md` 裡**第一層編號步驟**拆解出的動作（`READ`／`WRITE`／`DERIVE` 等）。編號建議：`(phase序)`、`(phase序-子序)`（例：`1`、`1-1`），跨輪可對照；**進入該 phase 時**以 **`TODOCREATE`／`TASKCREATE`（或等效）** 補齊子項。

**Tier 0 範例**（語意範本；實務請用 **`TODOCREATE`／`TASKCREATE`（或等效）** 建立對應任務，結構對齊即可。`<NN-subsop>` 為占位符，以本檔 `# SOP` 實際路徑取代）：

```markdown
- [ ] (1) 展開並執行至完成：`01-<NN-subsop>/SOP.md`（細項見下）。
- [ ] (2) 展開並執行至完成：`02-<NN-subsop>/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-<NN-subsop>/SOP.md`。
```

**進入 (1) 後**才把 (1) 拆成 Tier 1；其餘 phase 在 Tier 0 維持單列：

```markdown
- [ ] (1) 展開並執行至完成：`01-<NN-subsop>/SOP.md`。
    - [ ] (1-1) READ：`01-<NN-subsop>/SOP.md` 步驟 0 …
    - [ ] (1-2) WRITE：`<該步授權產出路徑>`
    - [ ] (1-3) 依該 `SOP.md` 其餘編號步驟續跑 …
- [ ] (2) 展開並執行至完成：`02-<NN-subsop>/SOP.md`。
- [ ] (3) 展開並執行至完成：`03-<NN-subsop>/SOP.md`。
```

**(1)** 的子項全部完成後，以 **`TODOCREATE`／`TASKCREATE`（或等效）** 將 Tier 0 之 **(1)** 標為完成，再對 **(2)** 重複「展開 → 跑完」，依序往後。**未完成當前 phase** 前，**不要**為後續 phase 預開檔案層級的細項。
