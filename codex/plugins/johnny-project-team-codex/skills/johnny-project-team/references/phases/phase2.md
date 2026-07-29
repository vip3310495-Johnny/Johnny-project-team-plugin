# Phase 2: Construction contract

PM prepares the complete Phase 3 construction package.

## Required outcomes

- Small vertical milestones
- Exactly one tracer-bullet ticket per milestone, sharing the same stable ID
- Dependency ordering between ticket/milestone pairs
- Requirement-to-acceptance traceability
- Scope Contract Matrix using `FIXED`, `CONTROLLED`, and `DISCRETIONARY`
- FIXED items containing Intent, Observable Outcome, Tolerance, Non-goals, and
  Escalation Trigger
- Explicit compatibility expectations for CONTROLLED surfaces
- Testable acceptance examples without prescribing unnecessary implementation
- A CEO-selected Phase 3 execution policy

PM alone assigns the classifications. Any agent may submit one evidence-backed
challenge; PM decides. Do not use a team vote.

## Ticket construction

Apply the `/to-tickets` concept:

- Treat each ticket as one small milestone. Do not place multiple tickets inside
  one milestone and do not create a milestone without exactly one matching ticket.
- Give the pair one stable ID, such as `M03`, and use it in planning, DQA evidence,
  user review, the change ledger, and the As-Built report.
- Make every ticket/milestone an end-to-end vertical slice that produces a user-visible,
  demoable, or independently verifiable result.
- Size each ticket for one fresh agent context and one user review cycle.
- Declare only genuine blocking edges.
- Map every ticket one-to-one to its milestone and to the relevant Contract Matrix IDs.
- Express acceptance from the user's perspective; avoid stale file paths,
  code snippets, and layer-by-layer implementation instructions.
- Keep only one Phase 3 ticket active at a time.

Use `assets/templates/phase-contract-matrix.md` and
`assets/templates/tracer-ticket.md`. Present the numbered ticket/milestone pairs,
blockers, and end-to-end result to the user.

## Phase 3 execution policy

Before leaving Phase 2, PM explains and asks the CEO to select exactly one:

- `SUPERVISED`: after TDD and SDD PASS, PM presents every Milestone Review
  Package and waits for explicit CEO approval.
- `AUTONOMOUS`: the Phase 2 approval delegates Milestone approval to the
  workflow. After all required DQA roles PASS, the Milestone is recorded as
  approved from that delegation and the next dependency-ready Milestone may run.

AUTONOMOUS does not fabricate a new CEO message. Its audit source is
`phase2-ceo-delegation`. A DQA FAIL returns the same Milestone to Engineer and
automatic execution continues after correction. If the same DQA role rejects
the same Milestone five times, freeze it and submit the conflict and evidence to
CEO. Only an explicit CEO resolution reopens review.

Advance only after the CEO approves the construction package, granularity, and
policy:

`python scripts/johnny_phase_gate.py --project <repo> --to-phase 3 --execution-policy SUPERVISED|AUTONOMOUS --approval "<CEO approval and delegation text>"`
