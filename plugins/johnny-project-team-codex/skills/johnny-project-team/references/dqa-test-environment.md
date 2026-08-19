# DQA 測試環境與實際硬體安全規範

TDD／SDD DQA 只能在非正式環境、可重建、可清理且不會對真實使用者造成
不可逆副作用的環境執行驗證。Codex 的 `workspace-write` sandbox 只是檔案權限邊界，
不能取代測試環境隔離。

## 一般環境

- 禁止使用正式環境 credentials、正式 database、真實客戶資料，或會產生不可逆寫入的
  正式外部 endpoint。
- 優先使用暫存 database、sandbox account、record/replay、stub 或供應商測試環境。
- 報告記錄 OS／runtime、build、設定、測試資料版本、外部依賴與清理結果；不得記錄 secret。
- 壓力、猴子、fuzz、soak 或 chaos 測試必須設定時間、速率、資源及停止上限；禁止
  無界執行或把正式服務當作負載目標。
- 若環境無法安全隔離、重建或清理，回報 `BLOCKED_ENVIRONMENT`，不得提交 PASS verdict。

## 實際硬體

允許使用實際硬體，但必須是專用測試機、實驗室設備，或已進入核准維護時段且與正式
使用者隔離的設備。開始前記錄：

1. 裝置識別、硬體／韌體版本與連線拓撲；
2. 測試帳號、合成資料及非正式環境 backend；
3. 電壓、溫度、速度、循環次數、負載等安全範圍（envelope）；
4. 緊急停止機制、operator、觀察方式與停止條件；
5. 可復原的 setup／teardown，以及測試前後的狀態證據。

猴子或壓力測試不得突破製造商安全限制、損耗預算或法規限制。若設備正在正式運轉、
與真實使用者共享、只能連正式環境，或測試可能造成人身、設備、資料或外部系統的
不可逆影響，回報 `BLOCKED_ENVIRONMENT`，不得以實際硬體為由降低標準。

`BLOCKED_ENVIRONMENT` 是報告狀態，不是 PASS／FAIL verdict；在解除前不得呼叫
`johnny_dqa_record.py verdict`。
