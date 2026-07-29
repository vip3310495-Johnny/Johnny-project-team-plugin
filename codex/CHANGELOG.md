# Codex Edition Changelog

此檔只記錄 `codex/` 版本；Antigravity Edition 使用儲存庫根目錄的
`CHANGELOG.md`。

## 2.1.7-codex.1 — 2026-07-29

### Added

- `johnny_pm_merge.py`：核對 Milestone approval、DQA、escalation、乾淨工作樹
  與 merge conflict 後，執行可稽核的受控 PM merge。
- Phase 1、3、5 結構化 prerequisite evidence 與 Model Matrix validator。
- `.johnny/ecc-selection.json` schema v2、rule hashes 與 selection hash。
- `johnny_project_hooks.py migrate` 舊專案升級命令。

### Changed

- ECC selector 改為 package-aware；混合 React Native／Web monorepo 不再互相
  洩漏規則。
- Claude DQA prompt 必須載入精確 ECC routes，evidence 記錄 selection hash。
- 相同 Milestone、相同 DQA role 的 CEO escalation 固定在第 5 次 FAIL。
- 正式 references 不再調用 experimental placeholders 或不存在的
  `johnny_te_dispatch.py`。

### Validation

- 新增 controlled merge、mixed monorepo、Model Matrix、migration、固定第五次
  escalation、Claude ECC prompt 與文件反向引用測試。

## 2.1.6-codex.1 — 2026-07-29

- 初始 Codex Edition、project-scoped Git gates、TDD/SDD DQA、兩種 Phase 3
  execution policy、122 份 ECC rules 與選用式 Claude DQA。
