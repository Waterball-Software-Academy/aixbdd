# SOP

確認從紅到現在 runtime 環境沒有飄移。DSL／preset／可見性的對應信任 `red_handoff` 帶來的結果，不重算。

1. 算出「現在的」runtime 來源指紋：對 `${ACCEPTANCE_RUNNER_RUNTIME_REF}`、`${STEP_DEFINITIONS_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`、`${FEATURE_ARCHIVE_RUNTIME_REF}` 各算出路徑與內容指紋。
2. 把這份指紋，逐項比對 `red_handoff.runtime_refs_snapshot` 中對這組 target 的對應項。
3. 確認每一項都一致；一旦任一項飄移，就停下來，把可路由的飄移原因記成 `stop_reason: runtime_drift`（runtime 飄移該回去檢查專案 BDD stack 設定，不是 green 該修的）。
