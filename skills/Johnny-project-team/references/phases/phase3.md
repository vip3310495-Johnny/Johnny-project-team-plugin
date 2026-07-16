# Phase 3: 開發與驗收循環 (The Chat Chain)

> **【中斷存檔提醒】** CEO 隨時可能下達「收工」或「暫停」等中斷指令。當收到該指令時，PM 必須立刻停止目前的開發迴圈，並觸發 `SKILL.md` 中定義的**中斷與存檔機制 (Interruption & Save State)**。

本階段為高頻率的實作與驗證循環，所有工作必須在獨立的 Feature 分支上進行。

## 1. 分支與開發前置
- Engineer 在獨立分支 (`feature/milestone-X`) 進行開發。
- 開發必須遵循 TDD 規範 (詳見 `references/tdd-integration.md`) 與終極戒律 (詳見 `references/engineering-agent.md`)。

## 2. Token Optimization (省 Token 留痕協議)
- **【強制規定】**所有 Agent 在聊天頻道中**禁止貼出大量程式碼**。
- 資訊傳遞一律採用「1-2句話解釋 + 檔案絕對路徑 (File Paths)」來回報進度與問題。

## 3. Smoke Test Barrier (工程師自檢防線)
- Engineer 準備交接給 DQA 之前，必須親自在終端機執行基礎建置或啟動指令 (如 `npm run build` 或 `npm start`)。
- **安全護欄 (AgentShield Self-Audit) [NEW]**：Engineer 必須在提交前強制執行 `python .agents/skills/Johnny-project-team/scripts/agent_shield_hook.py`。若掃描失敗 (紅燈)，工程師必須提供 Autofix 並重新掃描，絕對禁止將帶有安全漏洞或危險指令的程式碼交給 DQA。
- **防偷工減料 (Execution Verification)**：Engineer 必須透過 `ls` 證明檔案確實成功產生。若連基本編譯都會 Crash，嚴禁交接。
- **編譯自救方案**：若工程師遇到編譯失敗，PM 必須強制配發對應語言的 Build Resolver (位於 `references/ecc_agents/`，例如 `react-build-resolver.md`、`python-build-resolver.md`) 給工程師，要求其依照 RCA 流程排錯，嚴禁盲目試錯。

## 4. 單線程審查佇列 (Queue Manager)
- 當 Engineer 完工後，PM 必須透過 `scripts/dqa_queue_manager.py` 進行排隊。
- 系統保證一次只送審一位工程師的程式碼，徹底防堵 Git Merge Hell。
- **佇列死鎖防護 (Queue Lock Prevention)**：若 DQA 退回程式碼，必須同時呼叫 `finish` 指令釋放該次審查佇列，讓其他排隊中的工程師進入。該被退回的工程師修復完畢後，必須重新排隊。

## 5. 測試與串聯審查 (Sequential Review)
當輪到某程式碼審查時，流程如下：
1. **DQA 靜態審查 (Static Review)**：PM 指示 DQA 讀取對應語言的 Reviewer (位於 `references/ecc_agents/`，例如 `react-reviewer.md`、`python-reviewer.md`、`go-reviewer.md`)，對交接的程式碼進行靜態抓漏。若有架構問題直接退回。
2. **TE 平行驗證 (Parallel Verification)**：當 DQA 盤點發現測試案例 $\le$ 5 個時，由 DQA 自行執行；若 $> 5$ 個，DQA 必須指揮 PM 喚醒多名 TE 進行平行驗證。**(注意：TE 必須嚴格遵守 `references/te-persona.md` 的禁令，禁止自己改 Code，只能將 JSON 報告交還給 DQA 彙整)**。
3. **DQA Test Stalemate**：DQA 必須保證自己的腳本無語法錯誤。若修復腳本失敗超過 3 次，視為 Test Stalemate，交由 PM 處理。
4. **TDD DQA 第一關 (理科把關)**：
   - 確保測試 100% 通過且覆蓋率達 80%。
   - 使用 `references/dqa-analysis.md` 核對靜默錯誤、記憶體洩漏等易錯點。
   - **【動態運行強制令與 Docker 沙盒隔離 (Docker Sandbox Mandate)】**：絕對禁止只做靜態看 Code 分析，也**絕對禁止**直接在本地終端機 (Host OS) 下達任何執行指令 (如 `python test.py` 或 `npm test`)。
   - TDD DQA 必須且只能透過 Docker 容器來掛載執行測試指令，將所有潛在破壞行為 (爆炸半徑) 封死在虛擬貨櫃內。
     - *指令範例*：`docker run --rm -v ${PWD}:/app -w /app node:18 npm test` 或 `docker run --rm -v ${PWD}:/app -w /app python:3.9 pytest`
   - 若失敗，亮紅燈 (RED LIGHT) 直接退回。
