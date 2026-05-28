# Given Delta: 後置（回應） — web-service

1. 本檔是 web-service boundary 中 `後置（回應）` 的 `Given Delta`。
2. arrangement engine、shared forces、shared optimization 與 shared legality 一律 follow `shared-given-law.md`。
3. 本檔只補 `後置（回應）` 專屬的 arrangement 差異與 optimization tie-break。

## Arrangement Delta
1. `Given` 的目標是建出操作成功所需的最小前置狀態。
2. 只保留與回應欄位可判定性直接相關的背景；無關 state 不應混入。
3. 若回應值依賴既有資料、時間或 external stub，該依賴必須在 `Given` 中可追溯。

## Optimization Delta
1. Optimization 追加 tie-break：優先選最少背景、最少無關 aggregate 的 plan。
