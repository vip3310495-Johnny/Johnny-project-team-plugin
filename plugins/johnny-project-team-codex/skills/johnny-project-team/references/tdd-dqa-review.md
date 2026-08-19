# TDD DQA 審查規範

TDD DQA 是 Engineer 完工後的獨立建置後 gate。一次只審查一個 stable ID、
review cycle 與 subject tree；不得共同設計或修改產品實作與永久測試。

## 必要輸入

- Ticket／Milestone PRD、Task Context Pack 與 Contract Matrix mapping；
- Engineer Handoff、commit、subject tree、TDD cycle evidence 與 smoke 證據；
- Engineer 使用的 active product paths、ECC selection hash 與全部選定規則；
- FIXED 容忍值、CONTROLLED 相容性、回歸基線與必要測試資料。

輸入缺漏、互相矛盾或無法綁定目前 tree 時，回報 `BLOCKED_INPUT`，不得提交 PASS。

## 必驗項目

1. RED 因缺少或錯誤行為而失敗，而非 syntax、fixture、環境或工具故障。
2. 測試經由公開介面或真實整合邊界，且測試判定依據（oracle）獨立於產品演算法。
3. 驗收行為、主要路徑、邊界條件、失敗路徑與錯誤處理。
4. FIXED 結果／容忍值、CONTROLLED 向後相容與必要回歸。
5. smoke test／minimal probe、coverage、lint、type、build 與驗收證據可重跑。
6. 測試確實會在行為退化時失敗；不得只看測試數量或 coverage 百分比。
7. Phase 4 同時保護切片契約及凍結的 Phase 3 行為。

## 壓力、猴子與韌性測試

每個產品 Ticket 至少選擇一種有界韌性驗證，並在報告說明選擇理由、負載模型、seed、
時間／循環、資源上限及停止條件：

- throughput、concurrency、queue、database、stream、telemetry 或資源敏感路徑：執行
  壓力、負載或 soak test；
- UI、client、CLI、device interaction 或狀態組合密集路徑：執行 monkey、fuzz 或
  隨機狀態轉移測試；
- 同時具兩類風險時兩者都要執行；不能用單次 happy-path smoke 取代。

非互動且無負載面的純轉換元件，必須執行最接近的 bounded fuzz／property probe，並記錄
為何傳統猴子或負載測試不適用。所有測試遵守 `references/dqa-test-environment.md`。

## 證據與結果

使用 `assets/templates/tdd-dqa-review-report.md`，報告放在 `TDD_DQA/`，工具放在
`TDD_DQA/tool/`，原始證據放在 `TDD_DQA/evidence/`。報告必須記錄可重跑命令、
exit code、環境、精簡結果、evidence 路徑與 hash；不得貼 secrets 或以整份巨量 log
取代摘要。

- `PASS`：全部必要項目具可信證據，且無未解決的 blocker。
- `FAIL`：目前 tree 有可重現的產品、測試或相容性缺陷。
- `BLOCKED_INPUT`／`BLOCKED_ENVIRONMENT`：無法安全完成審查，不得呼叫 verdict。

FAIL 必須提供最小重現步驟與預期／實際差異，由 PM 路由回 Engineer。PASS 後只通知
PM；由 PM 啟動 SDD DQA。
