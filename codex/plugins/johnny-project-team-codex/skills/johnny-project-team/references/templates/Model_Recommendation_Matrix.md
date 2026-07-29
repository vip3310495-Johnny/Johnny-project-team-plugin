# Model recommendation matrix

PM 在 Phase 0 選擇專案模型與 reasoning budget 時填寫此矩陣。下列 model
與 reasoning 是初始推薦值；PM 必須在 Phase 3 前確認可用性並取得使用者核准。

| Role | Codex configuration | Responsibility | Recommended model | Reasoning tier | Budget per task | Allowed time | User approved |
|---|---|---|---|---|---|---|---|
| PM | `assets/agents/johnny-pm.toml` | Scope, sequencing, user checkpoints, and final decisions | sol | Medium |  |  | [ ] |
| Architect | `assets/agents/johnny-architect.toml` | Architecture frame and Phase 5 As-Built verification | sol | Medium |  |  | [ ] |
| Engineer | `assets/agents/johnny-engineer.toml` | Implement one active ticket/milestone within the scope contract | terra | Medium |  |  | [ ] |
| TDD DQA | `assets/agents/johnny-tdd-dqa.toml` | Run behavior, regression, edge-case, and compatibility verification first | terra | High |  |  | [ ] |
| SDD DQA | `assets/agents/johnny-sdd-dqa.toml` | Verify specification and intent after TDD PASS | terra | High |  |  | [ ] |
| DQA coordinator | `assets/agents/johnny-dqa.toml` | Own DQA evidence, verdicts, and bounded TE delegation | terra | High |  |  | [ ] |
| TE | `assets/agents/johnny-te.toml` | Execute bounded read-only checks for the parent DQA | Luna | High |  |  | [ ] |
| Security DQA | `assets/agents/johnny-security-dqa.toml` | Optional manual security and trust-boundary review | sol | Medium |  |  | [ ] |
| Log Agent | `assets/agents/johnny-log-agent.toml` | Optional observability, context-drop, RCA, and lesson analysis |  |  |  |  | [ ] |
| Claude DQA | External `claude` CLI | Optional manual independent cross-check |  |  |  |  | [ ] |

Use only models available in the current Codex environment. Treat budget and
time values as ceilings, not targets. The user must approve any material model,
cost, or time change.
