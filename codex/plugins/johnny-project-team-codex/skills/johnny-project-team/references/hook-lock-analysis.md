# Hook lock analysis

## Problems in the original implementation

1. Antigravity `BeforeTool`/`AfterTool` declarations are not Codex plugin hooks,
   so they do not form a physical lock in Codex.
2. The phase token and state file are written by different scripts without one
   atomic transaction. A leftover token can authorize an unrelated later write.
3. Global environment bypasses (`SKIP_PATH_GUARD`, `DQA_WRITE_SPECS`) are
   unscoped and unaudited.
4. Phase 0 writes are broadly allowed, which weakens the claimed physical lock.
5. Claude DQA previously checked for a CLI but did not execute it, then marked
   the review PASS.
6. A hook that invokes reviewers or mutates the files it validates can recurse,
   deadlock, or leave partially written state.
7. Overwriting root `AGENTS.md`, `.gitignore`, or global hook configuration can
   affect projects that did not opt in.

## Codex design

- Activation is per repository with `.johnny/enabled.json`.
- Git uses repository-local `core.hooksPath=.johnny/git-hooks`.
- Existing repository-local hooks path is saved and restored on disable.
- Existing project hooks are chained before the Johnny guard, so they remain
  effective while Johnny is enabled; either hook can block the operation.
- The pre-commit dispatcher is read-only and has a fixed order:
  activation -> state -> staged paths -> DQA.
- External reviewers never run in hooks.
- Phase changes use one short-lived OS lock and atomic `os.replace`.
- No lock is held while running Git, Claude, tests, or network operations.
- DQA evidence is bound to the staged Git tree, preventing stale approval.
- There is no environment-variable bypass. Recovery uses the explicit,
  auditable disable command, which preserves state and evidence.

## Remaining trade-off

Git hooks physically block commits, not arbitrary file writes. Codex currently
does not expose a supported plugin-level pre-write hook. Claiming otherwise
would create a false safety guarantee. The phase gate and repository-local Git
hook together protect workflow transitions and committed output without
changing unrelated repositories.
