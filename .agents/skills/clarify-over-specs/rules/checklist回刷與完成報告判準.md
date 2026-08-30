# Rule 1 - checklist 只更新實際狀態有變化的項目

- Level: `MUST`
- 若 `CHECKLIST_FILE` 存在，回刷時只允許切換實際狀態已改變的 checkbox；未變化的行、標題、順序、說明與空白應保留原樣，不做美容式改寫。
- 回刷時應先以更新後的 `spec.md` 重新判斷每個 checkbox 是否通過，再決定 `[ ]` / `[x]` 是否需要切換。
- 若某項在更新後仍不通過，應保留未勾選狀態，並在完成回報中說明它為何仍未通過。
- 若本輪沒有 checklist，應跳過檔案更新，但仍需在完成回報中明示「本輪無 checklist 可回刷」。

## Good Example

- 這個例子是好的，因為它只改動狀態真的變化的 checkbox。

```md
更新前：
- [ ] 仍保留的 `NEEDS CLARIFICATION` 已標示是否阻塞後續規劃

更新後：
- [x] 仍保留的 `NEEDS CLARIFICATION` 已標示是否阻塞後續規劃

其餘 checklist 內容不動
```

## Bad Example

- 這個例子是壞的，因為它把整份 checklist 重寫成新版 wording，造成大量無關 diff。

```md
處理：
- 順手重排 checklist 順序
- 調整所有條目 wording
- 同時切換少數 checkbox 狀態
```

# Rule 2 - ready 判定必須同時看 checklist 與剩餘高影響缺口

- Level: `MUST`
- 判斷是否已可進 `/plan` 時，不可只看 spec 已被更新，也不可只看部分 checklist 勾選情況；必須同時評估：
  - 是否仍有未解的高影響需求缺口
  - 這些缺口是否會改變正式驗收、資料邊界、NFR 承諾或規劃方向
  - checklist 中是否仍有與上述高影響缺口對應的未通過項
- 若仍存在會改變後續規劃方向的高影響缺口，應判為尚未 ready，即使 spec 其他部分已大致完整。
- 若剩餘未通過項只屬低風險 deferred 細節，且不會推翻後續規劃，可以在完成回報中明示風險後仍判定可進 `/plan`。

## Good Example

- 這個例子是好的，因為它沒有把「有更新」誤當成「已 ready」。

```md
觀察：
- 已補上先手規則與延遲門檻
- 但斷線處置仍未定，且會影響遊戲狀態轉換與驗收

判定：
- 尚未 ready
- 建議再跑一次 `/clarify-over-specs`
```

## Bad Example

- 這個例子是壞的，因為它忽略剩餘高影響缺口，過早宣告完成。

```md
觀察：
- spec 已有若干更新
- checklist 也多勾了兩項

判定：
- 直接進 `/plan`
```

# Rule 3 - 完成回報必須完整交代本輪澄清效果與殘餘風險

- Level: `MUST`
- 完成回報至少必須交代：
  - 目標 `SPEC_FILE` 與 `CHECKLIST_FILE`（或其缺席狀態）
  - 本輪是否進入 `/clarify`，以及實際處理了幾個高影響缺口
  - 哪些 section 被更新
  - checklist before / after 狀態，或無 checklist 可回刷
  - 哪些高影響缺口已解決、哪些仍 deferred 或 outstanding
  - 是否已 ready，以及建議下一步應進 `/plan` 或稍後再跑 `/clarify-over-specs`
- 完成回報的重點是讓使用者與後續 skill 都能知道：這輪到底清掉了哪些風險，還剩什麼不能假裝沒看到。
- 若本輪沒有進 `/clarify`，也要說明原因，例如所有高影響缺口皆已清楚，或僅剩低風險 deferred 細節。

## Good Example

- 這個例子是好的，因為它回報了處理結果，也回報了剩餘風險與下一步。

```md
完成回報：
- 目標 spec：`specs/001-online-pvp-1a2b/spec.md`
- 進入 `/clarify`：是，2 題
- 更新 section：使用者故事 3、邊界情況、成功標準
- checklist：12/16 -> 14/16
- deferred：斷線恢復策略
- ready：否
- 建議下一步：再跑一次 `/clarify-over-specs`
```

## Bad Example

- 這個例子是壞的，因為它只說「已更新完成」，沒有讓人知道成果與殘留問題。

```md
完成回報：
- spec 已更新
- 請繼續下一步
```

# Rule 4 - checklist 缺席或 deferred 缺口都不可被隱藏

- Level: `SHOULD`
- 若 `CHECKLIST_FILE` 不存在，完成回報中應明示本輪未回刷 checklist，而不是讓使用者誤以為已完成完整驗證。
- 若高影響缺口被刻意 defer，完成回報中應說明 defer 理由與其對後續 `/plan` 的影響，不可只寫成泛泛的「還有一些問題待確認」。
- 若本輪完全不需提問，也應在完成回報中說明是因為高影響缺口皆已 `Clear`，而不是省略掉澄清策略判斷。

## Good Example

- 這個例子是好的，因為它把缺席與 defer 狀態都外顯。

```md
回報：
- checklist：本輪無對應檔案，因此未回刷
- deferred：第三方通知通道是否納入第一版，影響低，保留到 `/plan`
```

## Bad Example

- 這個例子是壞的，因為它用模糊說法掩蓋驗證缺口。

```md
回報：
- 大致都好了
- 還有一些地方之後再說
```
