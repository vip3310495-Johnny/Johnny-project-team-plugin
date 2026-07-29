# Codex Edition 安裝與更新

## 前置需求

- OpenAI Codex Desktop 或可使用 `codex plugin` 指令的 Codex CLI。
- Git。
- Python 3.10 以上，用於 repository-local gate scripts。
- Claude CLI 僅在手動啟用 Claude DQA 時需要。

## 從 GitHub 安裝

```bash
git clone https://github.com/vip3310495-Johnny/Johnny-project-team-plugin.git
cd Johnny-project-team-plugin
codex plugin marketplace add ./codex
codex plugin add johnny-project-team-codex@johnny-project-team-github
codex plugin list
```

Windows PowerShell 也可以使用：

```powershell
git clone https://github.com/vip3310495-Johnny/Johnny-project-team-plugin.git
Set-Location .\Johnny-project-team-plugin
codex plugin marketplace add .\codex
codex plugin add johnny-project-team-codex@johnny-project-team-github
codex plugin list
```

成功時，清單應顯示：

```text
johnny-project-team-codex@johnny-project-team-github  installed, enabled
```

## 更新

```bash
git pull
codex plugin add johnny-project-team-codex@johnny-project-team-github
```

每次安裝或更新後都應開啟新的 Codex task，讓 Skills、Hooks 與 Agent
profiles 從新版本載入。

## Hook trust

Codex lifecycle hooks 可以在 `SessionStart`、`SubagentStart` 與
`PreToolUse` 執行。首次安裝或 Hook 內容更新後，Codex 可能要求信任確認。
請先檢視 `plugins/johnny-project-team-codex/hooks/hooks.json` 與對應 Python
dispatcher，再允許執行。

## 啟用目標專案

1. 確認專案已初始化 Git。
2. 建立乾淨的 initial commit。
3. 執行 `johnny_project_hooks.py enable`。
4. 執行 `status` 確認 `.johnny/enabled.json` 與 repository scope。

Plugin 不會覆寫既有的 `AGENTS.md`、`.gitignore` 或自訂 Git hooks。

## 解除專案 Gate

```bash
python <plugin-root>/skills/johnny-project-team/scripts/johnny_project_hooks.py \
  disable --project <project-path>
```

Disable 只還原該 Repository 先前的 hooks path，保留 `.johnny` 稽核證據。

## 疑難排解

- 找不到 Skill：確認已開啟新的 Codex task。
- Hook 沒有執行：檢查 Hook trust 與 `hooks/hooks.json`。
- Git commit 被阻擋：先執行 `status`，確認 Phase、branch、DQA evidence 與
  staged tree 是否一致。
- Phase 3 無法開始：Phase 2→3 必須選擇 `SUPERVISED` 或 `AUTONOMOUS`。
- 同一 DQA 第五次退件：必須由 CEO resolution 指令解除 Milestone freeze。
