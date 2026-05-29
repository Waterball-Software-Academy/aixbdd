# Given Delta: 後置（狀態） — web-service

1. 本檔是 web-service boundary 中 `後置（狀態）` 的 `Given Delta`。
2. arrangement engine、shared forces、shared optimization 與 shared legality 一律 follow `shared-given-law.md`。
3. 本檔只補 `後置（狀態）` 專屬的 arrangement 差異、legality 加嚴與 optimization tie-break。

## Arrangement Delta
1. `Given` 的目標是建出一個可量測的 before-state，讓 `Then` 能清楚觀察 expected delta。
2. 若 rule 需要觀察 `資料`、`外發`、`資源`、`行為` 其中一類狀態變化，`Given` 必須讓該子類的 before-state 可被明確對照。

## Legality Delta
1. Legality Gate 追加 veto：拒絕無法提供明確 before-state baseline 的 `Given`。

## Optimization Delta
1. Optimization 追加 tie-break：優先選最小 state scope、最短 state path、最少額外推論的 arrangement。
