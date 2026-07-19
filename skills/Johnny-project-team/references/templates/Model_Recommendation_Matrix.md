# 🤖 模型與角色適配推薦矩陣 (Model Recommendation Matrix)

> [!IMPORTANT]
> **PM 必讀指南**
> 在 Phase 0 階段，PM 必須檢視專案需求，並為下列每個預設代理人分配最適合的模型與思考層級。
> 若專案有新增其他客製化角色，請自行擴充此表格。
> **請在完成填寫後，強制要求 CEO 審閱並於最後一欄打勾簽核 (✅)。**

| 角色名稱 (Role) | 設定檔位置 (Config Path) | 角色作用 (Description - 60字內) | 推薦模型 (Recommended Model) | 思考層級 (Thinking Tier) | CEO 簽核 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **PM (主控端)** | `skills/Johnny-project-team/SKILL.md` | 專案大腦。負責流程控管、需求拆解、指揮調度其他子代理人，並負責與 CEO 溝通。 |  |  | [ ] |
| **Architect** | `agents/architect.json` | 系統架構師。負責決定技術棧、畫出 System Flow Diagram，以及制定開發規範。 |  |  | [ ] |
| **Engineer** | `agents/engineer.json` | 核心開發者 (本地預設)。負責根據架構圖與 PRD 在 `src/` 中進行具體的程式碼實作。 |  |  | [ ] |
| **TDD DQA** | `agents/tdd_dqa.json` | 理科品管。負責撰寫單元/E2E測試，嚴格審查極端邊界，並確保覆蓋率。 |  |  | [ ] |
| **SDD DQA** | `agents/sdd_dqa.json` | 文科品管。負責核對實作是否符合 PRD 業務邏輯，並進行 UI/UX 視覺對齊與無障礙審查。 |  |  | [ ] |
| **Claude DQA** | 外部終端機 (`claude` CLI) | 外部獨立審查員 (非本地預設)。透過不同模型架構進行防偽與交叉驗證抓漏。 |  |  | [ ] |

---

### 📝 填寫範例參考 (僅供參考，請刪除)
* **推薦模型**：`Gemini 1.5 Pro`, `Gemini 2.0 Flash`, `Claude 3.5 Sonnet` 等。
* **思考層級**：`High` (深度推論/複雜邏輯), `Medium` (一般開發), `Low` (快速反應/簡單校對)。