5. **SDD DQA 第二關 (文科把關)**：
   - TDD 通過後，SDD 進行視覺對齊、A11y (無障礙) 審查與業務邏輯驗證。
   - **【規格合規性確認】**：SDD DQA 必須貫徹「SDD 開發精神」，嚴格比對產品實作是否 100% 吻合**全局 PRD** 與 **Milestone 細部開發計畫書**。若有任何遺漏或實作與 Spec 描述不符之處，立即退回。
   - **【動態體驗驗證 (Computer Use 整合)】**：絕對禁止只看截圖。SDD DQA 必須優先嘗試使用以下工具輔助測試：
     - 若為 Web 專案：使用 `gstack` (極速無頭瀏覽器) 實際開啟網頁、點擊按鈕、填寫表單。
     - 跨平台 UI 解析：強制呼叫 `omniparser` 來解析產品的螢幕截圖，取得所有按鈕、圖示的精確 Bounding Box (邊界框) 座標，判斷是否破版或對齊。
     - **若為非瀏覽器 (如 Native App / Desktop 軟體)**：`omniparser` 依然能精準解析任何截圖的 UI 元素。針對操作，SDD DQA 應利用 Python 的 `pyautogui`、`appium` 等自動化工具，配合 `omniparser` 回傳的座標進行實體游標點擊與輸入。
     - **【優雅降級 (Graceful Degradation)】**：若上述外部工具未安裝，SDD DQA 必須自動切換至替代方案，不得因此卡住流程：
       - `gstack` 未安裝 → 改用 `generate_image` 截取畫面 + 視覺分析能力進行 UI 審查。
       - `omniparser` 未安裝 → 改用目視比對方式審查 UI 對齊與破版，並在報告中註明「未使用自動化 UI 解析」。
   - **【邊緣狀態與微交互 (Vibe Review)】**：針對前端/UI 專案，SDD DQA 必須無情獵殺缺乏「Loading 狀態」、「無資料 (Empty) 狀態」與「Error 狀態」的裸奔畫面；並確保所有按鈕與連結都具備符合高質感 (Vibe) 的 Hover/Active 微動畫回饋。

6. **Claude Code DQA 第三關 (外部獨立核查) [強制]**：
   - **【不可跳過與嚴禁造假 (Anti-Fake Claude)】**：當本地的 TDD 與 SDD DQA 都給予綠燈後，PM **必須且只能**透過 `run_command` 工具在終端機呼叫 `scripts/claude_dqa_hook.py` (或是直接執行 `npx @anthropic-ai/claude-code`) 來喚醒外部的 Anthropic Claude 進行獨立審查。
   - **🚨 嚴禁使用 invoke_subagent**：PM **絕對不可以**試圖透過 `invoke_subagent` 指令去生出一個名為 "Claude DQA" 的子代理人！那只是用 Gemini 偽裝的假 Claude，這是嚴重的造假行為。必須透過終端機執行真正的 CLI。
   - **獨立意識與模型彈性**：Claude DQA 被嚴格設定為「不可輕信 PM 說的話」。它會親自去讀取專案檔案進行二次抓漏。**【模型選擇】**預設使用 `Sonnet` 模型，但 PM 必須允許 CEO 隨時透過參數或指令指定其他版本 (例如 `Sonnet-5`, `Opus` 等)。絕不可寫死版本號。
   - **通過條件**：只有當真正的 Claude CLI 回傳 PASS 時，這段程式碼才算真正通過測試。

