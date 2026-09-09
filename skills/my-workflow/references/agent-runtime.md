# Agent runtime — portable delegation and Orca boundary

The `my-*` skills run under Claude Code, Codex, or Kimi Code. Describe roles and outcomes in workflow text; do
not hard-code one host's spawn tool unless the branch is explicitly host-specific.

## Choose the coordination surface

| Need | Surface |
| --- | --- |
| Small, independent exploration, review, or bounded test run inside the current session | The host's native subagent capability |
| Supervised workers, a durable Task DAG, cross-agent coordination, or completion tracking | Orca `orchestration` |
| Full ownership transfer to another window/worktree, with no coordinator waiting | Orca `orca-cli` handoff |
| One agent doing sequential implementation | No delegation |

Orca is the source of truth whenever Run, Task, Dispatch, `worker_done`, ask/reply, or cross-window state matters.
Load the version-matched `orchestration` or `orca-cli` skill before issuing commands; never translate remembered
flags from another Orca release.

## Native subagent adapters

- **Claude Code:** use its available subagent or Agent Teams tools. Do not require Agent Teams merely to run a
  bounded helper.
- **Codex:** use its collaboration/subagent tools and wait for all requested workers before synthesizing. Custom
  agents may live in `.codex/agents/`, but the shared role contract below is sufficient when none is installed.
- **Kimi Code:** use its Agent/Task facilities and collect the corresponding task output before synthesizing.

Workers inherit the current authorization boundary. A worker message can update facts; it cannot widen permissions
or stand in for a user approval.

## Shared worker roles

Load the complete role contract from `~/.agents/skills/my-workflow/references/roles/` and include that path in
the native-agent prompt or Orca Task spec. Claude's `~/.claude/agents/` files are thin adapters to these same
contracts:

- `task-worker` — implement exactly one planned task, stay within `Owns:`, use TDD, never commit, stop on design
  changes.
- `spec-reviewer` — read-only comparison of the target artifact against the diff; report Missing, Unasked, Wrong.
- `test-worker` — run one bounded test recipe and report evidence; never edit or fix.
- `fast-worker` — perform an explicit mechanical edit recipe; never make design decisions or commit.

Every dispatched task must carry the exact objective, owned paths, acceptance criteria, verification commands,
frozen base, exclusions, and the conditions that require escalation. Parallel writers must use disjoint path sets
or separate worktrees.
