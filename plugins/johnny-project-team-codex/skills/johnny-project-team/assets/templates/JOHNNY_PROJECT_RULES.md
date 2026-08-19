# Johnny Project Rules

<!-- johnny-project-contract-v4:start -->

處理任何 Phase 或 Milestone 前：

1. 執行 `johnny_project_hooks.py status`，確認目前 Phase，並讀取
   `.agents/context-manifest.json` 與當前 Task Context Pack。
2. Engineer 寫 code 或 DQA review 前，必須對 active product paths 使用目前的 ECC
   selection；路徑或技術棧改變時，重新執行 `johnny_ecc_rules.py` 並讀取全部回傳規則。
3. 一次只處理一個符合目前 Phase 的 Milestone branch 與一組 Ticket／Milestone。
4. 依 Phase 2 execution policy 執行：`SUPERVISED` 於每個 Milestone 要求 CEO 核准；
   `AUTONOMOUS` 只可在 DQA PASS 後使用 Phase 2 已記錄的 delegation。
5. 產品交付與永久測試只放在 `src/` 與 `src/tests/`。PM 自行建立的臨時或人工驗證程式
   只能放在 `PM/tests/`；PM、Engineer Handoff、DQA、Log、evidence 與其他流程產物不得
   混入產品 commit。
6. 所有 Agent 產出的報告、PRD、交接、審查、架構、測試與紀錄文件，以繁體中文（台灣用語）
   為主；程式碼、指令、檔案路徑、變數名稱、原始錯誤訊息與既有英文技術術語可維持原樣。
7. PM 文件只存於 `PM/` 的對應子目錄：`Planning/`、`PRD/`、`Flows/`、`DataFlows/`、
   `Contracts/`、`Context/`、`Milestones/`、`Changes/`、`Approvals/` 或 `tests/`；不得在
   專案根目錄或其他角色目錄建立 PM 文件。
8. 任何 hook、script 或 Agent 若以 stdout／stderr 傳遞 JSON 或其他機器可讀輸出，必須明確
   使用 UTF-8，且不得依賴 Windows 的系統預設編碼（例如 CP950）。Python 輸出 JSON 時，
   優先使用 `json.dumps(..., ensure_ascii=True)`；若需保留原始 Unicode，必須明確設定 stdout
   與呼叫端 subprocess 的 UTF-8 encoding，並在 Windows 繁體中文環境加入回歸測試。

<!-- johnny-project-contract-v4:end -->