## 5.1 修改即重審 (Anti-Bypass DQA) [CRITICAL]
- **【鐵律】**：若遇到 CEO 退件或任何測試環節退件，**只要 Engineer 有碰到 `src/` 裡的任何一行程式碼，就必須強制重新跑滿 TDD、SDD 與 Claude DQA 審查流程**，絕對禁止私下改完直接交給 CEO 複測。
- 只有 PM 針對「文件(md)」的微調可以豁免 DQA。

## 5.5 防盲目試錯機制 (Anti-Blind-Trial) [CRITICAL]
當工程師收到任何一關 DQA 亮紅燈退件時，**絕對禁止立刻去修改 `src/` 裡的程式碼**。
工程師必須強制先完成以下兩件事：
1. **除錯沙盤推演 (RCA)**：產出 `Debug_Hypothesis.md`，並將其嚴格分類存放在 `/Engineer/RCA/` 資料夾下 (例如 `/Engineer/RCA/M1_Login_Bug.md`)。檔案內需明確寫出報錯的 Root Cause (根本原因) 與接下來打算修改的檔案行數。
2. **提煉與寫入教訓**：將本次踩坑的知識點提煉成通則，並強制執行 Hook 寫入教訓庫 (必須帶上角色標籤)：
   `python .agents/skills/Johnny-project-team/scripts/verify_lesson_hook.py --role Engineer --proposal "你的具體教訓"`
3. **放行條件**：只有當 Hook 回傳 `[APPROVED]` 後，工程師才獲准依照沙盤推演的計畫修改實作代碼。

## 6. 變更請求阻斷機制 (Mid-Flight Spec Change Exception) [NEW]
在開發過程中 (Phase 3)，若 CEO 下達修改規格的指令，或 Engineer 發現原規格技術上不可行：
1. **強制暫停 (Pause)**：PM 必須立刻中斷當前的開發與審查佇列。
2. **降級回溯 (Rollback)**：PM 必須帶著新的需求降級回到 **Phase 1**，更新 `PM/Milestones/M<N>_PRD.md`。
3. **重新守門 (Re-Gatekeeping)**：更新後的計畫書必須再次經過 Architect 的架構影響評估，以及 SDD DQA 的 **Phase 2** 審核與腳本修正。
**絕對禁令**：嚴禁 Engineer 在沒有更新 PRD/Spec 的情況下，私下接受 PM 或 CEO 的口頭指令直接改 Code。這會導致 SDD DQA 依照舊 Spec 測試而產生無窮盡的退件死鎖。

## 7. 僵局裁決 (Stalemate Escalate)
- 若 Engineer 提交的代碼被 DQA 退回超過 **5 次**，觸發僵局。
- PM 強制暫停開發，撰寫 `Conflict_Report.md`，交由 CEO 進行最終裁決。
- **【PM 反推卸責任 (Anti-Buck-Passing)】**：PM 必須提出結構化的 Option A / Option B 給 CEO 選擇，絕對禁止直接把錯誤丟給 CEO 去敲指令。

