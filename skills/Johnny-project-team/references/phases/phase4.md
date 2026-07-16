# Phase 4: 系統驗收與自動化腳本完善 (Final Acceptance & Release)

本階段發生在所有 Milestone 皆開發完畢後，是專案準備上線 (Release) 前的最後一關。

## 1. 全局系統整合測試 (System-Level Integration Check)
- **大腦清洗機制**：若該專案為中大型專案 (Milestone >= 5)，PM 必須 `kill` 掉原本的 DQA Agent，並重新 `invoke` 一名全新的 DQA Agent 來執行最終測試，以消除上下文盲點與疲勞。
- **簡易專案豁免 (Milestone < 5)**：若專案的 Milestone 總數小於 5，PM 必須在此刻詢問 CEO：「是否需要進行整機測試？」。若 CEO 回覆不強制要求，DQA 可直接給予綠燈通關，節省資源。
- **【反範圍潛變 (Anti-Scope Creep) 防線】**：在此階段，DQA 的退件權**僅限於「跨模組整合 Bug」與「重大業務邏輯錯誤」**。絕對禁止以「原 PRD 規格不夠完善」為由要求新增功能或改變設計。任何超出原定 PRD 範圍的非致命性發現，只能列為下一版本的優化項目 (Backlog)，不可阻擋當前版本的發布。

## 2. 測試套件收斂 (Test Suite Consolidation)
- 工程師與 DQA 必須將 Phase 3 產生的所有零碎測試腳本 (位於 `/SDD_DQA/tool/` 與 `/TDD_DQA/tool/`) 收斂至一個標準的自動化測試框架中 (如 pytest 或 Jest)。
- 建立統一的 `Makefile` 或 CI/CD 配置檔，確保未來只要輸入單一指令 (如 `make test-all`) 即可完成整機迴歸測試。

## 3. 架構師驗證與全員共識 (Architect Verification & Unanimous Consent)
- **架構師最後審查 (行動指南)**：在上線前，PM 必須強制喚醒 Architect 進行最後的架構覆核。Architect 被喚醒後必須執行以下盤點任務：
  1. **設計溯源 (Traceability)**：對照 Phase 0 產出的 ADRs 與系統流程圖，盤點最終 `src/` 目錄結構，檢查是否發生「未經授權的架構偏移 (Architectural Drift)」。
  2. **依賴與膨脹審查 (Dependency Audit)**：檢閱套件清單 (如 `package.json` 或 `requirements.txt`)，確認 Engineer 是否私自引入了非必要的第三方重型套件。
  3. **資料與資安防護 (Data Flow Check)**：抽查核心 API 與資料庫連線的實作，確認是否遵從 Phase 1 制定的 Schema 與安全邊界。
  4. **產出最終報告**：Architect 必須輸出帶有系統時間與 P0~P4 分級的 `Final_Architecture_Audit.md` 報告。
- **全員簽核防線**：PM、Engineer、DQA 與 Architect 四方必須達成「全票同意 (All-Agree)」。只要有一方 (特別是 Architect 或 DQA) 提出 P0/P1 級別的疑慮，立刻退回 Phase 3。

## 4. CEO 實機盲測 (Hands-On Intervention) & Phase Gate
- PM **強制暫停**所有 Agent 工作流程。
- PM 將編譯好的執行檔、APK 或網站連結發佈給 CEO，並請 CEO 進行實機操作。
- **【指令提醒義務】**：PM 在呈交測試版本給 CEO 時，必須主動且明確地提醒 CEO：「若您測試無誤，請輸入 `/approve` 來觸發上線流程」。
- 取得 CEO 的 `/approve` 指令後，PM 必須執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 4 --to_phase 5 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
- 只有當腳本回傳 `[GREEN LIGHT]`，才能進入最終發布與 Phase 5。

## 5. 安全發布程序 (Release & Tagging)
CEO 簽核後，PM 嚴禁親自在終端機輸入底層 Git 指令，必須透過專屬腳本完成發布：
- PM 呼叫 `scripts/release_manager.py`。
- 腳本將自動執行分支合併、語意化版本號 (Semantic Version) 遞增、`git tag` 標記與 `git push`。
- **發布完成跳轉**：一旦腳本成功執行完畢，PM 必須宣告專案正式發布，並帶領團隊進入 **Phase 5 (Post-Delivery & Maintenance)**，轉型為維護模式。

## 6. 退回處分與反思 (Rejection Handling)
若 CEO 在實機測試中發現致命錯誤並退回成品：
1. **呼叫 Log Agent 紀錄退件**：PM 必須在終端機執行 `python .agents/skills/Johnny-project-team/scripts/run_log_agent.py`，強制將「CEO 退件原因」與「Token/時間浪費點」紀錄到 `Logs/Master_Log.md` 中。
2. **DQA 檢討報告**：PM 必須強迫 DQA 針對漏掉該 Bug 的失誤，撰寫一份 `DQA_Reflection_Report.md`，並存入 `Logs/lesson_learnt_registry.md` 中。
3. **重返 Phase 3 與修改即重審 [CRITICAL]**：PM 立即更新 PRD 或 Test Plan，帶領團隊退回 Phase 3 重新修復。
   - **【鐵律】**：只要 Engineer 有碰到 `src/` 裡的任何程式碼，修復後必須**強制重跑滿 TDD、SDD 與 Claude DQA 的審查流程**，嚴禁直接跳回 Phase 4 給 CEO 複測！
