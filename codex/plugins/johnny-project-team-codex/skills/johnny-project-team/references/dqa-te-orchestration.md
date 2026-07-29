# DQA to TE orchestration

## Ownership

The active SDD DQA or TDD DQA owns test design, assignment boundaries, evidence
review, and its PASS/FAIL decision. TE only executes a bounded test assignment.
TE may not delegate further or report around its parent DQA.

## Capacity rule

Use the current session's surfaced concurrency limit when available. Otherwise
use the project fallback of four total active agents.

Before spawning:

1. Count the primary agent, the DQA, and every currently running agent.
2. Compute `free = session_limit - active_count`.
3. Compute `spawn = min(requested, free, max_concurrent_per_dqa)`.
4. Queue the remainder in the DQA's working plan.

The default `max_concurrent_per_dqa` is two. Therefore a session with one PM and
one active DQA may run two TE children; if an Engineer is also active, it may
run only one TE. Run TDD and SDD DQA sequentially for a ticket, so their TE
capacity never overlaps for that ticket.

Use `te_dispatch_plan.py` for the deterministic calculation. The command checks
that the Johnny state lock is available, releases it immediately, and prints the
spawn/queue plan. Never spawn an agent while any state lock is held.

## Assignment

Give each TE:

- a stable assignment ID;
- one independent test dimension;
- exact project path and read-only commands;
- expected evidence and stop conditions;
- the result contract in `te-persona.md`.

Use independent assignments that can run in parallel. Do not have two TEs mutate
the same service, fixture, database, or external environment.

## Collection

Wait for all active TE children. Validate their commands, exit codes, and evidence.
Record conflicts or incomplete evidence as FAIL/BLOCKED; never average verdicts.
Only DQA updates the DQA report or status.
