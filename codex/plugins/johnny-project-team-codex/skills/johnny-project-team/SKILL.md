---
name: johnny-project-team
description: Run the Johnny Project Team phase workflow in Codex with lifecycle context hooks, project-scoped Git gates, Milestone branches, review-cycle DQA evidence, and optional manual Claude DQA. Use when initializing, planning, implementing, reviewing, rejecting, approving, merging, or releasing a project under the Johnny workflow.
---

# Johnny Project Team for Codex

Act as the PM/main agent and report to the user. Use Codex plans, tools, and
collaboration primitives. Treat the bundled `SessionStart`, `SubagentStart`, and
`PreToolUse` hooks as concise context and guardrail dispatchers, not as reviewers.

## Runtime contract

1. PM 確認為全新專案時，以下列命令建立標準產品／流程目錄並初始化 Git：
   `python scripts/johnny_new_project.py --project <new-repo> --name "<name>"`.
   檢查結果後，建立只包含 `.gitignore` 與 `src/` 的乾淨 baseline commit，
   再以下列命令啟用 repository：
   `python scripts/johnny_project_hooks.py enable --project <repo>`.
2. Never write global Git configuration. The setup uses repository-local
   `core.hooksPath=.johnny/git-hooks`, so unrelated projects are unaffected.
3. Treat `.johnny/enabled.json` as the activation marker. Guards must fail open
   when the marker is absent and fail closed when an enabled project's state is invalid.
4. Keep Claude DQA disabled and not required by default. Permit the user to
   request it manually as an additional cross-check for any ticket or Phase 4.
5. Run a manually requested Claude DQA outside hooks:
   `python scripts/claude_dqa.py --project <repo> --ticket <milestone-id>`.
   The command invokes the real CLI, writes evidence, then delegates the verdict
   to `johnny_dqa_record.py`; no hook may invoke Claude or write a verdict.
6. Advance phases only through:
   `python scripts/johnny_phase_gate.py --project <repo> --to-phase N --approval "<user approval>"`.
   Transitions to Phase 1, 3, and 5 also require a schema-valid `--evidence`
   JSON file; Phase 3 evidence includes the approved, available Model Matrix.
   When advancing from Phase 2 to Phase 3, also require
   `--execution-policy SUPERVISED|AUTONOMOUS`.
7. Never overwrite a project's `AGENTS.md`, `.gitignore`, or existing hooks.
   The enable command records and restores any prior repository-local hooks path.
8. Treat DQA as TE's direct parent. A DQA may run at most two TE child agents
   concurrently and must reduce that number when the session has fewer free slots.
9. Classify Phase 3 scope as `FIXED`, `CONTROLLED`, or `DISCRETIONARY`.
   Apply `references/scope-contract-model.md`; do not treat every implementation
   difference as a contract violation.
10. Treat Security DQA and Log Agent as optional manual roles. Security DQA is
    read-only and does not join the default TDD-to-SDD gate. Log Agent may write
    only bounded observability and lessons-learned paths and never product code,
    contracts, architecture, or DQA verdicts.
11. Before invoking any bundled script, read `references/script-catalog.md`.
    Do not invoke files under `experimental/`; they are quarantined placeholders.
12. At session start and before every Phase or Milestone, inspect status and
    `.agents/context-manifest.json`; do not infer state from chat memory.
13. Before Engineer writes code or any DQA reviews code, run
    `python scripts/johnny_ecc_rules.py --project <repo> --paths <active-product-paths>`.
    Read every returned rule file. `common` is mandatory; detected language and
    framework layers override common guidance where they conflict. Never select
    Web React rules for a React Native project.
14. Treat the ECC selector catalog as closed and complete: all bundled
    `references/rules/*/` directories must be represented. After adding or
    changing rules, run `johnny_rules_refresh.py` and inspect the recorded
    `ecc_rules` routes before continuing.
15. `src/` 是唯一產品交付根目錄。Engineer 在 `src/` 下負責產品程式、永久
    測試 (`src/tests/`)、依賴／建置 manifest、runtime config、migration
    與產品腳本。Phase 3 commit 只能包含 `src/**`。
16. TDD DQA 只能在 `TDD_DQA/tool/` 撰寫獨立工具；SDD DQA 只能使用
    `SDD_DQA/tool/`；手動 Claude DQA 只能使用 `Claude DQA/tool/`。其報告
    與 evidence 留在相對應流程目錄，不屬於產品 commit。TE 維持唯讀且只能
    執行 DQA 提供的工具。可重用的回歸檢查必須交給 Engineer 納入
    `src/tests/`。

## Workflow

- Phase 0: clarify intent, non-goals, observable outcomes, and risks. Use the
  `5w1h-grill-me` skill when the request is underspecified.
  Model Matrix 初始值為 PM／Architect `sol (Medium)`、Engineer
  `terra (Medium)`、TDD／SDD DQA 與 DQA coordinator `terra (High)`、
  Security DQA `sol (Medium)`、TE `Luna (High)`；必須驗證模型可用性並
  取得使用者核准，不得把推薦值視為已可用。
