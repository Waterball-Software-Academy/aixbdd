# Phase {{phase_number}} - {{feature_label}}

## RED
- [ ] 透過 `/aibdd-red-execute` 來撰寫 `{{feature_path}}` 的測試程式碼。
- [ ] Looping 啟動一個獨立 Subagent，請他進行 `/aibdd-red-evaluate`。
  - [ ] 輸入此次 feature 的 red evidence artifact paths。
  - [ ] 若 evaluator 判定不合法，持續修正，然後重新啟動全新 evaluator subagent。
  - [ ] 直到 evaluator 判定此 feature 的 red 合法為止。

## GREEN
- [ ] 透過 `/aibdd-green-execute` 讓 `{{feature_path}}` 轉綠。
- [ ] 實作時必須參考 `{{implementation_dir}}` 底下的設計與本 phase 的 implementation waves。
{{green_wave_block}}
- [ ] 進行回歸測試，確定所有測試都通過了，確認產出測試報告。
- [ ] Looping 啟動一個獨立 Subagent，請他進行 `/aibdd-green-evaluate`。
  - [ ] 輸入此次 feature 對應的 green / full-suite report artifact paths。
  - [ ] 若 evaluator 判定不合格，持續修正，然後重新啟動全新 evaluator subagent。
  - [ ] 直到 evaluator 判定 green 合法為止。

## Refactor
- [ ] 進行 `/aibdd-refactor-execute`。
- [ ] Looping 啟動一個獨立 Subagent，請他進行 `/aibdd-refactor-evaluate`。
  - [ ] 輸入此次 feature 對應的 refactor / full-suite evidence artifact paths。
  - [ ] 若 evaluator 判定不合格，持續修正，然後重新啟動全新 evaluator subagent。
  - [ ] 直到 evaluator 判定 refactor 合法為止。

<!-- INSTRUCT:
- `phase_number`, `feature_label`, `feature_path`, and `implementation_dir` must come from deterministic scaffold data.
- `green_wave_block` is the only major semantic fill slot inside this template.
- `green_wave_block` must obey `references/implementation-task-wording-contract.md`.
- This template owns all fixed RED / GREEN / Refactor wording and evaluator retry loop wording.
-->
