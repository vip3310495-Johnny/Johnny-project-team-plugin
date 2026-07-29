# Johnny Project Rules

Before handling a Phase or Milestone:

1. Run `johnny_project_hooks.py status` and verify the current Phase.
2. Read `.agents/context-manifest.json`, the active Task Context Pack, and only
   the routed role and technology references.
3. Work on one `codex/milestone-Mxx` branch and one ticket/milestone pair.
4. Bind TDD, SDD, and optional Claude evidence to the same product subject tree.
5. Read the Phase 2 execution policy. SUPERVISED requires per-Milestone CEO
   approval; AUTONOMOUS uses the recorded Phase 2 delegation after DQA PASS.
6. Return DQA FAIL attempts 1–4 to Engineer. On the fifth FAIL by one DQA role
   for the same Milestone, freeze it and request explicit CEO resolution.
7. Ask the CEO with plain-language consequences and 2–3 concrete options when
   a decision, installation, permission, cost, or irreversible action is needed.

Do not overwrite a repository's `AGENTS.md`. If durable startup routing is
needed, add an explicit link from that file to this file with repository-owner
approval.
