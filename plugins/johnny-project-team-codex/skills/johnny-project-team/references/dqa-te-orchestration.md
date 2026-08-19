# DQA 與 TE 協作編排

## 權責歸屬

當前的 SDD DQA 或 TDD DQA 負責測試設計、任務邊界、證據審查及 PASS／FAIL 判定。
TE 只執行範圍明確的測試任務，不得再向下委派，也不得繞過其上層 DQA 回報。

## 容量規則

若目前工作階段有提供並行數上限，應採用該上限；否則使用專案預設值：最多四個
同時執行的 agent。

建立 TE 前：

1. 計入主 agent、DQA，以及所有目前執行中的 agent。
2. 計算 `free = session_limit - active_count`。
3. 計算 `spawn = min(requested, free, max_concurrent_per_dqa)`。
4. 將其餘任務排入 DQA 的工作計畫。

`max_concurrent_per_dqa` 預設為二。因此，只有一個 PM 與一個執行中 DQA 的工作階段
可同時執行兩個 TE 子 agent；若 Engineer 也正在執行，則只能執行一個 TE。單一 Ticket
的 TDD DQA 與 SDD DQA 必須依序執行，兩者的 TE 容量不得重疊。

使用 `te_dispatch_plan.py` 進行確定性的容量計算。該命令會確認 Johnny 狀態鎖可用、
立即釋放鎖，並輸出建立／排隊計畫。持有任何狀態鎖時，絕對不得建立 agent。

## 任務指派

每個 TE 都必須取得：

- 穩定的任務 ID；
- 一個獨立的測試面向；
- 明確的專案路徑與唯讀命令；
- 預期證據與停止條件；
- `assets/schemas/te-result.schema.json` 所定義的結果契約。

任務必須彼此獨立且可並行執行。不得讓兩個 TE 修改相同的 service、fixture、database
或外部環境。

## 結果彙整

等待所有執行中的 TE 子 agent 完成，驗證其命令、exit code 與證據。衝突或不完整的證據
必須記為 FAIL／BLOCKED；不得將判定取平均。只有 DQA 可以更新 DQA 報告或狀態。
