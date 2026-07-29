# Script catalog

Read this catalog before invoking bundled code. A script is not a hook merely
because an older filename or document called it one.

## Lifecycle dispatchers

| Script | Event | Application and limits |
|---|---|---|
| `hooks/johnny_session_context.py` | `SessionStart` | Read enabled state, Phase, context manifest, project rules, and applicable ECC rule routes; return concise developer context. Do not write files or infer missing approvals. |
| `hooks/johnny_subagent_context.py` | `SubagentStart` | Route a subagent to its role, Task Context Pack, and the same applicable ECC rule files. Do not copy full project history or advance state. |
| `hooks/johnny_tool_guard.py` | `PreToolUse` | Deny direct edits and Git commit/push on protected branches in Phase 3+. Keep the check fast and read-only. |

## Repository Git gates

| Script | Application |
|---|---|
| `scripts/johnny_new_project.py` | PM 僅在確認為全新專案後執行。腳本拒絕非空目標，建立標準 `src/` 產品樹與被忽略的 PM／DQA／流程工作區，在 `main` 初始化 Git，並刻意不建立 baseline commit，留待人工檢查。 |
| `scripts/johnny_project_hooks.py` | Run `enable`, `status`, `migrate`, or `disable`. `migrate` upgrades managed config and context routes without replacing unrelated project choices. |
| `scripts/johnny_guard.py` | 僅由產生的 `pre-commit` 與 `pre-push` 呼叫。驗證 branch、staged paths、DQA schema、產品 `subject_tree`、完整 `commit_tree` 與必要 verdict。Phase 3 會拒絕 `src/` 外的所有 staged path；不得把它當 reviewer 手動呼叫。 |

## State-changing commands

| Script | Application |
|---|---|
| `scripts/johnny_phase_gate.py` | Advance exactly one Phase after explicit approval. Transitions to Phase 1, 3, and 5 require structured `--evidence`; Phase 2→3 also requires `--execution-policy`. |
| `scripts/johnny_phase_prerequisites.py` | Import-only validator for Phase 0, Phase 2 Model Matrix, and Phase 4 acceptance evidence. Do not execute directly. |
| `scripts/johnny_dqa_record.py` | Use `verdict` as the only TDD, SDD, or Claude verdict entry, `reopen` for explicit rejection cycles, and `resolve-escalation` after the fifth same-role FAIL on one Milestone. Require evidence and append every transition to `.johnny/dqa-history.jsonl`. |
| `scripts/johnny_milestone_gate.py` | After the DQA-approved tree is committed, record one tree-bound Milestone approval. Require `--approval` under SUPERVISED; under AUTONOMOUS use the Phase 2 CEO delegation and never fabricate a fresh CEO message. |
| `scripts/johnny_pm_merge.py` | Merge one approved `codex/milestone-Mxx` into `feature/*` or `main` after clean-tree, approval, DQA, escalation, branch-ID, and conflict checks. Use explicit `--push` for the controlled origin push; write merge/push evidence and history. |
| `scripts/claude_dqa.py` | Manually run the real Claude CLI after TDD and SDD PASS. Save raw evidence and submit the result through `johnny_dqa_record.py`; never run from a hook. |
| `scripts/johnny_rules_refresh.py` | Run with `--paths <active-product-paths>` to write the shared `.johnny/ecc-selection.json` hash and `.agents/session-context.json`. Engineer and every reviewer use this same selection. |
| `scripts/johnny_lesson_record.py` | Atomically validate and store one structured lesson plus append-only history. Use instead of separated verify-then-write flows. |
| `scripts/log_aggregator.py` | Explicitly append a reviewed Log Agent artifact to `Logs/Master_Log.md`. Never treat a timestamp as proof of workflow completion. |
| `scripts/run_log_agent.py` | Explicitly run the bounded Log Agent pipeline described in `references/log-agent.md`; never attach it to lifecycle or Git hooks. |

## Read-only validators and decision aids

| Script | Application |
|---|---|
| `scripts/johnny_ecc_rules.py` | Detect the repository technology stack, keep `common` mandatory, apply each ECC file's `paths:` frontmatter to active product paths, and print exact rule routes as JSON, paths, or hook context. Run before Engineer implementation and every code DQA review; it is read-only and does not approve code. |
| `scripts/dqa_test_limit.py` | Count Markdown checklist items using Phase limits from `.johnny/config.json`; failure is a planning signal, not a DQA verdict. |
| `scripts/pm_context_compressor.py` | Check a Context Pack or Digest size before handoff. It does not summarize content or approve correctness. |
| `scripts/te_dispatch_plan.py` | Calculate bounded TE capacity for a parent DQA. It does not spawn agents or write state. |
| `scripts/analysis_paralysis_breaker.py` | PM-only, on-demand framing aid when a decision is stuck; it prints options and never selects or records CEO approval. |
| `scripts/socratic_challenger.py` | PM-only, on-demand feasibility prompts and bounded repository discovery; its successful exit is not Phase, DQA, or architecture approval. |
| `scripts/johnny_common.py` | Import-only library for Git, atomic JSON, append-only JSONL, file locks, and tree hashes. Never execute directly. |

## Experimental quarantine

The following placeholders have no formal runtime application and must not be
invoked, referenced as hooks, or accepted as PASS evidence:

`ahp_evaluator.py`, `check_coverage.py`, `circuit_breaker_generator.py`,
`devil_advocate_consensus_breaker.py`, `dqa_queue_manager.py`,
`dqa_toolbox_manager.py`, `five_whys_analyzer.py`, `generate_digest.py`,
`generate_pr_description.py`, `impact_mapping_validator.py`,
`init_spec_template.py`, `kano_classifier.py`, `lesson_learn_manager.py`,
`mece_evaluator.py`, `moscow_sorter.py`, `pdca_state_machine.py`,
`pert_estimator.py`, `poka_yoke_validator.py`, `project_context_manager.py`,
`query_lesson.py`, `record_lesson.py`, `release_manager.py`,
`roi_make_or_buy_evaluator.py`, `security_scanner.py`,
`shannon_entropy_limiter.py`, `topological_sorter.py`, `trace_extractor.py`,
`user_story_validator.py`, and `wsjf_calculator.py`.

Promote one only after implementing real input validation, failure conditions,
deterministic output, and tests; then move it into `scripts/` and add a formal
entry above.
