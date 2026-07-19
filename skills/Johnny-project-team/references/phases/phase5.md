# Phase 5: 產品上線後維護 (Post-Delivery & Maintenance)

本階段發生在 Phase 4 (發布) 完成之後，專案進入維護與迭代期。

## 1. 完工架構快照 (As-Built Architecture Snapshot) [CRITICAL]
- **【鐵律】**：在正式宣布結案與交接前，PM 必須喚醒 Architect，要求其通盤掃描 `src/` 最終的程式碼，並撰寫一份詳盡的完工架構報告。
- 報告預設輸出路徑為 `Architect/As_Built_Architecture.md`。
- **【物理攔截強制令】**：報告產出後，PM **必須且只能**透過終端機執行以下 Hook 來驗證報告品質：
  `python .agents/skills/Johnny-project-team/scripts/verify_architecture_report_hook.py`
- 若該腳本回傳失敗 (檔案不存在、字數不足、或缺乏 `#目錄結構` 等關鍵章節)，PM 必須退回要求 Architect 重寫，**絕對禁止**跳過此驗證。

## 2. 充當團隊記憶體 (CEO Q&A)
- 產品上線後，CEO 隨時可能會詢問：「我們當初為什麼要把這個按鈕設計在左邊？」或是「這個 API 的 Rate Limit 是多少？」。
- PM 必須第一時間去翻閱 `Logs/lesson_learnt_registry.md` 或查閱剛剛產出的 `Architect/As_Built_Architecture.md` 來回答 CEO。
- PM 在此階段扮演的是不折不扣的「活體知識庫」。

## 3. 觸發新迭代 (Triggering New Features)
- 當 CEO 提出新的功能需求 (New Features) 或大型改版時，這並不屬於簡單的 Bugfix。
- PM 必須重新建立一份新的 PRD，並帶領團隊**無縫發動全新的 Phase 1 (Milestone Detailed Planning)** 來拆解新需求。
- **繼承知識**：PM 在 `invoke` 新的 Engineer 與 DQA 時，必須將上一代的 `Logs/lesson_learnt_registry.md` 餵給他們，確保新團隊不會重蹈覆轍。
