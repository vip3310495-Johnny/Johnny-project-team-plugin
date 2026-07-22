# Johnny-project-team Hooks System [Draft / 實驗性 Roadmap]

> [!WARNING]
> 目前 Hook 系統尚在實驗階段，**請勿依賴控制器的自動掃描**。所有的 Hook 腳本必須由 PM 或 Agent 判斷時機並「手動觸發執行」。請期待未來的自動化更新。

`Johnny-project-team` 內建了一套輕量且強大的 Python Hooks 系統。這套系統允許開發團隊在專案的特定生命週期中，安插自動化攔截點（例如 Linter, 發送 Slack 通知, 資安掃描, 等等）。

## Hook 存放位置與觸發語言
- **預設存放目錄**：專案根目錄下的 `.agents/hooks/`
- **預設語言**：強烈建議使用 **Python (`.py`)**。Python 具備完美的跨平台相容性 (支援 Windows/Mac/Linux)，且能輕易解析 JSON 狀態檔。

## 支援的 Hooks 生命週期 (目前為手動觸發)
建議在下列特定的執行節點中，手動觸發對應的 Hook 檔案：

1. **`pre-phase1.py`**: 進入 Phase 1 (細節計畫) 之前觸發。
2. **`pre-dqa-audit.py`**: DQA 開始審查前觸發。可用於自動匯入測試資料庫。
3. **`post-dqa-audit.py`**: DQA 審查完畢後觸發。可用於將測試結果同步至 Jira 或 Slack。
4. **`pre-commit.py`** [最頻繁使用]: 在 Engineer 或 PM 嘗試 `git commit` 前觸發。這是攔截「義大利麵條程式碼」的最佳時機。通常在此掛載 `black`, `flake8` 等 Linter。
5. **`post-phase3.py`**: 專案所有模組 (Milestone) 開發與單體驗收完畢後觸發。
6. **`pre-release.py`**: Phase 4 (系統整機驗收) 通過後，正式進入部署階段前觸發。**【重要職責】**：負責檢查並確保 PM、Engineer、DQA 與 Architect 四方皆已達成「全票同意 (Unanimous Consent)」。若有任一方未核准或遺漏，必須立刻 `sys.exit(1)` 攔截上線，並可附加執行 CI/CD Pipeline 腳本。

## Hook 開發指南 (給開發者或 Agent)
當你在 `.agents/hooks/` 中建立上述檔名的 Python 腳本時，`workflow_controller.py` 會自動傳入對應的引數 (Arguments)。

### 執行範例 (以 pre-commit.py 為例)
控制器在背後會這樣呼叫你的腳本：
```bash
python .agents/hooks/pre-commit.py --project_dir "/path/to/project"
```

### 攔截邏輯 (Return Code)
Hooks 系統是透過 **Return Code (Exit Status)** 來判斷是否放行的：
- `sys.exit(0)`：代表 Hook 成功，流程繼續。
- `sys.exit(1)` (或任何非 0 數字)：代表 Hook 攔截失敗，控制器會立刻中斷當前行為，並強制亮起 `RED_LIGHT`，要求 PM 或 Engineer 處理錯誤。

### 範例：一個簡單的 Python Hook (`pre-commit.py`)
```python
import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_dir", required=True)
    args = parser.parse_args()

    print("[HOOK] 執行 pre-commit 檢查...")
    src_dir = os.path.join(args.project_dir, "src")
    
    if not os.path.exists(src_dir):
        print("[HOOK] 沒有 src 目錄，跳過檢查。")
        sys.exit(0)
        
    # 這裡可以實作呼叫 Linter 的邏輯
    # if linter_fails:
    #     print("[HOOK ERROR] Linter 檢查未通過！")
    #     sys.exit(1) # 阻斷 Commit
        
    print("[HOOK] 檢查通過！")
    sys.exit(0)

if __name__ == "__main__":
    main()
```
