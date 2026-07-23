# Phase 3: 實作與驗收雙迴圈 (Dev & Acceptance Loop)

> **【定位與範圍】**：Milestone 微觀開發與驗收執行處。強制實施「規格契約 (Intent Contract)」、「三方上下文強灌 (Context Injection Payload)」、「衝突修合約再開工 (Amend Before Dev)」與「異步變更日誌寫入 (Parallel Change Log Generation)」。

---

## 1. 微觀規格擬定 (Milestone PRD Generation)
- **架構對齊**：PM 必須**讀取架構師檔案 (`System_Architecture.md` / ADRs)**。
- **PRD 產出**：PM 依據架構邊界與 Milestone 範疇產出微觀實體檔案 `PM/Milestones/M<N>_PRD.md`，作為 DQA 撰寫驗收合約之基準。

## 2. BDD 驗收合約與測試項目審核 (BDD Acceptance Contract & Review)
- PM 喚醒 `SDD_DQA` 與 `TDD_DQA` 產出合約檔案 `specs/sdd_spec.md` 與 `specs/tdd_spec.md`。
- **BDD & TO-DO Checklist**：合約須採 BDD 語法 (`WHEN...THEN...`) 且包含標準 Markdown Checklist (`- [ ]`)。
- **測試項目超標審核協定 (Exceed Limit Review Protocol)**：
  - 預設單一合約測試項目上限為 30 項。
  - **若 DQA 評估有必要超過 30 項**，DQA 嚴禁擅自擴充，**必須提交 PM 自動進行內部審查與核准 (完全無需 CEO 參與，每個小 Milestone 最多允許提交審核 1 次)**。PM 審查放行後寫入 `specs/.pm_exceed_approved` 驗證 Token 即可放行過關！

## 3. 規格簽核放行閘門 (Spec Approval Gate Enforcement)
- PM 將 `specs/` 呈交 CEO 簽核 (輸入 `/approve`)。
- PM 強制執行放行 Hook：
  `python .agents/skills/Johnny-project-team/scripts/verify_spec_approval_hook.py`
- 驗證授權通過始解鎖開發流程。

## 4. 三方上下文物理強灌 (Three-Way Context Injection Payload)
- 在喚醒 Engineer 前，PM 必須執行物理強灌 Hook `inject_specs_hook.py`，將以下 **三方權責文檔完整強灌至 Engineer 之 System Prompt Payload**：
  1. **架構師檔案** (`System_Architecture.md` / ADRs)
  2. **當前 Milestone PRD** (`PM/Milestones/M<N>_PRD.md`)
  3. **DQA 驗收合約** (`specs/sdd_spec.md`, `specs/tdd_spec.md`)

## 5. 三方合約衝突排解與修合約開工協定 (Contract Conflict & Amend-Before-Dev Protocol) [CRITICAL]
- **工程師衝突回報**：Engineer 在開工前或實作中，若發現 **PRD、DQA 驗收合約、架構師檔案** 三者之間出現矛盾或邏輯衝突，**必須立刻停工並呈報 PM**。
- **階層排解與 CEO 升級**：
  - PM 優先進行協調與排解。
  - 若 PM 無法決定，PM **必須立刻呈報 CEO 請求終極裁決**。
- **修合約再開工鐵律 (Amend Before Dev)**：衝突裁決後，PM **必須先指示相關角色 (Architect / PM / DQA) 修改並更新其權責合約與文檔**，確保三方合約 100% 一致後，**才允許指示 Engineer 重新開工**！

## 6. 沙盒開發與防護網 (Sandboxed Execution & AgentShield)
- Engineer 在隔離沙盒 (Branch Workspace) 依據強灌之三方 specs 進行代碼實作。
- **AgentShield Guard**：底層持續監控，高危指令即刻攔截。
- 完成編譯與基本功能驗證後交付進度。

## 7. DQA 物理勾選驗收防爆 (DQA Checklist Verification Hook)
- DQA 根據 `specs/*.md` 逐項進行驗收測試，成功者將 `[ ]` 標註為 `[x]`。
- **Automated Inspection Hook**：提交報告前觸發：
  `python .agents/skills/Johnny-project-team/scripts/verify_dqa_checklist_hook.py`
- 若掃描出未勾選之 `[ ]`，直接亮紅燈物理阻斷提交，退回工程師修復至 100% `[x]` 覆蓋。

## 8. Milestone 異步變更日誌寫入與平行流水線 (Parallel Change Log Generation) [CRITICAL]
當當前 Milestone (例：Milestone 1) 完成驗收與 CEO 放行後，PM **必須執行異步平行流水線**：
1. **Milestone 1 通過**：CEO `/approve` 驗收完成。
2. **下階段 PRD 擬定**：PM 撰寫 Milestone 2 的 PRD (`PM/Milestones/M2_PRD.md`)。
3. **DQA 審核與工程師派遣**：DQA 審核 M2 specs 通過，PM 派遣 Milestone 2 工程師進場寫扣。
4. **PM 趁空檔撰寫變更日誌 (Parallel Change Log Generation)**：
   - PM 趁等待 Milestone 2 工程師開發的空檔，彙整並撰寫 **Milestone 1 工程師實際修改之細部變更摘要**，存為 `PM/Changes/M1_Change_Log.md`。
   - 此變更日誌留供 Phase 5 架構師進行完工對照。

## 9. 外部獨立審查 (Third-Party Independent Audit)
- 內部驗收通過後，呼叫外部 Claude CLI 進行極端測試與防禦性抓漏。
- 若發現瑕疵退回修復；通過則宣布該 Milestone 正式完工。

## 10. Milestone 迴圈與階段跳轉 (Phase Gate Transition)
- **多 Milestone 迴圈**：重複 Step 1~9 直至所有 Milestone 完工。
- **Phase 3 -> 4 跳轉**：全數完工後向 CEO 請求 `/approve` 簽核，執行階段閘門腳本：
  `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 3 --to_phase 4 --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
- [GREEN LIGHT] 後正式進入 Phase 4 成品驗收。
