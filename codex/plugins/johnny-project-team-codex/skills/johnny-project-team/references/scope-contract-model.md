# Scope contract model

Use three constraint levels so requirements preserve intent without prescribing
unnecessary implementation details.

## FIXED

Use for product intent, non-goals, core user journeys, observable outcomes,
tolerances, security boundaries, and breaking external-contract changes.

Every FIXED item must state:

1. Intent
2. Observable outcome
3. Tolerance
4. Non-goals
5. Escalation trigger

Do not prescribe function names, class layouts, or step-by-step implementation
unless that mechanism is itself an essential requirement.

If a FIXED problem appears during Phase 3, Engineer must stop the affected feature
and dependency chain, notify PM immediately, and continue only unrelated work.
PM decides whether and how the contract changes.

## CONTROLLED

Use for backward-compatible API, schema, data-flow, configuration, and error-handling
changes inside the FIXED envelope.

Engineer may make the change without approval and must send PM a Change Notice.
PM appends it to the Phase 3 ledger. DQA and Architect do not approve the notice.
Per-ticket DQA and Phase 4 DQA objectively test backward compatibility.

## DISCRETIONARY

Use for internal implementation, naming, refactoring, test technique, and minor
presentation details that do not change FIXED outcomes or compatibility.

Engineer chooses freely. Record only details needed to understand or maintain the
finished system.

## Classification ownership

PM alone assigns the initial level before Phase 3. Any agent may raise one
evidence-backed classification challenge; PM makes the final decision.

## Defect metrics

Count as `Contract Violation`:

- unapproved deviation from FIXED;
- CONTROLLED change that fails compatibility tests;
- missed observable outcome or tolerance.

Count separately as `Process/Documentation Defect`:

- missing Engineer Change Notice;
- missing PM ledger entry;
- As-Built documentation that differs from the system.

Never count a valid DISCRETIONARY choice as a contract violation.

## Relationship to per-ticket DQA

The three scope levels remain active throughout Phase 3. They control change
authority; the DQA sequence controls verification:

- `FIXED`: Engineer must escalate a problem immediately. TDD verifies behavior
  and tolerances; SDD verifies intent and contract alignment.
- `CONTROLLED`: Engineer may make a backward-compatible change and must notify
  PM. TDD verifies compatibility; SDD verifies that the change stays inside the
  FIXED envelope. DQA does not approve the Change Notice.
- `DISCRETIONARY`: Engineer chooses the internal implementation. DQA may test
  its effects but may not fail it merely for preferring another valid approach.
