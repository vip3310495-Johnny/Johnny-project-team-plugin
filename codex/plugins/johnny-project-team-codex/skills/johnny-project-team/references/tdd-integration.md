# TDD 整合規範 (TDD Integration & Red-Green-Refactor)

本專案強烈要求工程師遵守 TDD (Test-Driven Development) 開發模式。
所有開發任務必須遵循以下循環：

## 1. RED (撰寫失敗的測試)
- Engineer 必須先根據 DQA 規劃的 `Mock_Data.json` 與測試計畫，撰寫自動化測試腳本。
- 此階段的測試執行結果必須是**失敗 (RED)**，藉此驗證測試案例本身具備捕捉 Bug 的能力。

## 2. GREEN (實作最低限度功能)
- Engineer 實作最少量的產品代碼，唯一目標是讓剛剛寫的測試腳本順利通過。
- 禁止在此階段進行過度設計 (Over-engineering)。

## 3. REFACTOR (重構與收斂)
- 當測試通過後 (GREEN)，Engineer 必須回頭檢視代碼。
- 發動 Code Simplifier 消除死代碼 (Dead Code)、移除不必要的相依性。
- 確保時間與空間複雜度達到最佳狀態。

## 4. DQA 80% 覆蓋率大關
- Engineer 完成開發後，必須確保本地端測試覆蓋率達到 80% 以上。
- 若覆蓋率未達 80%，TDD DQA 將會在 Phase 3 的第一關直接亮紅燈退件。
- PM **不具備**覆蓋率特批權限，此為系統硬性規範。

## 5. Silent Failure 獵殺
- TDD 必須特別針對「靜默錯誤」進行防護。
- 凡是使用 `try...except` 或 `catch` 捕捉異常時，必須明確記錄日誌 (Logging) 或向外拋出對應的錯誤狀態碼。
- 空的 catch block 將直接被視為不合格代碼。

## 6. 高階防禦體系 (Advanced TDD Guidelines) [CRITICAL]
除了基礎的覆蓋率與靜默錯誤獵殺外，TDD DQA 必須將以下四大高階測試方向納入考量：
1. **狀態機與副作用驗證 (State & Side-Effect Validation)**：
   - 包含「冪等性測試 (Idempotency)」(連續呼叫多次不改變預期狀態)。
   - 確保函數執行後不會污染全域變數或引發未預期的資料庫突變。
2. **併發與競爭危害 (Concurrency & Race Condition)**：
   - 針對多線程/多行程同時存取同一個資源 (如寫入同一個檔案或資料庫 Row) 進行非同步搶奪測試。
   - 驗證互斥鎖 (Mutex) 或資料庫 Transaction 的有效性。
3. **快速失敗與合約 (Fail-Fast & Contract)**：
   - 嚴格比對回傳的 JSON 或資料結構是否 100% 吻合 Architect 定義的 Schema。
   - 前置防禦測試：輸入缺漏欄位的惡意資料，驗證系統是否能在「第一行」立刻拋出清晰錯誤，而非引發後續的連鎖崩潰 (Fail-Slow)。
4. **時序與外部依賴 (Time & Dependency Mocking)**：
   - 時間旅行 (Time Travel) 測試：凍結或快進時間以驗證逾期邏輯。
   - 外部斷線隔離：強制切斷對外部 API 或資料庫的連線，驗證重試機制 (Retry) 與斷路器 (Circuit Breaker) 是否生效。

## 7. TDD DQA 最高裁量權 (Strict Discretion)
- TDD DQA 擁有對於上述「高階防禦體系」的**最高裁量權**。
- TDD DQA 必須以最嚴苛的標準審視當前專案，自行決定是否需要啟用併發測試、冪等性測試等高階防線。
- 一旦 DQA 判定需要，工程師**不得拒絕**，必須照單全收實作對應的自動化測試腳本。
