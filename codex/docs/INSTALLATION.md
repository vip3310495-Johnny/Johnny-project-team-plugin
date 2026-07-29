# Codex Edition 安裝

## 安裝 Plugin

在儲存庫根目錄執行：

```powershell
codex plugin marketplace add .\codex
codex plugin add johnny-project-team-codex@johnny-project-team-github
codex plugin list
```

## 啟用專案

若是全新專案，先由 PM 建立標準骨架與 Git repository：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_new_project.py `
  --project <new-project-path> --name "<product-name>"
```

檢查內容後，建立只包含 `.gitignore` 與 `src/` 的乾淨 baseline commit。
開發流程資料夾已由 `.gitignore` 排除。

專案必須已有乾淨的初始 Git commit：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  enable --project <project-path>
```

此命令只設定該 repository 的 `core.hooksPath=.johnny/git-hooks`，不修改 global
Git config，也不覆蓋專案的 `AGENTS.md` 或 `.gitignore`。

確認狀態：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  status --project <project-path>
```

## 升級既有專案

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  migrate --project <project-path>
```

Migration 會更新 managed config、固定第 5 次 DQA escalation、將產品根目錄
收斂為 `src/`、更新 context manifest 與 ECC selection v2，同時保留無衝突
的專案自訂設定。升級前應先將既有產品程式、永久測試、依賴、migration 與
runtime config 移入 `src/`。

## 停用

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  disable --project <project-path>
```

停用會還原先前 repository-local hooks path，並保留 `.johnny` evidence。
