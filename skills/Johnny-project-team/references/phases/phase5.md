# Phase 5: 產品上線後維護 (Post-Delivery & Maintenance)

本階段發生在 Phase 4 (發布) 完成之後，專案進入維護與迭代期。

## 1. 充當團隊記憶體 (CEO Q&A)
- 產品上線後，CEO 隨時可能會詢問：「我們當初為什麼要把這個按鈕設計在左邊？」或是「這個 API 的 Rate Limit 是多少？」。
- PM 必須第一時間去翻閱 `Logs/lesson_learnt_registry.md` 或查閱程式碼，透過過去留下的「對話留痕」與「架構紀錄」來回答 CEO。
- PM 在此階段扮演的是不折不扣的「活體知識庫」。

## 2. 觸發新迭代 (Triggering New Features)
- 當 CEO 提出新的功能需求 (New Features) 或大型改版時，這並不屬於簡單的 Bugfix。
- PM 必須重新建立一份新的 PRD，並帶領團隊**無縫發動全新的 Phase 1 (Milestone Detailed Planning)** 來拆解新需求。
- **繼承知識**：PM 在 `invoke` 新的 Engineer 與 DQA 時，必須將上一代的 `Logs/lesson_learnt_registry.md` 餵給他們，確保新團隊不會重蹈覆轍。
