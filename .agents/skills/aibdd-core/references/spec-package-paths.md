# Spec Package Paths

AIBDD skills 的 specs 目錄樹 SSOT。

1. 每個 `specs/` root，都是為單一一個 Boundary 存放其相關計劃及產品規格的 root。
2. 每一次 plan 的迭代始於一次 `/aibdd-discovery` 執行。

## 目錄樹

```text
specs/
├── architecture/
│   ├── boundary.yml              # boundary 身分與 type 宣告
│   └── component-diagram.class.mmd  # boundary 元件邊界與依賴
├── boundary-map.yml              # 跨 boundary / sub-boundary 對照
├── test-strategy.yml             # boundary 測試分層與覆蓋策略
├── contracts/                    # operation contract truth（boundary-level）
│   └── *.dsl.yml                 # operation part 對應的 handler DSL 語料
├── data/                         # state truth（boundary-level）
│   └── *.dsl.yml                 # state part 對應的 handler DSL 語料
├── shared/
│   └── dsl.yml                   # boundary 共用 step / handler 詞彙
├── packages/
│   └── NN-<functional-module>/   # 單一功能模組的 accepted behavior 規格包
│       ├── features/             # SBE `.feature` 規格
│       ├── activities/           # Activity 流程模型（`.activity`）
│       └── test-plan/            # feature 測試計畫與覆蓋對照
└── plans/
    └── NNN-<plan-slug>/          # 單次 plan 迭代的規劃與實作藍圖包
        ├── spec.md               # 本次 plan 的需求與範圍摘要
        ├── plan.md               # 實作計畫（topology、delegation、gate）
        ├── clarify/              # plan 期澄清問答紀錄
        ├── reports/              # plan 分析產出
        │   ├── impact-matrix.yml # feature / contract / entity 影響矩陣
        │   └── coverage/         # plan 覆蓋度報告
        └── implementation/       # 實作期藍圖產物
            ├── sequences/        # 關鍵互動 sequence diagram
            └── internal-structure.class.mmd  # plan 範圍內部類別結構
```
