# Given Delta: 前置（參數） — web-service

1. 本檔是 web-service boundary 中 `前置（參數）` 的 `Given Delta`。
2. arrangement engine、shared forces、shared optimization 與 shared legality 一律 follow `shared-given-law.md`。
3. 本檔只補 `前置（參數）` 專屬的 arrangement 差異、legality 加嚴與 optimization tie-break。

## Arrangement Delta
1. `Given` 的目標是建出一個最小且合法的背景，使主操作可以被正常呼叫。
2. failure source 必須收斂在 `When` 帶入的無效參數，不得提前藏進 state。
3. 若 rule 採 `Scenario Outline`，無效值應集中在 `Examples` / `When`，不要回滲進 `Given`。

## Legality Delta
1. `Given` 不得偷跑當前 `When` 正在受測的主操作。
2. `Given` 不得把本 rule 的無效參數值提前塞回前置建構。
3. `operation-invoke` 不得提前帶入本 rule 的無效參數值。
4. 任一 plan 若雖可跑通，但會讓「失敗只來自無效參數」這件事被埋沒，視為不合法。
5. Background reuse 追加限制：與某一個 invalid value、某一個 failure side、或某一個 special branch 綁死的 state，不可提升成 `Background`。

## Optimization Delta
1. Optimization 追加 tie-break：`failure-source isolation` 優先——若某 plan 更能清楚隔離「只有參數是非法的」，優先選它。
