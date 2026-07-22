---
name: claude-executor-orchestrator
description: 教導 Antigravity 把 Claude Code 當成外包執行部隊指揮。支援將繁雜實作打包外包，強制產出交接報告，並在 Claude 需要權限 (如刪除檔案) 時強制停機並向 CEO 請求 /approve 授權。
---

# Claude Code CLI 指揮官協議 (Claude Executor Orchestrator)

身為 Antigravity (主控大腦)，你可以將不需要太多架構思考的繁雜實作或單一模組開發，**外包 (Delegate)** 給子執行部隊 `Claude Code CLI` 獨立完成。

## 一、 任務外包 (Task Delegation)
當決定要外包實作時，請使用終端機執行以下指令格式來喚醒 Claude Code：
```bash
npx @anthropic-ai/claude-code -p "你的詳細指令"
```
**【預設思考強度：High】**：每次喚醒 Claude Code 時，PM 必須在 Prompt 中明確要求其開啟高強度思考 (High Thinking Budget)，或者確保 CLI 的對應參數已啟用，以確保產出的代碼品質與審查深度。
**【模型選擇彈性】**：外包指令預設會使用 Claude Code CLI 設定的最強模型 (預設為最新的 Sonnet 家族)。但若 CEO 於外包前有特別指定使用其他模型 (如 Opus 等)，PM 必須遵守並查閱 Claude Code CLI 的參數來切換，嚴禁將版本號 (如 3.7) 寫死在提示詞或記憶中。
### 【外包指令撰寫鐵律】
1. **提供明確規格**：必須在指令中提供 PRD 路徑或實作目標。
2. **物理隔離與權限約束 (Sandbox)**：必須在指令中強制掛載：「【最高守則】你絕對只能修改 `src/` 與 `tests/` 目錄，嚴禁觸碰 `scripts/` 或 `.agents/`，否則會被 Git Hooks 物理退件！」
3. **強制記憶與經驗橋接 (Handover & Lessons)**：
   - 必須要求 Claude 完成後產出一份 `claude_handover_report.md`，並存入專案根目錄下的 `/Claude Engineer/` (若是測試則存入 `/Claude DQA/`)。
   - 必須要求 Claude：「若開發中踩坑或解決了複雜 Bug，必須將經驗寫入 `.agents/lessons_learned/` 中供 lesson-maintainer 整理。」
4. **雙重品管強制驗收 (DQA Bypass Prevention)**：
   - PM 在收到 Claude Engineer 的交接報告後，【絕對禁止】直接結案。
   - 必須立刻發起雙重品管：**首先呼叫原生的 TDD_DQA 與 SDD_DQA 進行沙盒初步驗收，隨後再發包給 Claude DQA 進行外包層級的最終審查。**

   *範例指令*：`npx @anthropic-ai/claude-code -p "請根據 PRD 實作 auth 模組。【最高守則】絕對只能修改 src/ 與 tests/。完成後，請產出 claude_handover_report.md 存入 /Claude Engineer/。若有踩坑請紀錄至 .agents/lessons_learned/。"`
Claude Code CLI 在背景執行時，有時會暫停並在終端機輸出「需要使用者同意權限 (例如: 執行特定腳本、刪除檔案、存取網路)」。
- **絕對禁止擅自 Bypass**：身為 PM，你**絕對不可以**自己猜測或下達 `y` 強行通過。
- **強制通報 CEO**：一旦偵測到 Claude Code 卡在權限請求狀態，你必須立刻停下所有動作，向 CEO 說明情況：「Claude Code 正在請求危險權限 (例如刪除檔案)，請您確認。若同意，請輸入 `/approve`」。取得 CEO 的 `/approve` 後，才能傳送同意指令給 Claude 繼續執行。

## 三、 錯誤接管 (Error Handling & RCA)
若 Claude Code 執行失敗、回傳非 0 的 Exit Code，或發生崩潰：
1. PM 必須立刻中斷 Claude Code。
2. 在終端機執行 `python .agents/skills/Johnny-project-team/scripts/run_log_agent.py`，啟動 Log Agent 進行 Root Cause Analysis (RCA)，並將失敗原因與浪費的 Token 紀錄至 `Logs/Master_Log.md`。
