# Phase 4: Architecture deepening and brownfield baseline

Phase 4 does not repeat Phase 3 and is not a whole-product release acceptance.
Its purpose is to improve the internal architecture while preserving every
Phase 3-validated behavior, then document the delivered system for future
brownfield development.

## Entry: Architect review and CEO-approved plan

1. Freeze the Phase 3 baseline: commit, regression commands and results, public
   interfaces, critical user flows, data compatibility, FIXED contracts, and
   known limitations.
2. Architect must run the `improve-codebase-architecture` skill. The project
   does not assume a `CONTEXT.md` exists. Read available `AGENTS.md`, README,
   manifests, Phase 0-3 PRDs, Task Context Packs, ADRs, architecture artifacts,
   change logs, tests, Git history, recent diffs, public interfaces, schemas,
   migrations, and runtime configuration. Prioritize recent changes and hotspots,
   and use the `codebase-design` vocabulary: module, interface, implementation,
   depth, seam, adapter, leverage, and locality.
3. Persist the reconstructed scan context in
   `Architect/Phase4_Codebase_Context.md`, including evidence sources, module
   map, entry points, dependency direction, regression commands, unknowns, and
   confidence. A missing `CONTEXT.md` is not a blocker; missing source, tests,
   or Phase 3 regression evidence is.
4. Produce the skill's temporary HTML candidate report. Do not define a new
   interface or change code before CEO selects a candidate.
5. After selection, persist the actionable conclusion in
   `Architect/Phase4_Architecture_Review.md`, including evidence, current and
   target boundaries, preserved contracts, seams/adapters, migration order,
   risks, non-goals, validation, and rollback.
6. PM derives `PM/PRD/Phase4_PRD.md` only from the selected Architect conclusion.
   Split the work into `P4-Mxx` vertical-slice Milestones. Every slice must name
   its architectural target, end-to-end scope, preserved Phase 3 behaviors,
   TDD plan, SDD acceptance, dependencies, non-goals, and rollback.
7. At this point the project is already in the Phase 4 planning segment. CEO
   must explicitly approve the Architect review and Phase 4 PRD, then PM runs
   `johnny_phase4_start.py --evidence <phase4-plan-evidence.json> --approval
   "<CEO approval>"`. This does not change Phase; it unlocks Phase 4
   construction. Engineer must not modify product code before that record exists.

Every `P4-Mxx` must also have `PM/Milestones/P4-Mxx_PRD.md` created from
`assets/templates/milestone-prd.md`. Its Acceptance Criteria must map each
architectural slice and preserved Phase 3 behavior to steps, expected result,
tolerance, evidence command, and responsible DQA.

## Construction loop

Run each `P4-Mxx` through the Phase 3-style controlled loop on a
`codex/phase4-Mxx` branch:

1. PM publishes the Task Context Pack, the P4 Milestone PRD, Flow, and Data Flow.
2. Engineer follows `references/tdd-integration.md`; tests must protect both the
   slice contract and frozen Phase 3 behavior. After implementation and self-test,
   Engineer writes the review-cycle Handoff under `Engineer/` and submits its
   path, commit, and tree to PM instead of dispatching DQA directly.
3. PM validates the Engineer Handoff, then routes the fresh ticket-scoped tree
   to TDD DQA. The TDD review includes bounded stress/load/soak or monkey/fuzz
   resilience testing selected for the slice and follows the shared non-production
   environment and controlled-hardware rules. SDD DQA may run only after TDD PASS
   and reviews against the Phase 4 PRD, selected Architect
   direction, original Phase 3 contract, and actual UI/flows. Review UI by
   screenshot first; use OmniParser only when screenshot evidence is unclear.
4. REJECT starts a new review cycle. Old evidence cannot be reused.
5. Apply the Phase 2 SUPERVISED/AUTONOMOUS execution policy, record Milestone
   approval, and use the controlled PM merge.

Each Phase 4 Milestone has the same default 30-item DQA checklist limit as a
Phase 3 Milestone. An approved exception must not lower the validation standard.
Do not add features or perform a big-bang rewrite.

## Completion

After all `P4-Mxx` Milestones merge:

1. Re-run the complete frozen Phase 3 regression baseline. Any regression
   requires a new repair Milestone and fresh TDD -> SDD evidence.
2. Verify that public APIs, data formats, critical UI flows, and FIXED contracts
   contain no unauthorized behavior change.
3. Architect writes `Architect/As_Built_Architecture.md` from the delivered
   code. It must document system/module boundaries, dependency direction,
   interfaces, control/data flows, seams/adapters, integrations, error strategy,
   ADRs, constraints, test baseline, known risks, brownfield change guidance,
   and traceable Phase 4 before/after evidence.
4. PM creates completion evidence from
   `assets/templates/phase4-evidence.json`. The gate physically verifies that
   its approved Phase 4 plan lists exactly the completed `P4-Mxx` set, every
   listed Milestone exists in `.johnny/merge-history.jsonl`, regression evidence
   exists, no DQA escalation remains active, and `commit_tree` matches the
   current Git tree.
5. The gate also verifies that `Architect/As_Built_Architecture.md` exists,
   contains every required template section, and records `- Verdict: VERIFIED`.
   A filename alone is not completion evidence.
6. CEO approval plus valid evidence advances Phase 4 -> 5 through
   `johnny_phase_gate.py`; any failed physical check keeps the project in Phase 4.
