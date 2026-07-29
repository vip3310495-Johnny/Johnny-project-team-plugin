# Phase 4: Final acceptance

DQA validates the completed house, not the Phase 3 paperwork.

## Ordered final-acceptance loop

1. PM freezes one final candidate staged tree and opens the `PHASE4-FINAL`
   review scope. Phase 3 ticket DQA evidence cannot satisfy this gate.
2. TDD DQA runs integrated behavior, regression, compatibility, security, and
   critical failure-path tests across the completed system.
3. Record TDD only for the final scope:
   `python scripts/johnny_dqa_record.py --project <repo> --scope phase4 --ticket PHASE4-FINAL --role tdd --result PASS|FAIL --evidence "<evidence>"`.
4. Only after TDD PASS for the same final scope and staged tree, SDD DQA validates
   the whole system against the PRD, architecture, FIXED intent, tolerances, and
   non-goals.
5. Record SDD with the same command using `--role sdd`. The command refuses SDD
   before TDD. If either DQA fails and implementation changes, restart Phase 4
   from TDD because the prior tree-bound evidence is stale.
6. Run Claude DQA only when the user explicitly requests it, using
   `--scope phase4 --ticket PHASE4-FINAL`.
7. PM presents the final acceptance package to the user only after required TDD
   and SDD PASS results exist for the same final scope and staged tree.

## Required checks

- FIXED observable outcomes and tolerances
- Intent and non-goal alignment
- End-to-end behavior and regression coverage
- Backward compatibility of CONTROLLED surfaces
- Security and critical failure paths
- Claude DQA only when the user manually requests an external cross-check

DQA may delegate independent read-only test execution to at most two TE children
under `dqa-te-orchestration.md`. DQA owns the final verdict.

An unapproved FIXED deviation or compatibility failure is a Contract Violation.
A missing Change Notice is a Process/Documentation Defect and does not by itself
prove the product behavior is wrong.

Advance only when final integrated TDD DQA and then SDD DQA results pass for the
same `phase4` scope and staged tree and the user accepts the finished product.
A manually requested Claude DQA result joins the evidence package but is not
part of the default gate.
