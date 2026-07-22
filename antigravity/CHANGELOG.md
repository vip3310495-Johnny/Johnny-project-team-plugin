# 📝 更新日誌 (Changelog)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3.0.0] - 2026-07-21

### 🚀 Added
- **OpenSpec V3 Workflow Integration**:
  - **Intent & Non-goals**: Enforced in Phase 1 Global PRD to lock down development purpose and prevent scope creep.
  - **Milestone Sizing Gate**: Phase 2 transformed into a DQA "Milestone Reasonability" gatekeeper.
  - **BDD Spec Injection**: Phase 3 now strictly requires DQA to generate `specs/sdd_spec.md` & `specs/tdd_spec.md` with explicit TO-DO checklists.
- **Physical Phase Guards**:
  - `verify_spec_approval_hook.py`: Prevents development until CEO approves Phase 3 test specs.
  - `inject_specs_hook.py`: Physically injects the intent contract into the Engineer subagent's payload.
  - `verify_dqa_checklist_hook.py`: Blocks DQA reports unless all Markdown TO-DOs `[ ]` are ticked `[x]`.
- **Socratic Challenger Upgrade**: `/grill-me` via `socratic_challenger.py` now supports automated codebase scanning to evaluate technical feasibility.
- **Strict Path Standardization**: Harmonized all lesson learnt registries to use `.agents/lessons_learned/DIGEST.md`.

## [v1.0.0] - 2026-07-21

### 🚀 Added
- **Multi-Agent Sandbox Framework**: Integrated `Engineer`, `Architect`, `TDD_DQA`, and `SDD_DQA` as native subagents governed by a central PM structure.
- **Defense-in-Depth Architecture**:
  - `path_guard.py`: Added to physically isolate and lock subagents in `src/` and `tests/`.
  - `agent_shield_hook.py`: Added to scan commits for destructive commands and leaked secrets.
  - `phase_gate_hook.py`: Enforces strict milestone transitions requiring CEO approval.
- **Claude External Orchestrator**: Safely delegate coding tasks to Claude Code CLI with mandatory Dual-DQA (Claude DQA + Native DQA) reviews.
- **Lesson Maintainer**: Automated module for deduplicating, archiving, and promoting AI experiences into global architectural rules.
- **Team Constitution**: Built-in global rules ensuring consistent Traditional Chinese outputs and folder hygiene.
- **Open Source Readiness**: Added `LICENSE`, `CONTRIBUTING.md`, and this `CHANGELOG.md` file.

### 🛡️ Security
- Patched path traversal vulnerabilities in `agent_shield_hook.py` by converting to relative path verification.
- Enforced Sandbox constraints on external Claude delegates, preventing root directory pollution.
