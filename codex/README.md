# Johnny Project Team Plugin（Codex）

可驗證的 Codex 多代理專案治理 Plugin：將 CEO 核准、Phase Gate、大小 Milestone、DQA、TE、完整 Log 與 lessons learned 置於可追溯且 fail-closed 的流程中。

## 核心能力

- Phase 0 以 Grill-me 對談引導 CEO 完成 Why／Who／What／Where／When-Action 與希望的設計風格，再建立可核准的 5W 初始計畫書。
- 本機 Approval Ledger 將核准綁定明確 scope、artifact 路徑、SHA-256 與語意指紋；語意變更自動使核准失效。
- Phase 0 分為 5W 核准、Architect How、雙 DQA 與獨立 Exit 核准；How 必須以 `5W-TRACE` 追溯產品方向。
- Phase 3 起要求 SDD、TDD、Claude 三重 DQA；外部 Claude CLI 不會自動執行，且需要 CEO 成本核准 Ledger。
- TE 僅執行測試與蒐證；Phase 3／4 合併測試項目上限為 30／50，超限需要 PM 核准。
- 以 `.agents/project_state.json` 為唯一權威狀態，並保留 JSONL 完整歷史 Log、敏感資料遮罩與 trace ID。

## 開始使用

安裝後，以「使用 Johnny Project Team 規劃這個開發任務」啟動。PM 會先依 `grill-me-phase0.md` 引導 CEO 對齊 5W 與設計方向，未取得 `PHASE0_5W_ALIGNMENT` 前不會正式派遣 Architect。

治理工具位於 `skills/Johnny-project-team/scripts/project_governance.py`：

```powershell
python project_governance.py init --project-dir <project>
python project_governance.py approve ...
python project_governance.py gate ...
```

所有寫入均以 UTF-8 處理。Plugin 不會安裝或修改 Git hooks，也不會自動呼叫付費外部服務。

## 驗證

```powershell
python -m unittest discover -s tests -v
python <skill-creator>/scripts/quick_validate.py skills/Johnny-project-team
python <plugin-creator>/scripts/validate_plugin.py .
```

目前版本含 18 項治理回歸測試，涵蓋 Phase 0 forward test、核准失效、DQA report/context 指紋、TE 邊界、Milestone 隔離、Windows Unicode 與 Hook fail-closed 行為。

## 結構

- `skills/Johnny-project-team/`：主 Skill、Phase 規則、治理工具與參考規格。
- `agents/`：統一角色設定 Schema。
- `tests/`：Plugin 治理回歸測試。
- `.codex-plugin/plugin.json`：Codex Plugin manifest。

## 安全邊界

角色設定屬流程約束，不等同平台物理權限隔離。若平台無法限制檔案系統或工具，Plugin 會明確記錄限制並以 Gate、artifact hash、report schema 與 fail-closed 驗證降低繞過風險。

## 授權

MIT。詳見 [LICENSE](LICENSE)。