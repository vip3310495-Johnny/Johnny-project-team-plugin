# Engineer TDD：垂直切片 Red–Green–Refactor

本文件規範 Engineer 在一個已核准 Ticket 的內部開發方法。它補強、但不取代
Phase 3 的 TDD DQA → SDD DQA gate；DQA 不共同設計或修改產品實作。

## 每次只推進一個可觀察行為

先從一個 end-to-end tracer bullet 開始：用一個測試證明單一路徑真的可行，
再逐步擴展。禁止先批次寫完多個測試再批次實作；那會產生未經驗證的假設與脆弱的
「水平切片」測試。

每一輪只處理一個行為，完整紀錄於 Ticket 的 TDD cycle evidence：

1. **行為與介面**：以使用者或外部系統可觀察的語句命名，例如「有效購物車可以結帳」。
   測試只能經由公開介面或真實整合邊界，不得綁定私有函式、內部資料結構或呼叫次數。
2. **獨立 oracle**：預期值必須來自 Ticket、PRD、Contract Matrix、已驗證範例或常值。
   不得用與產品相同的演算法重算預期答案，避免 tautological test。
3. **RED**：先將永久自動測試寫入 `src/tests/`，執行並保留其明確失敗結果。RED 必須
   證明測試會抓到缺少或錯誤的行為。
4. **GREEN**：只在 `src/` 寫使當前一個測試通過所需的最小產品程式碼。不要趁此加入
   尚未由行為測試要求的抽象、功能或依賴。
5. **REFACTOR**：只有相關測試全綠時才重構。移除死碼與不必要依賴，改善可讀性和複雜度，
   並重新執行測試；不得在 RED 時重構。

接著才開始下一個行為。每次產品程式、active paths 或技術棧改變時，依 runtime contract
重新選擇並讀取 ECC rules。

## 最低品質要求

- 覆蓋主要行為、邊界條件、錯誤路徑、相容性與必要的回歸案例；永久檢查留在 `src/tests/`。
- 覆蓋率目標為 80% 以上，但不得以無意義或重複的測試湊數；TDD DQA 判定行為覆蓋與證據
  是否足夠。
- `try/except` 或 `catch` 必須記錄、轉譯或向呼叫端回傳可處理的失敗；空 catch block 不合格。
- 依 Ticket 風險加入副作用／冪等性、併發競爭、schema／fail-fast、時間與外部依賴隔離測試。
- 交接前執行 Ticket 指定的 test、coverage、lint、type-check、build 或 smoke 指令，並附上
  ECC selection hash 與可重現證據。

## Engineer 與 DQA 的邊界

Engineer 擁有測試設計與產品實作。TDD DQA 是獨立、必要的 post-build gate：驗證行為、
回歸、邊界、相容性與可重現證據，並可因缺口退件或要求補足可觀察的測試結果；不得預先
指定 Engineer 的內部測試結構、`Mock_Data.json` 或實作方式。TDD PASS 後才可進入 SDD DQA。

TDD DQA 的隔離工具與 evidence 僅能位於 `TDD_DQA/tool/` 與相關 DQA workspace，
不得進入產品 commit。
