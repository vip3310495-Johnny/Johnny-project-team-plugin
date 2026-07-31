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

## 工作階段初始化與 Windows

Codex 的 lifecycle event 名稱是 `SessionStart`（支援 `startup`、`resume`、
`clear`、`compact`），並沒有 `PreSession`。成功的 hook 只會注入目前
repository、Phase、專案規則與 ECC 規則的**路由**；主 agent 仍必須依路由讀取
所有目前 Phase 所需的規則、角色設定與 Task Context Pack。

請直接在已啟用的 Johnny repository root 開啟 task。若 task 必須由父目錄開啟，
hook 只會選擇唯一一個已啟用的子 repository；若不存在或有多個候選，會回報可採取
動作的診斷訊息，而不會猜測目標。

可在任何上述位置重新建立完整、可稽核的初始化 context：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_initialize.py `
  --project <project-or-parent-path> --paths src\feature.tsx
```

此命令會驗證 exact repository、執行 managed migration、重新選擇 ECC 規則，並輸出
Phase、approval state、必讀檔案、managed agents、ECC routes 與 selection hash。每次
來源技術棧或 active product paths 改變時都要重新執行。

Windows hook 依序使用 `CODEX_PYTHON`（由 Codex 提供且驗證的 Python）、`py -3`、
`python3`、`python`。若皆不可用，hook 會輸出診斷訊息；不會修改 global PATH、
global Git config 或 Python 設定。

## 停用

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  disable --project <project-path>
```

停用會還原先前 repository-local hooks path，並保留 `.johnny` evidence。
