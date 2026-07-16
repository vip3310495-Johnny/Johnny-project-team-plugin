# Phase 2: DQA 進場與邊界規劃 (DQA Planning & Boundary Handshake)

本階段發生在 Phase 1 (PM 產出 PRD 與架構圖) 完成後，以及 Phase 3 (工程師動工) 之前。此為 DQA 確保品質的關鍵防線。

## 1. 邊界握手協議 (Boundary Handshake)
PM 必須在此階段正式發布當前 Milestone 的 `In-Scope` (開發範圍內) 與 `Out-of-Scope` (不涵蓋範圍) 清單。
此清單將做為 DQA 測試與工程師開發的「合約」。

## 2. DQA 規格守門 (Spec Gatekeeping) [NEW]
- 在啟動測試腳本撰寫前，SDD DQA 必須先檢視 PM 產出的 `PM/Milestones/M<N>_PRD.md`。
- **退件權發動**：若計畫書中的驗收標準模糊、缺乏邊界條件，不足以轉化為嚴謹的測試案例，SDD DQA **必須發動退件權**，將流程打回 Phase 1 要求 PM 重寫。絕對禁止帶著模糊的規格進入開發。
- **簽核放行**：若計畫書合格，SDD DQA 必須要求 PM 將文件底部的 `[ ] SDD DQA 授權同意` 改為 `[x]`。

## 3. 測試策略制定
在產出測試計畫前，**SDD DQA 與 TDD DQA 皆必須強制執行「知識繼承」**：讀取團隊知識庫 `Logs/lesson_learnt_registry.md`。若發現過去曾發生特定類型的 Bug，DQA 必須自動為未來的測試計畫新增專屬的測試防線，確保同一個坑不踩兩次。

- **SDD DQA**：產出體驗與邏輯驗證計畫。針對 UI 流程、A11y (無障礙設計)、與業務邏輯進行規劃。
- **TDD DQA**：產出極端邊界測試計畫 (包含惡意輸入設計、覆蓋率檢查策略、靜默錯誤獵殺計畫)。並且必須強制參考 `tdd-integration.md` 中的**高階防禦體系** (狀態機、併發、快速失敗、時序隔離)，以最高裁量權決定是否啟動對應防線。
- **Mock Data 建立**：TDD DQA 必須建立首版 `Mock_Data.json`，存放在 `/TDD_DQA/Mock_Data.json`，確保工程師有一致的測試基準。

## 4. 測試邊界審核 (PM Veto)
PM 必須嚴格審核 SDD DQA 與 TDD DQA 產出的測試計畫。
**PM 否決權**：一旦發現測試案例「越界」測到了 `Out-of-Scope` 的功能，PM 必須行使否決權 (Veto)，將測試計畫退回重寫。

## 5. 輔助工具預備
DQA 必須預先撰寫好自動化測試工具腳本，並分別存入：
- `/SDD_DQA/tool/`
- `/TDD_DQA/tool/`

這些工具稍後將在 Phase 3 中由 TE (Test Engineer) 負責執行。

## 6. 安全護欄政策 (AgentShield Org Policy) [NEW]
為了防範後續 Phase 3 開發中發生 AI 幻覺引發的毀滅性操作或機密外洩：
- **架構師與 PM 必須共同擬定** `org_security_policy.json` (組織安全規則)，包含專案特有的禁止讀寫路徑 (如專屬的 Secrets 檔)、以及高危險指令禁令。
- 此 Policy 檔案將成為 Phase 3 時 `agent_shield_hook.py` 的安檢基準。

## 7. 進入條件 (Phase Gate Execution)
在正式進入 Phase 3 之前，必須滿足以下條件：
1. PM 批准所有測試計畫、安全護欄政策 (`org_security_policy.json`) 建立完畢，且工具就緒。
2. **【強制】階段閘門防線 (Phase Gate Hook)**：
   - PM 必須主動向 CEO 說明：「Phase 2 (DQA 規劃) 已完成。請您檢視計畫，若同意請輸入 `/approve` 讓我能進入 Phase 3 開發階段。」
   - 取得 CEO 的 `/approve` 指令後，PM 必須在終端機強制執行：
     `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 2 --to_phase 3 --prd_path <PM/Milestones/M<N>_PRD.md 路徑> --ceo_signature "/approve"`
   - 若為**全自動模式**，則加上 `--auto` 參數。
   - **只有當腳本回傳 [GREEN LIGHT] (exit 0) 時，專案才能正式進入 Phase 3。** 否則 PM 必須依照錯誤訊息補齊簽核 (包含確保 SDD DQA 已在文件內打勾)。
