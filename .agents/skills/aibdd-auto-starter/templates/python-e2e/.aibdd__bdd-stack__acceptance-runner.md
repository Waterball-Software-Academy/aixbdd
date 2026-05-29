# Acceptance Runner Runtime

## acceptance runner command

```bash
behave tests/features
```

## dry-run / discovery command

```bash
behave --dry-run tests/features
```

## runner config file path

`behave.ini`

## runtime feature glob

`tests/features/**/*.feature`

## step definition glob

`tests/features/steps/**/*.py`

## shared step glob（若有）

`tests/features/steps/shared/**/*.py`

## report output path（若有）

無。預設 starter 不輸出 JUnit XML、plain log、HTML report；若專案啟用報告，請在本檔明確補上實際路徑。

## runner visibility check 方法

1. 確認 `behave.ini` 的 `paths` 指向 `tests/features`。
2. 若 step definitions 允許落在巢狀 package 目錄下，確認 runner config 已開啟對應 discoverability 設定。
3. 執行 `behave --dry-run tests/features`。
4. 若 dry-run 無法載入 feature 或 step definitions，先修 runner wiring，不進入紅燈。

## stack-specific caveat / known limitations

- `behave --dry-run` 不會執行 `environment.py` 的完整 runtime side effects。
- Testcontainers 需要 Docker 可用；真正 acceptance runner command 可能因 Docker 未啟動而失敗。
- 中文 feature 檔名依賴本機檔案系統與 Behave/Python encoding 支援。