- Phase 1: establish the architectural frame and external boundaries.
- Phase 2: let PM alone classify the contract and prepare the Phase 3
  construction package as dependency-ordered tracer bullets. Define exactly
  one ticket for every small milestone and use the same stable ID for both.
  Permit one evidence-backed classification challenge; PM makes the final decision.
  Inventory tools, accounts, hardware, test data, skills, and permissions before
  Phase 3. Classify a project as complex when it has at least ten small
  Milestones or equivalent cross-system, hardware, security, or UI complexity;
  group complex work into large Milestones of three to five dependent tickets.
  Create a one-page, versioned Task Context Pack for every ticket.
  Ask the CEO to choose `SUPERVISED` per-Milestone approval or `AUTONOMOUS`
  approval delegated at the Phase 2 gate.
- Phase 3: execute one approved, dependency-ready ticket/milestone at a time.
  Work only on `codex/milestone-Mxx`; do not commit or push directly to
  `feature/*` or `main`.
  Engineer 將所有產品交付檔案寫入 `src/`，永久自動測試放在 `src/tests/`。
  只 stage 與 commit `src/**`；不得包含 PM、DQA、Log、`.johnny` 或
  `.agents` 流程產物。
  Before implementation, route the active ticket's product paths through
  `johnny_rules_refresh.py --paths ...`; Engineer and both DQA roles must load the same selected
  common, language, and framework rule files. Re-run selection whenever the
  active product paths or technology stack changes.
  After Engineer delivers its demoable or verifiable vertical slice, require
  TDD DQA PASS followed by SDD DQA PASS for the same ticket and tree. Add Claude
  DQA only when the user explicitly requests it. A DQA FAIL returns work to
  Engineer and does not stop AUTONOMOUS execution. Count FAILs separately for
  each Milestone and DQA role. On the fifth FAIL from the same role, freeze that
  Milestone and require CEO conflict resolution.
  After required DQA passes, run `johnny_milestone_gate.py`. SUPERVISED requires
  explicit CEO approval; AUTONOMOUS records the Phase 2 CEO delegation. Only
  then unlock the next dependency-ready pair.
  Merge an approved Milestone only through `johnny_pm_merge.py --ticket Mxx
  --target feature/<release>` (or `main` for the final approved integration).
  Add `--push` only when the approved workflow should publish that target to origin.
  Record required subject-tree-bound verdicts in order:
  `python scripts/johnny_dqa_record.py verdict --project <repo> --ticket <milestone-id> --role tdd --result PASS|FAIL --evidence "<path-or-reference>" --reviewer-id "<stable-id>"`
  and then the same command with `--role sdd`.
  An SDD FAIL opens a new review cycle and requires both TDD and SDD again.
  A Claude FAIL requires only Claude again while the product subject tree is
  unchanged; any product change invalidates every prior PASS.
  Resolve a five-rejection freeze only with:
  `python scripts/johnny_dqa_record.py resolve-escalation --project <repo> --ticket <milestone-id> --role tdd|sdd|claude --approval "<CEO approval>" --resolution "<decision>"`.
  Escalate `FIXED` problems immediately to PM and freeze only affected work.
  Let Engineer make backward-compatible `CONTROLLED` changes while PM records them.
- Phase 4: run final integrated TDD DQA followed by SDD DQA for the same staged
  tree. Use a separate `phase4` evidence scope so Phase 3 ticket results cannot
  satisfy final acceptance. Run Claude DQA only when manually requested. Test
  compatibility objectively; do not review or approve PM's change ledger.
  DQA may delegate bounded, read-only execution to TE children.
- Phase 5: let PM produce As-Built documentation from the Phase 3 ledger. Let
  Architect verify it against the real system and sample critical routes.
- Phase 6: retrospect on scope quality and lessons without rewriting Phase 5 history.

Before each phase, read only the matching `references/phases/phaseN.md` plus
the relevant role references. Legacy Antigravity instructions in references
are background material; this runtime contract takes precedence.

## Physical gate model

The plugin bundles three official Codex lifecycle dispatchers:

- `SessionStart` returns the active Phase, minimal context, and complete
  applicable ECC rule-file routes for the current changed paths without
  injecting their full contents.
- `SubagentStart` returns the role, Task Context Pack, and the same applicable
  ECC rule routes.
- `PreToolUse` blocks direct edits or Git commit/push on protected branches.

Repository-local `pre-commit` and `pre-push` call one read-only dispatcher. It
validates activation, state, branch, staged paths, `subject_tree`, `commit_tree`,
review cycle, and required PASS results. Hooks never transition phases, launch
LLMs, create approvals, or write DQA verdicts. State-changing commands use one
short-lived OS file lock and append auditable history.

Read `references/hook-lock-analysis.md` before changing hook or phase logic.
Read `references/dqa-te-orchestration.md` before DQA delegates work to TE.
Read `references/scope-contract-model.md` before classifying, implementing,
testing, or reporting a requirement.
Read `references/log-agent.md` before invoking `johnny_log_agent`.
Read `references/script-catalog.md` to select any command or validator.

## Recovery

Inspect without mutation:

`python scripts/johnny_project_hooks.py status --project <repo>`

Disable only this project's hooks while preserving `.johnny` evidence:

`python scripts/johnny_project_hooks.py disable --project <repo>`

Do not use bypass environment variables as a normal workflow.
