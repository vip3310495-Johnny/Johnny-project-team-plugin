# Phase 4: 成品驗收階段 (Final Acceptance & Release)

當所有的 Milestones 都順利跑完 Phase 3 後，系統將進入 Phase 4。
此階段的重點是「全局檢視與初衷對齊」，確保開發結果與一開始的戰略目標沒有偏離。

## 1. SDD DQA 初衷覆核 (Intent Verification)
- PM 必須強制喚醒 SDD DQA，並交付 Phase 1 的「總體 PRD」。
- **核心任務**：SDD DQA 必須根據 Phase 1 PRD 內寫的「**開發目的 (Intent)**」與「**Non-goals (非目標)**」進行最終的全盤覆核。
- 若發現開發出的成品雖然符合細部規格，但卻偏離了原始的商業初衷，或是不小心實作了 Non-goals，SDD DQA 必須亮紅燈退件。

## 2. TDD DQA 整合與回歸測試
- SDD DQA PASS 後，TDD DQA 必須執行全局整合、回歸與關鍵邊界測試。
- 兩位 DQA 必須各自透過下列狀態命令回報 PASS；未回報或 FAIL 都會阻擋 Phase 5：
  `python dqa_status_manager.py --project_dir . --status_file .agents/.phase4_dqa_status.json --role <SDD|TDD> --status PASS`

## 3. Claude DQA 最終獨立審查
- SDD 與 TDD 均為 PASS 後，Phase 4 最終閘門會自動呼叫 Claude CLI 進行唯讀獨立審查。
- Claude 只在真實回覆 PASS 時才會記錄 PASS；其 JSON 報告寫入 `Claude DQA/`，失敗、逾時或 CLI 錯誤均維持鎖定。
- 在交給 CEO UAT 前，PM 必須執行：
  `python phase4_final_gate.py --project_dir .`

## 4. 實機盲測與自動上線
- SDD、TDD、Claude 三者亮綠燈後，PM 將最終的執行檔、網站連結或文件統整，呈交給 CEO。
- CEO 進行**「實機盲測 (Dogfooding / UAT)」**。
- 若 CEO 發現致命問題，則退回 Phase 3 重新修補。
- 若 CEO 盲測滿意，輸入 `/approve`。
- PM 取得 CEO 簽核後，必須強制執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 4 --to_phase 5 --ceo_signature "/approve"`
- 腳本會再次驗證 Phase 4 三重 DQA 狀態；若前一步尚未執行 Claude DQA，會作為安全備援自動執行。回傳 `[GREEN LIGHT]` 後，PM 才能呼叫 `release_manager.py` 處理 Git Merge、Tagging 與 Push 上線。
- 上線完成後，正式宣告進入 **Phase 5 (產品上線後維護)**。
