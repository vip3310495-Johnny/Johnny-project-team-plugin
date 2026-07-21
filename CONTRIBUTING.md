# 🤝 貢獻指南 (Contributing to Johnny-Project-Team)

歡迎來到 **Johnny-Project-Team Plugin**！這是一個專為 Google Antigravity 打造的多重代理人沙盒框架。我們非常歡迎任何形式的開源貢獻。

在您發起 Pull Request (PR) 前，請務必了解我們的「防爆沙盒鐵律」。

## 🛡️ 防爆沙盒開發鐵律 (The Sandbox Rules)

為了確保主系統 (`scripts/` 與 `.agents/`) 不被 AI 代理人誤刪或惡意竄改，我們內建了極其嚴格的 Git Hooks 與防禦機制。所有的程式碼開發，必須遵循以下物理限制：

1. **僅限修改 `src/` 與 `tests/`**
   - 所有的商業邏輯與新功能實作，絕對只能放置在 `src/` 目錄。
   - 不論是人類開發者還是 Claude 外包代理人，**嚴禁觸碰 `scripts/` (底層腳本) 或 `.agents/` (知識庫)**。如果您觸犯這條紅線，內建的 `path_guard.py` 將會進行物理攔截，您的 Commit 將會失敗。
   - 若您是核心架構師，需要修改底層，請確認您擁有 VIP 通行證 (`SKIP_PATH_GUARD=1`)。

2. **嚴格的雙重品管驗收 (Dual DQA Verification)**
   - 您提交的程式碼，必須包含對應的單元測試與功能測試。
   - 在合併至 `main` 之前，我們將會啟動自動化測試（TDD_DQA 與 SDD_DQA）。
   - 若您的程式碼是由 Claude 或其他 LLM 生成的，我們將要求先進行 Claude DQA 的初步審核。

3. **禁止目錄污染**
   - 新增的文件、架構圖，請放置於 `PM/` 或 `Architect/`。
   - 不要把測試產出的暫存檔留在專案根目錄。

## 🚀 如何發起 Pull Request

1. **Fork 本專案**：在您的帳號下建立分支。
2. **切換開發分支**：`git checkout -b feature/your-feature-name` (禁止直接在 main 開發)。
3. **遵循上述鐵律開發**：修改 `src/` 下的程式碼。
4. **提交變更**：`git commit -m "feat: your awesome feature"` (請遵守 Semantic Commit Messages)。
5. **發起 PR**：在 GitHub 上發起 Pull Request，並描述您的修改內容。

感謝您的貢獻，讓我們一起將 AI 專案管理推向新的境界！
