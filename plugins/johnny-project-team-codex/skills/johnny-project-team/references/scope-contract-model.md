# 範圍契約模型

使用三種約束層級，讓需求保留原始意圖，又不會指定不必要的實作細節。

## FIXED

適用於產品意圖、非目標、核心使用者流程、可觀察結果、容忍值、安全邊界，以及會破壞
外部契約的變更。

每個 FIXED 項目必須說明：

1. 意圖（Intent）
2. 可觀察結果（Observable outcome）
3. 容忍值（Tolerance）
4. 非目標（Non-goals）
5. 升級處理觸發條件（Escalation trigger）

除非某項機制本身就是必要需求，否則不得指定 function name、class layout 或逐步實作方式。

若 Phase 3 發現 FIXED 問題，Engineer 必須停止受影響的功能與相依鏈、立即通知 PM，且只能
繼續無關工作。由 PM 決定是否及如何變更契約。

## CONTROLLED

適用於 FIXED 範圍內保持向後相容的 API、schema、data flow、configuration 與 error handling
變更。

Engineer 可在未經核准的情況下進行變更，但必須向 PM 提交 Change Notice。PM 將其附加至
Phase 3 ledger；DQA 與 Architect 不負責核准該通知。Phase 3 與 Phase 4 的逐 Ticket DQA
會客觀測試向後相容性。

## DISCRETIONARY

適用於不改變 FIXED 結果或相容性的內部實作、命名、重構、測試技術及次要呈現細節。

Engineer 可自行選擇，只記錄理解或維護完成系統所需的細節。

## 分類權責

Phase 3 前只有 PM 能指定初始層級。任何 agent 均可提出一次有證據支持的分類異議，最終
由 PM 決定。

## 缺陷指標

下列情況計為 `Contract Violation`：

- 未經核准而偏離 FIXED；
- CONTROLLED 變更未通過相容性測試；
- 未達可觀察結果或容忍值。

下列情況另計為 `Process/Documentation Defect`：

- 缺少 Engineer Change Notice；
- 缺少 PM ledger 紀錄；
- As-Built 文件與系統不一致。

不得將有效的 DISCRETIONARY 選擇計為契約違規。

## 與逐 Ticket DQA 的關係

三種範圍層級在 Phase 3 與 Phase 4 全程有效。它們控制變更權限，DQA 順序則控制驗證：

- `FIXED`：Engineer 必須立即升級處理問題。TDD 驗證行為與容忍值；SDD 驗證意圖及契約一致性。
- `CONTROLLED`：Engineer 可進行向後相容的變更，但必須通知 PM。TDD 驗證相容性；SDD
  驗證變更仍在 FIXED 範圍內。DQA 不負責核准 Change Notice。
- `DISCRETIONARY`：Engineer 自行選擇內部實作。DQA 可以測試其影響，但不得只因偏好另一種
  同樣有效的方法而判定失敗。
