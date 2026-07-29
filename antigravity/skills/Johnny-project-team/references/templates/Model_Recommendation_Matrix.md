# 🤖 模型與角色適配推薦矩陣 (Model Recommendation Matrix)

> [!IMPORTANT]
> **PM 必讀指南**
> 在 Phase 0 階段，PM 必須檢視專案需求，並為下列每個預設代理人分配最適合的模型與思考層級。
> 若專案有新增其他客製化角色，請自行擴充此表格。
> **請在完成填寫後，強制要求 CEO 審閱並於最後一欄打勾簽核 (✅)。**

| 角色名稱 (Role) | 設定檔位置 (Config Path) | 角色作用 (Description - 60字內) | 推薦模型 (Recommended Model) | 思考層級 (Thinking Tier) | 單次預算 (Budget per Task) | 允許時間 (Allowed Time) | CEO 簽核 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **PM (主控端)** | `skills/Johnny-project-team/SKILL.md` | 專案大腦。負責流程控管、需求拆解、指揮調度其他子代理人，並負責與 CEO 溝通。 |  |  |  |  | [ ] |
| **Architect** | `agents/architect.json` | 系統架構師。負責決定技術棧、畫出 System Flow Diagram，以及制定開發規範。 |  |  |  |  | [ ] |
| **Engineer** | `agents/engineer.json` | 核心開發者 (本地預設)。負責根據架構圖與 PRD 在 `src/` 中進行具體的程式碼實作。 |  |  |  |  | [ ] |
| **TDD DQA** | `agents/tdd_dqa.json` | 理科品管。負責撰寫單元/E2E測試，嚴格審查極端邊界，並確保覆蓋率。 |  |  |  |  | [ ] |
| **SDD DQA** | `agents/sdd_dqa.json` | 文科品管。負責核對實作是否符合 PRD 業務邏輯，並進行 UI/UX 視覺對齊與無障礙審查。 |  |  |  |  | [ ] |
| **Security DQA** | `agents/security_dqa.json` | 資安品管 (外掛)。負責高敏感功能之漏洞掃描、供應鏈盤點與越權防護，需手動喚醒。 |  |  |  |  | [ ] |
| **Log Agent** | `agents/log_agent.json` | 日誌與觀測代理人。負責系統健康度遙測、繪製儀表板與提取教訓。 |  |  |  |  | [ ] |
| **Claude DQA** | 外部終端機 (`claude` CLI) | 外部獨立審查員 (非本地預設)。透過不同模型架構進行防偽與交叉驗證抓漏。 |  |  |  |  | [ ] |

---

### 📝 填寫範例參考 (僅供參考，請刪除)
* **推薦模型**：`Gemini 1.5 Pro`, `Gemini 2.0 Flash`, `Claude 3.5 Sonnet` 等。
* **思考層級**：`High` (深度推論/複雜邏輯), `Medium` (一般開發), `Low` (快速反應/簡單校對)。
* **單次預算**：每次呼叫該代理人的預算上限 (例如：`$0.5`, `$2.0`)。
* **允許時間**：預期該代理人單次任務的合理執行時間上限 (例如：`10 mins`, `1 hr`)。
