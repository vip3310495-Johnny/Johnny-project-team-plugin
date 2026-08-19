---
name: claude-dqa-orchestrator
description: Run a real, manually requested Claude CLI review for an enabled Johnny Project Team repository and submit its subject-tree-bound verdict to the shared DQA state machine. Use after TDD and SDD PASS when the user requires an independent Claude cross-check for a ticket or Phase 4.
---

# Claude DQA Orchestrator

Claude DQA is disabled and optional by default. Run it only when the user
requests it or the approved project configuration marks it required. It is an
independent reviewer, not a simulated persona and not an automatic pass.

1. Ensure the repository was enabled with `johnny_project_hooks.py`.
2. Stage the exact changes to review.
3. Confirm TDD and SDD PASS in the active review cycle.
4. Run `python ../johnny-project-team/scripts/claude_dqa.py --project <repo> --ticket <id> --reviewer-id claude-cli`.
5. The runner resolves `claude.cmd` on Windows and `claude` elsewhere, sends a
   read-only review prompt, saves raw evidence, and calls
   `johnny_dqa_record.py verdict --role claude`. It never writes DQA status itself.
6. Any missing executable, timeout, non-zero exit, malformed output, or non-PASS
   verdict cannot produce PASS.
7. Never invoke Claude while the state lock is held or from any hook.

A Claude FAIL requires only Claude again while `subject_tree` is unchanged.
Any product, test, product configuration, UI, or security-contract change
invalidates TDD, SDD, and Claude evidence and opens a complete review cycle.
