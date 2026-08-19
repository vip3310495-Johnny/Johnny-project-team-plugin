# <Wave>_<Milestone>_TDD DQA Review — Cycle <N>

## Binding

- Stable ID:
- Review cycle:
- Branch／commit／subject tree:
- Engineer Handoff:
- ECC selection hash:
- Reviewer ID:

## Input integrity

- Ticket／PRD／Context Pack／Contract Matrix versions:
- TDD cycle and smoke evidence:
- Missing or conflicting input: None / details

## Test environment

- Environment／build／test data:
- Isolation and teardown evidence:
- Production credentials／data／endpoint used: NO
- Actual hardware（如有）：device／firmware／safety envelope／emergency stop／pre-post state
- Environment status: READY / BLOCKED_ENVIRONMENT

## Verification matrix

| Contract／behavior | Dimension | Command／steps | Expected | Actual | Evidence／hash | Result |
|---|---|---|---|---|---|---|
|  | Acceptance／Boundary／Failure／Regression／Compatibility |  |  |  |  | PASS / FAIL |

## Test credibility

- RED validity:
- Public interface／real boundary:
- Independent oracle:
- Mutation／negative proof that the test can fail:
- Coverage quality:

## Stress／monkey／resilience

- Selected mode and reason: Stress／Load／Soak / Monkey／Fuzz / Both
- Load model or random seed:
- Duration／iterations／resource limits／stop conditions:
- Result and evidence:

## Findings

| ID | Severity | Reproduction | Expected／actual | Evidence | Required correction |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Verdict

- Status: PASS / FAIL / BLOCKED_INPUT / BLOCKED_ENVIRONMENT
- Evidence path:
- Suggested SDD focus（PASS 時）：
