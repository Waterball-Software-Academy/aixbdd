# Given Delta: 前置（狀態） — web-service

1. 本檔是 web-service boundary 中 `前置（狀態）` 的 `Given Delta`。
2. arrangement engine、shared forces、shared optimization 與 shared legality 一律 follow `shared-given-law.md`。
3. 本檔只補 `前置（狀態）` 專屬的 arrangement 差異、legality 加嚴與 optimization tie-break。

## Arrangement Delta
1. `Given` 的目標是建出一個不滿足被測前置條件的違規狀態，而不是合法背景。
2. failure source 必須收斂在被測前置條件本身；不得讓其他 entity invariant 壞掉來製造失敗。
3. 若被測條件是 lifecycle phase / journey stage，優先用「停在上一個自然階段」表達違規，而不是直接 snapshot 一個看似合法但語意模糊的 phase 值。
4. 若 violation 需要局部 state spotlight，可在 shared Decision Tree 選出的 strategy 上，再補最後一段 focused snapshot；但 replay 部分仍應保留 journey semantics。

## Optimization Delta
1. Optimization 追加 tie-break：`failure-source isolation` 優先於 `minimum cardinality`——若某 plan 更能清楚隔離「只有前置狀態是非法的」，優先選它。
