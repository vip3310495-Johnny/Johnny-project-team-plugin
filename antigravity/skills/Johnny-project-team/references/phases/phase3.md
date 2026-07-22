# Phase 3: 實作與封裝核心迴圈 (Dev & Acceptance Loop)

本階段是每個小 Milestone 的實際開發與驗收執行處。必須嚴格遵循「規格先決 (Intent Contract)」與「物理餵食 (Context Injection)」。

## 1. 產出小 PRD
- PM 根據該 Milestone 的規劃，提出細部的實作 PRD，並強制輸出至 `PM/Milestones/M<N>_PRD.md`，作為 DQA 撰寫測試合約的基準。

## 2. DQA 撰寫測試合約 (強制 TO-DO 驗收單)
- PM 呼叫 `SDD_DQA` 與 `TDD_DQA`，要求他們產出測試合約。
- **產出要求**：DQA 必須建立實體檔案 `specs/sdd_spec.md` 與 `specs/tdd_spec.md`。
- **情境化與 Checklist 規範**：
  - 合約內必須使用 BDD 情境化語法 (例如：`WHEN 使用者點擊按鈕 THEN 畫面變更`)。
  - **【強制】** 必須包含標準 Markdown 格式的「TO-DO Checklist」，例如：`- [ ] 檢查按鈕顏色是否符合色碼`。

## 3. CEO 最終放行閘門
- PM 將產出的 `specs` 合約呈交給 CEO，請求放行。
- 取得 CEO 的 `/approve` 後，PM 必須強制執行攔截 Hook：
  `python .agents/skills/Johnny-project-team/scripts/verify_spec_approval_hook.py`
- Hook 會檢查 CEO 是否真的授權。沒有此簽核，後續完全無法動工。

## 4. 物理餵食機制 (Context Injection)
- 在正式喚醒 Engineer 前，PM 必須執行物理餵食 Hook：
  `python .agents/skills/Johnny-project-team/scripts/inject_specs_hook.py`
- 此腳本會強制讀取 `specs/` 內的合約內容。PM 必須將這份內容作為 System Prompt Payload 的一部分，直接塞給 Engineer，確保 Engineer 一出生大腦裡就有最新的規格。

## 5. 工程師開發與 AgentShield 防爆
- Engineer 根據灌入的 specs 進行代碼實作。
- 開發過程中，`AgentShield Hook` 會持續在底層監控，攔截危險指令 (如刪除專案或洩漏密碼)。
- 工程師完成後，編譯並確保程式可執行，隨後將進度交回給 PM。

## 6. DQA 驗收防呆閘門
- PM 請求 DQA 進行驗收。
- DQA 必須根據自己撰寫的 `specs/*.md`，逐條驗收並將 `[ ]` 打勾改為 `[x]`。
- **防呆攔截**：當 DQA 宣稱驗收完畢，準備將報告提交給 PM 前，必須觸發攔截腳本：
  `python .agents/skills/Johnny-project-team/scripts/verify_dqa_checklist_hook.py`
- 若該 Hook 掃描到 `specs/` 內還有任何一項是 `[ ]`，會直接亮紅燈，**物理禁止 DQA 提交報告給 PM**。DQA 必須將問題退回給工程師修正，直到所有 Checklist 全數達成 `[x]`。

## 7. Claude DQA 最終抓漏
- 若內部 DQA 皆綠燈通過，PM 會呼叫外部 Claude CLI 進行最後的獨立抓漏。
- 若 Claude 發現問題，必須將問題退回給工程師修正，並重新跑一次驗收流程。
- 若全數通過，該 Milestone 正式完工，PM 可選擇進入下一個 Milestone (跳回 Phase 3 的開頭)。

## 8. 進入成品驗收 (Phase 3 -> Phase 4 Gate)
- 當所有的 Milestones 都宣告完工後，PM 必須向 CEO 報告並請求進入 Phase 4。
- 取得 CEO 的 `/approve` 後，PM 必須強制執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 3 --to_phase 4 --ceo_signature "/approve"`
- 腳本回傳 `[GREEN LIGHT]` 後，正式進入 **Phase 4 (成品驗收階段)**。
