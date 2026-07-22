# Codex 相容性說明

此目錄是原始 GitHub plugin 的 Codex 相容版本。Codex 的唯一掛載點為
`.codex-plugin/plugin.json`，並由其中的 `skills: "./skills/"` 載入四個 skills。

## 已完成的轉換

- 將原本依賴 `invoke_subagent` 的 PM 流程改為使用 Codex 原生協作工具；只有在任務可獨立、範圍明確時才委派。
- 移除 Claude Code CLI 的自動外包要求，避免安裝外部 CLI、網路存取或權限流程的隱性依賴。
- 原始 `agents/*.json` 保留為歷史角色參考，不會被 Codex 掛載或自動執行。
- 原本的 Python hooks 改為「手動診斷工具」：未在 manifest 宣告 hooks，也不會寫入目標專案的 `.git/hooks/`。

## Hooks 安全邊界

`skills/Johnny-project-team/scripts/` 內的檢查程式可在需要時由使用者或 Codex 明確執行，並以傳入的 `--project_dir` 作為唯一作用範圍。`setup_hooks.py` 已改為安全的相容性提示程式，絕不建立、覆蓋或掛載 Git hooks。

因此本 plugin 不會與 Codex 全域 hooks、其他 plugin，或任一專案既有的 Git hooks 產生掛載衝突。
