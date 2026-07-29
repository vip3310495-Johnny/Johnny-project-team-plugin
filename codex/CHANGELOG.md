# Codex Edition Changelog

此檔只記錄 `codex/` 版本；Antigravity Edition 使用同層 `../antigravity/` 的
`CHANGELOG.md`。

## 2.1.8-codex.1 — 2026-07-29

### Added

- `johnny_new_project.py`：由 PM 為全新專案建立標準 `src/` 產品骨架、
  隔離的 PM/DQA 流程工作區，並初始化 `main` Git repository。
- README 新增完整檔案架構、目錄所有權與產品提交規則。

### Changed

- `src/` 成為唯一產品交付根目錄；永久測試、依賴／建置 manifest、
  runtime config、migration 與產品腳本皆集中在其下。
- Phase 3 Git gate 只接受 `src/**`；DQA tool、報告與 evidence 不得混入
  產品 commit。
- TDD／SDD DQA 可在各自 `tool/` 建立獨立測試工具，但不得修改 `src/`；
  TE 維持唯讀。
- Model Recommendation Matrix 初始值更新為 PM／Architect `sol (Medium)`、
  Engineer `terra (Medium)`、TDD／SDD／DQA coordinator `terra (High)`、
  Security DQA `sol (Medium)`、TE `Luna (High)`。
- Config schema 升級至 v3；migration 會拒絕仍有 tracked 產品檔案散落在
  `src/` 外的舊專案。

### Validation

- 新增新專案骨架、Git 初始化、非空目錄防呆、`src/**` gate、DQA workspace、
  模型矩陣與 schema v3 migration 測試。

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
