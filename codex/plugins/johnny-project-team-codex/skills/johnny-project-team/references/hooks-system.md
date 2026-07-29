# Johnny hooks system

The plugin bundles official Codex lifecycle configuration at
`hooks/hooks.json`. Codex loads it only when the plugin is enabled and the user
has reviewed and trusted the current hook definition.

## Lifecycle hooks

- `SessionStart` runs `johnny_session_context.py` to return concise Phase and
  context routing. It does not write state or claim the model read missing files.
- `SubagentStart` runs `johnny_subagent_context.py` to route only the relevant
  role and Task Context Pack.
- `PreToolUse` runs `johnny_tool_guard.py` for fast protected-branch checks.

Hook commands resolve the installation through `PLUGIN_ROOT`. They never assume
the plugin was copied into `.agents/skills/`.

## Repository Git hooks

`johnny_project_hooks.py enable` configures repository-local
`core.hooksPath=.johnny/git-hooks` and generates `pre-commit` plus `pre-push`.
Both call the same read-only `johnny_guard.py`. Existing custom Git hooks are
chained once, preserved, and restored on disable.

Every hook must remain short and deterministic. Hooks must not:

- invoke an LLM, reviewer, test suite, or network service;
- advance a Phase, create approval, or write DQA verdicts;
- generate project documentation;
- accept environment-variable bypasses.

Use the explicit commands in `references/script-catalog.md` for state-changing
or long-running behavior.
