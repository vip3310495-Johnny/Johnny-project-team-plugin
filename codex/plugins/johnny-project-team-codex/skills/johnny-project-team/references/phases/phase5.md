# Phase 5: As-Built handover

PM converts the Phase 3 ledger and current system evidence into the final maintenance
record. Use `assets/templates/as-built-report.md`.

## Required contents

1. Final architecture and data-flow diagrams
2. Actual APIs, schemas, configuration, and external dependencies
3. Baseline-to-As-Built comparison using the Phase 3 change ledger
4. Critical routes, maintenance entry points, known limitations, and technical debt
5. Reproducible build, test, diagnostic, and recovery commands

Architect compares the report with the real system and samples critical routes.
Architect records discrepancies as Process/Documentation Defects. DQA does not
review the change ledger.

Phase 5 completes only after the commands have been exercised and Architect verifies
that the report describes the delivered system.
