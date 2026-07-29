# Johnny Project Team — Codex Edition

[![Plugin version](https://img.shields.io/badge/version-2.1.7--codex.1-blue)](plugins/johnny-project-team-codex/.codex-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](plugins/johnny-project-team-codex/LICENSE)

這是 Johnny Project Team 的 OpenAI Codex 版本，完整放在 `codex/`，不會覆蓋
儲存庫根目錄的 Antigravity Edition。

## 主要功能

- Phase 0～6 workflow 與 `SUPERVISED`／`AUTONOMOUS` Phase 3 policy。
- 一個 Ticket 對應一個 Milestone；TDD DQA PASS 後才進入 SDD DQA。
- 同一 Milestone、同一 DQA role 第 1～4 次 FAIL 返回 Engineer；第 5 次
  凍結該 Milestone 並提交 CEO。
- DQA evidence 綁定 Git `subject_tree`、`commit_tree`、review cycle 與 ECC
  selection hash。
- `johnny_pm_merge.py` 只合併已核准、無有效 escalation 且 conflict preflight
  通過的 Milestone。
- 122 份 ECC rules、22 個 ruleset；monorepo 依 active path 所屬 package
  選規則，React Native 不會載入 Web／React DOM 規則。
- Phase 1、3、5 使用結構化 prerequisite evidence；Phase 3 另外驗證
  Model Matrix 的模型可用性與核准者。
- Claude DQA 為手動選用，預設關閉；執行時必須使用相同 ECC selection。

## 目錄分離

| 項目 | Codex Edition | Antigravity Edition |
|---|---|---|
| 根目錄 | `codex/` | Repository root |
| Manifest | `.codex-plugin/plugin.json` | `plugin.json` |
| Agent profiles | `.codex/agents/*.toml` | `agents/*.json` |
| Hooks | Codex lifecycle hooks | Antigravity hooks |

## 安裝

```powershell
codex plugin marketplace add .\codex
codex plugin add johnny-project-team-codex@johnny-project-team-github
```

啟用指定 repository：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  enable --project <project-path>
```

升級既有專案：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_project_hooks.py `
  migrate --project <project-path>
```

## ECC selection

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_rules_refresh.py `
  --project <project-path> --paths src\feature.tsx
```

輸出寫入 `.johnny/ecc-selection.json`。Engineer、TDD DQA、SDD DQA 與
Claude DQA 必須使用相同 `selection_sha256`。

完整安裝方式見 [INSTALLATION.md](docs/INSTALLATION.md)，流程契約見
[WORKFLOW.md](docs/WORKFLOW.md)。
