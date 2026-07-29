# Johnny global rules

1. Treat `.johnny/state.json`, `.johnny/config.json`, and the active Task
   Context Pack as the source of workflow state; never infer state from memory.
2. Record DQA only through `johnny_dqa_record.py`; no lifecycle or Git hook may
   create PASS.
3. Bind reviews to configured product `subject_tree` and full staged
   `commit_tree`; a product change invalidates prior PASS results.
4. Use a `codex/milestone-Mxx` branch for Phase 3. Protect `feature/*` and
   `main` from direct edits, commits, and pushes.
5. Read `references/script-catalog.md` before running bundled code and never use
   `experimental/` output as workflow evidence.
