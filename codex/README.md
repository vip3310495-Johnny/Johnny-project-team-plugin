# Johnny Project Team — Codex Edition

[![Plugin version](https://img.shields.io/badge/version-2.1.8--codex.1-blue)](plugins/johnny-project-team-codex/.codex-plugin/plugin.json)
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

## 新專案檔案架構

PM 發現目標是全新專案時，使用 `johnny_new_project.py` 一次建立標準骨架並
初始化本機 Git repository（預設分支 `main`）：

```powershell
python <plugin-root>\skills\johnny-project-team\scripts\johnny_new_project.py `
  --project <new-project-path> --name "<product-name>"
```

腳本只接受不存在或空白的目標資料夾，且不會自動建立 commit。標準架構如下：

```text
<project>/
├─ src/                         # 唯一產品交付與 Phase 3 commit 根目錄
│  ├─ app/                     # 主程式
│  ├─ tests/                   # Engineer 維護的永久自動測試
│  │  ├─ unit/
│  │  ├─ integration/
│  │  ├─ regression/
│  │  └─ fixtures/
│  ├─ config/                  # 必要 runtime config
│  ├─ migrations/              # 資料庫 migrations
│  ├─ scripts/                 # 產品建置、啟動與維運腳本
│  ├─ delivery-manifest.json
│  └─ README.md
├─ TDD_DQA/{tool,evidence}/    # TDD DQA 的獨立工具與證據
├─ SDD_DQA/{tool,evidence}/    # SDD DQA 的獨立工具與證據
├─ Claude DQA/{tool,evidence}/ # 手動 Claude DQA 工具與證據
├─ PM/Context/                 # 規劃與 Task Context Packs
├─ Architect/                  # 架構流程文件
├─ Logs/                       # 開發流程紀錄
├─ .johnny/                    # Johnny gate state/evidence
├─ .agents/                    # Agent context/lessons
└─ .gitignore
```

依賴與建置檔也以 `src/` 為工作根目錄，例如 `src/package.json`、
`src/pyproject.toml`、`src/Cargo.toml` 或 `src/pom.xml`。第一次 baseline
commit 可包含根目錄 `.gitignore` 與 `src/`；Johnny 啟用後的 Phase 3 產品
commit 只能包含 `src/**`。DQA 可在自己的 `tool/` 建立獨立測試程式，但這些
是本機開發證據，不得混入產品 commit；適合長期保留的回歸測試由 Engineer
移植至 `src/tests/`。TE 始終唯讀，只能執行 DQA 已建立的工具。

模型推薦矩陣初始值為 PM／Architect：`sol (Medium)`、Engineer：
`terra (Medium)`、TDD／SDD／DQA coordinator：`terra (High)`、Security DQA：
`sol (Medium)`、TE：`Luna (High)`；Phase 0 仍須確認當前環境可用性，
Phase 2 → 3 前仍須取得使用者核准。

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
