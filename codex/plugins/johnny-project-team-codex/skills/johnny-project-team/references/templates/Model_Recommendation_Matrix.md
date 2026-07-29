# Model recommendation matrix

PM completes this matrix during Phase 0 when choosing models or reasoning
budgets for the project. Leave deployment-specific values blank until evidence
supports them.

| Role | Codex configuration | Responsibility | Recommended model | Reasoning tier | Budget per task | Allowed time | User approved |
|---|---|---|---|---|---|---|---|
| PM | `assets/agents/johnny-pm.toml` | Scope, sequencing, user checkpoints, and final decisions |  |  |  |  | [ ] |
| Architect | `assets/agents/johnny-architect.toml` | Architecture frame and Phase 5 As-Built verification |  |  |  |  | [ ] |
| Engineer | `assets/agents/johnny-engineer.toml` | Implement one active ticket/milestone within the scope contract |  |  |  |  | [ ] |
| TDD DQA | `assets/agents/johnny-tdd-dqa.toml` | Run behavior, regression, edge-case, and compatibility verification first |  |  |  |  | [ ] |
| SDD DQA | `assets/agents/johnny-sdd-dqa.toml` | Verify specification and intent after TDD PASS |  |  |  |  | [ ] |
| DQA coordinator | `assets/agents/johnny-dqa.toml` | Own DQA evidence, verdicts, and bounded TE delegation |  |  |  |  | [ ] |
| TE | `assets/agents/johnny-te.toml` | Execute bounded read-only checks for the parent DQA |  |  |  |  | [ ] |
| Security DQA | `assets/agents/johnny-security-dqa.toml` | Optional manual security and trust-boundary review |  |  |  |  | [ ] |
| Log Agent | `assets/agents/johnny-log-agent.toml` | Optional observability, context-drop, RCA, and lesson analysis |  |  |  |  | [ ] |
| Claude DQA | External `claude` CLI | Optional manual independent cross-check |  |  |  |  | [ ] |

Use only models available in the current Codex environment. Treat budget and
time values as ceilings, not targets. The user must approve any material model,
cost, or time change.