## 8. 合併與大腦清洗
- **GREEN LIGHT**：若全數通過，PM 將分支合併回 `main` (若有衝突，Engineer 必須手動解衝突，詳見 `git-strategy.md`)。
- **知識匯流 (Knowledge Merge) [CRITICAL]**：在 `kill` Agent 之前，PM **必須先**讀取 `.agents/lessons_learned/` 目錄中各 Agent 的個人筆記 (如 `engineering_lesson_learn.md`、`dqa_lessons_learned.md`)，將有價值的踩坑經驗提煉合併至團隊統一知識庫 `Logs/lesson_learnt_registry.md`。這是防止 Agent 被回收後，個人記憶永久消失的最後防線。
- **子代理人記憶清除**：大型 Milestone 結束後，PM 必須強制 `kill` 掉舊的 Engineer 與 DQA，並 `invoke` 新的 Agent 以避免大腦幻覺。新 `invoke` 的 Agent 只需讀取 `Logs/lesson_learnt_registry.md` 即可獲得完整的團隊記憶。
- **【強制】PM 上下文壓縮 (ECC Memory Flush)**：
  - 子代理人清除後，PM 必須親自撰寫一份 `M<N>_Digest.md`，總結本次 Milestone 的核心架構變更、未解技術債、以及後續依賴事項。
  - 將檔案存入 `PM/Memory/` 目錄 (如 `PM/Memory/M1_Digest.md`)。若目錄不存在需先建立。
  - PM 必須執行：`python .agents/skills/Johnny-project-team/scripts/pm_context_compressor.py PM/Memory/M<N>_Digest.md`。
  - 腳本會嚴格驗證摘要是否**小於 800 字**。若超標 (RED LIGHT)，PM 必須重新精簡摘要，剔除無用的除錯流水帳；直到腳本回傳 [GREEN LIGHT]，PM 的記憶壓縮才算完成。

## 8.5 視覺化報告產出 (Visual Report Generation) [NEW]
在每個 Milestone 結束後、將成果送交 CEO 審查之前，PM 必須自動產出一份專屬的視覺化報告：
1. **強制使用 Mermaid**：**絕對禁止**要求工程師寫 Python 腳本來畫圖，PM 必須直接使用 Markdown 原生的 **Mermaid 語法** (`graph TD`, `sequenceDiagram`) 來產出圖表 Artifact。
2. **圖表儲存路徑與命名**：這兩份圖表**必須實體存放在 `PM/` 資料夾內**，且嚴格依據 Milestone 命名：
   - **`PM/M<N>_System_Flow.md`** (系統流程圖)：標示本次 Milestone 新增或修改的系統元件與路由。
   - **`PM/M<N>_Data_Flow.md`** (資料流向圖)：標示前後端 API 串接與資料庫讀寫狀態。
3. **CEO 簽核**：PM 必須將這兩份圖表連同 DQA 的最終測試報告，一併呈現給 CEO 進行審查與確認。

## 8.6 強制呼叫 Log Agent 撰寫編年史 [CRITICAL]
為了確保專案具備可追溯性，PM 必須在「Milestone 結束」、「DQA 連續退件(Stalemate)」、「CEO 退件」這三個節點，**強制在終端機執行**：
`python .agents/skills/Johnny-project-team/scripts/run_log_agent.py`
- **PASS 狀態**：紀錄通過的里程碑、架構設計摘要。
- **FAIL 狀態**：嚴格紀錄「退件原因(Root Cause)」、「Token 浪費點」與「流程偏離情況」。
- 注意：跳轉閘門會檢查 Log 更新時間，沒跑 Log Agent 絕對不准進入下一階段！

## 9. 狀態跳轉與簽核 (Phase Gate Execution)
在完成視覺化報告產出後，PM 必須執行以下跳轉授權流程：
1. **主動請求簽核**：PM 必須向 CEO 說明：「本次 Milestone 的視覺化報告與測試結果皆已出爐。請您檢視，若同意請輸入 `/approve`，我們將進行後續的跳轉。」
2. **執行階段閘門**：取得 CEO 的 `/approve` 指令後，PM 必須執行：
   `python .agents/skills/Johnny-project-team/scripts/phase_gate_hook.py --from_phase 3 --to_phase <目標階段> --ceo_signature "/approve"` (若為自動模式則加上 `--auto`)
3. **跳轉方向**：
   - 檢視 `PM/PRD.md` 中的 Milestone 清單。
   - 若**還有未完成的 Milestone** ➔ 目標階段設為 `1`，腳本放行後跳回 **Phase 1 (Milestone Detailed Planning)** 開始拆解下一個任務。
   - 若**所有 Milestone 皆已完成** ➔ 目標階段設為 `4`，腳本放行後推進至 **Phase 4 (Final Acceptance & Release)**，準備系統驗收。
