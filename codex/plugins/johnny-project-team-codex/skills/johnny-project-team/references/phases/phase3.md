# Phase 3: Construction

Engineer implements the approved frame one tracer-bullet ticket/milestone at a
time. Do not add a 3A/3B phase gate and do not start multiple tickets in parallel.

## Ticket loop

1. PM selects one user-approved ticket/milestone pair whose blockers are complete.
2. Engineer implements only that pair's vertical slice and runs its acceptance checks.
   所有產品交付檔案都放在 `src/`：應用程式、`src/tests/` 永久自動測試、
   依賴／建置 manifest、runtime config、migration 與產品腳本。只 stage
   與 commit `src/**`。
3. TDD DQA verifies behavior, regressions, edge cases, compatibility, and
   reproducible test evidence for the same ticket and staged tree. A failure
   returns the same ticket to Engineer for correction, then review it again.
   TDD DQA 只能在 `TDD_DQA/tool/` 建立獨立工具；工具與 evidence 是本機
   流程產物，不得進入產品 commit。
   A FAIL does not stop AUTONOMOUS execution. Record the verdict with
   `scripts/johnny_dqa_record.py`.
4. After TDD DQA passes, SDD DQA checks the implementation against the ticket,
   Contract Matrix, user outcome, tolerance, and non-goals. A failure
   returns the same ticket to Engineer and invalidates prior DQA evidence after
   the implementation changes. Record the verdict with the same script using
   `--role sdd`; the command refuses to run before a TDD PASS.
   SDD DQA 只能在 `SDD_DQA/tool/` 建立獨立工具；TE 為唯讀，只能執行
   DQA 工具，不得建立或修改工具。適合永久回歸覆蓋的測試交給 Engineer
   納入 `src/tests/`。
5. If the user explicitly requests an external cross-check, run Claude DQA for
   the same ticket and staged tree. Claude DQA is otherwise skipped and cannot
   block the default flow.
6. After required DQA passes, PM prepares the Ticket Review Package:
   - observable result or demo;
   - acceptance criteria and actual result;
   - exact verification commands and evidence;
   - TDD DQA verdict and evidence;
   - SDD DQA verdict and evidence;
   - Claude DQA verdict when manually requested;
   - related Change Notice IDs;
   - known limitations.
7. Apply the Phase 2 execution policy:
   - `SUPERVISED`: PM presents that single result to the CEO and waits.
   - `AUTONOMOUS`: after committing the approved tree, run
     `johnny_milestone_gate.py` to record the Phase 2 delegation as approval.
8. Under SUPERVISED, if CEO rejects, revise and re-run both required DQA checks
   for the same ticket. Do not start another ticket.
9. Record approval with `johnny_milestone_gate.py`; SUPERVISED passes
   `--approval "<CEO approval>"`, while AUTONOMOUS omits it. Mark the
   ticket/milestone pair complete and unlock its dependents.
10. Repeat until every ticket/milestone pair is approved.

Ticket approval is a small milestone checkpoint, not a new project phase gate.

## Five-rejection conflict escalation

Maintain cumulative FAIL counts by stable Milestone ID and DQA role (`tdd`,
`sdd`, or optional `claude`). Attempts 1–4 return to Engineer and continue after
correction. On attempt 5 by the same role:

1. record the fifth FAIL and its evidence;
2. freeze that Milestone and affected dependency chain;
3. present the rejection history and conflict to CEO;
4. block further verdicts and Milestone approval until CEO resolves it.

Record the resolution with `johnny_dqa_record.py resolve-escalation`. This opens
a new review cycle and resets only that role's rejection counter. It does not
turn the fifth FAIL into PASS or bypass TDD→SDD ordering.

## Scope rules

- DQA does not co-design or modify the construction. TDD DQA and SDD DQA act as
  mandatory post-build, pre-user-review gates for every ticket.
- DQA 只能寫入其隔離的 tool、report 與 evidence workspace；不得修改
  `src/`，也不得在產品 commit 中 stage 流程產物。
- Follow FIXED outcomes and tolerances exactly. TDD verifies the observable
  behavior and tolerance; SDD verifies intent, boundaries, and specification fit.
- On a FIXED problem, notify PM immediately and freeze only the affected feature
  and dependency chain. Continue unrelated work.
- Make backward-compatible CONTROLLED changes autonomously and send PM a Change
  Notice immediately. TDD tests compatibility; SDD checks that the change remains
  inside the approved FIXED envelope. Neither DQA approves the Change Notice.
- Exercise discretion on DISCRETIONARY implementation details. DQA may test their
  effects but must not fail a ticket solely because it prefers another valid
  internal implementation.
- Submit one evidence-backed classification challenge when a level appears wrong;
  PM decides.

PM owns an append-only `PM/Phase3_Change_Ledger.md`. Recording a CONTROLLED change
is administrative, not a technical approval. Use
`assets/templates/phase3-change-ledger.md`.

At construction completion, Engineer hands off the approved ticket/milestone set,
built system, tests, known limitations, and reproducible commands to Phase 4.
DQA does not review the ledger.
