# 📝 更新日誌 (Changelog)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.0.0] - 2026-07-23

### 🚀 Added & Refactored
- **Native Antigravity Hooks Architecture**:
  - Integrated 8 native hooks (`SessionStart`, `BeforeTool`, `AfterTool`) defined in `hooks.json`.
  - Added `lock_guard_hook.py` (BeforeTool): Enforces token-based phase lock verification for `.current_phase.lock`.
  - Added `check_model_matrix_hook.py` (SessionStart): Prompts PM if model recommendation matrix is missing.
  - Added `dqa_test_limit_hook.py` (AfterTool): Controls DQA test item limits (Phase 3 <= 30 items with 1-time PM review allowance, Phase 4 <= 50 items with 2-time PM review allowance).
- **Skills-to-Tickets & Vertical Slicing Enforcement**:
  - Phase 2 DQA pre-view audit enforces end-to-end Vertical Slicing (data + logic + UI) and bans Horizontal Slicing anti-patterns.
  - Phase 2 Composite Milestone Hierarchy: Automatically groups small milestones into Milestone Groups (M1.1, M1.2...) for complex projects (>=5 milestones).
- **Three-Way Context Injection Payload & Conflict Escalation**:
  - Phase 3 injects Architect spec, Milestone PRD, and DQA specs into Engineer's payload.
  - Amend-Before-Dev Protocol: Forces PM/Architect/DQA to update specs before Engineer resumes work upon discovering contract conflicts.
  - Parallel Change Log Pipeline: PM generates fine-grained code change logs during Engineer coding windows for Phase 5 Architect verification.
- **Dual DQA Full-Product System Audit**:
  - Phase 4 invokes both `SDD_DQA` (Intent Audit) and `TDD_DQA` (Full-Product End-to-End System Testing) using Phase 2 reviewed PRD.
  - Code Truth Precedence Rule: Phase 5 Architect prioritizes actual `src/` source code over reports when generating as-built architecture snapshots.

## [v1.0.0] - 2026-07-21

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
