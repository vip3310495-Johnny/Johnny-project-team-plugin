# Codex Edition 安裝

## 安裝 Plugin

在儲存庫根目錄執行：

```powershell
codex plugin marketplace add .\codex
codex plugin add johnny-project-team-codex@johnny-project-team-github
codex plugin list
```

## 啟用專案

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

Migration 會更新 managed config、固定第 5 次 DQA escalation、context manifest
與 ECC selection v2，同時保留無衝突的專案自訂設定。

## 停用

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  disable --project <project-path>
```

停用會還原先前 repository-local hooks path，並保留 `.johnny` evidence。
