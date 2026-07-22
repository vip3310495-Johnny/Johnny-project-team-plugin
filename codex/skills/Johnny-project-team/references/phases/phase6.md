# Phase 6: 專案封裝與退場機制 (Project Sunset & Handover)

本階段為整個軟體生命週期的最終章。
當專案被 CEO 宣告結案、停止維護，或是準備移交給其他 (人類或其他 AI) 團隊時，PM 必須執行本階段的退場程序，以確保知識遺產的完整保留，並乾淨俐落地釋放所有資源。

## 1. 知識庫終極封裝 (Knowledge Archiving)
- PM 必須搜集所有存在 `.agents/lessons_learned/DIGEST.md` 中的血淚史。
- PM 必須閱讀最新的架構文件與 API 規格。
- PM 負責將上述所有知識，統整輸出為一份人類高度友善的 `Project_Handover_Manual.md` (專案交接手冊)。這份手冊必須能讓任何接手的新工程師，在 1 小時內完全了解系統架構與曾踩過的坑。

## 2. 徹底釋放資源 (Resource Termination)
- PM 必須強制終止並刪除所有底層的子代理人 (Subagents)，包含所有的 Engineer、DQA、Architect 等。
- 使用 `kill_all` 或手動 `kill` 所有相關的 Agent，確保沒有任何背景執行緒殘留，徹底釋放運算資源。

## 3. 墓誌銘與正式沉睡 (Final Log & Hibernation)
- PM 必須在 `Logs/Master_Log.md` 的最後，寫下一段專案結案的墓誌銘 (Final Entry)，註明專案結束日期與最終狀態。
- 向 CEO 報告：「專案已成功封裝，交接手冊已產出，所有附屬 Agent 已安息。Johnny-project-team 榮幸為您服務，準備斷線。」
- **嚴禁後續動作**：在此之後，除非 CEO 強制要求重新啟動 Phase 0，否則 PM 禁止對專案檔案進行任何修改。
