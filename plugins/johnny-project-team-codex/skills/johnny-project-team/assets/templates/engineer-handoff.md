# <Wave>_<Milestone>_Engineer Hand off — Review Cycle <N>

> 填寫規則：每一節都必須保留。沒有內容時明填 `None` 並說明原因，不得留白或刪節。
> 不貼入 secrets 或整份巨量 log；記錄可重跑命令、精簡結果、evidence 路徑與必要 hash。
> 完成範例見 `assets/examples/engineer-handoff-example.md`。

## 識別資料

- Ticket／Milestone：
- Wave：
- Review cycle：
- Branch：
- Commit：
- Subject tree：
- Context Pack 版本／路徑：

## 完成範圍

- 本次完成的 observable outcomes：
- 明確未處理的 non-goals：
- CONTROLLED Change Notice（如有）：

## 修改明細

| 路徑／元件 | 原問題或先前行為 | 修改內容 | 修改理由／對應需求 | 相容性與風險 |
|---|---|---|---|---|
|  |  |  |  |  |

## 規則與 TDD 證據

- ECC selection hash：
- 已讀取的 ECC rules：
- TDD cycle evidence 路徑：
- 永久測試路徑：
- 預期 RED 摘要與 evidence（不得列入下方非預期失敗）：

## 已執行測試

| 類型／範圍 | 驗證目的 | 可重跑命令 | 結果 | Evidence |
|---|---|---|---|---|
| Unit／Integration／E2E |  |  |  |  |
| Coverage |  |  |  |  |
| Lint |  |  |  |  |
| Type-check |  |  |  |  |
| Build／Acceptance |  |  |  |  |

## Smoke test 閘門

- 交付類型：UI / Service / CLI / Library / Migration / 其他
- Smoke／最接近 probe 的關鍵路徑：
- 測試環境與必要前置條件：
- 可重跑命令／操作步驟：
- 預期結果：
- 實際結果：
- Evidence：
- Verdict：PASS / BLOCKED

> UI、service 或 CLI 必須驗證至少一條關鍵成功路徑。Library、migration 或無獨立
> 入口的交付必須執行 import、load 或 minimal acceptance probe，不得直接填 N/A。
> `BLOCKED` 時 Engineer 結論也必須是 `BLOCKED`，PM 不得送 DQA。

## 使用工具與依賴

| 工具／版本或來源 | 用途 | 實際用法／命令 | 產出或副作用 |
|---|---|---|---|
|  |  |  |  |

- 新增／移除／升級的依賴與理由：

## 非預期失敗紀錄

> 記錄 build、test、工具、環境與流程中的非預期失敗；已解決者也不得刪除。若完全沒有，
> 填一列 `None`。預期的 TDD RED 只屬於 TDD cycle evidence。

| 階段 | 命令／動作 | 觀察到的失敗 | 根因 | 處理方式 | 最終狀態／Evidence |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 流程觀察

| 規則／context／工具問題 | 對流程的影響 | 暫時處理 | 建議改善 |
|---|---|---|---|
|  |  |  |  |

## 交付注意事項

- 已知限制與剩餘風險：
- 建議 TDD DQA 優先檢查項目：
- Rollback 方法：

## PM 接件

- Engineer 結論：READY_FOR_PM / BLOCKED
- Blocker（若有）：
- 本報告路徑：
