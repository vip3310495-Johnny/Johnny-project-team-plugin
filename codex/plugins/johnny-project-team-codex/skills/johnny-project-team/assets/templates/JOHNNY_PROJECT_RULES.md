# Johnny Project Rules

<!-- johnny-project-contract-v3 -->

Before handling a Phase or Milestone:

1. Run `johnny_project_hooks.py status` and verify the current Phase.
2. Read `.agents/context-manifest.json` and the active Task Context Pack.
3. Run `johnny_ecc_rules.py` for the active product paths and read every
   returned common, language, and framework rule before writing or reviewing
   code. Re-run it when paths or technology change.
4. Work on one `codex/milestone-Mxx` branch and one ticket/milestone pair.
5. Bind TDD, SDD, and optional Claude evidence to the same product subject tree.
6. Read the Phase 2 execution policy. SUPERVISED requires per-Milestone CEO
   approval; AUTONOMOUS uses the recorded Phase 2 delegation after DQA PASS.
7. Return DQA FAIL attempts 1–4 to Engineer. On the fifth FAIL by one DQA role
   for the same Milestone, freeze it and request explicit CEO resolution.
8. Ask the CEO with plain-language consequences and 2–4 concrete options when
   a decision, installation, permission, cost, or irreversible action is needed.
9. Keep all product delivery under `src/`. Engineer owns permanent tests under
   `src/tests/`; Phase 3 commits contain only `src/**`.
10. TDD/SDD/Claude DQA may write only their matching `*/tool/`, report, and
    evidence folders. TE is read-only. Never stage these process artifacts in a
    product commit.

Do not overwrite a repository's `AGENTS.md`. If durable startup routing is
needed, add an explicit link from that file to this file with repository-owner
approval.
