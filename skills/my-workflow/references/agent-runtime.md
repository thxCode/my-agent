# Agent runtime — portable delegation and Orca boundary

The `my-*` skills run under Claude Code, Codex, Kimi Code, or Qwen Code. Describe roles and outcomes in
workflow text; do not hard-code one host's spawn tool unless the branch is explicitly host-specific.

## Choose the coordination surface

| Need | Surface |
| --- | --- |
| Small, independent exploration, review, or bounded test run inside the current session | The host's native subagent capability |
| Supervised workers, a durable Task DAG, cross-agent coordination, or completion tracking | Orca `orchestration` |
| Full ownership transfer to another window/worktree, with no coordinator waiting | Orca `orca-cli` handoff |
| One agent doing sequential implementation | No delegation |

Orca is the source of truth whenever Run, Task, Dispatch, `worker_done`, ask/reply, or cross-window state matters.
Load the version-matched `orchestration` or `orca-cli` skill before issuing commands; never translate remembered
flags from another Orca release. Orca windows may host any CLI agent its launchers configure — claude, codex,
kimi, qwen — and the guide's low-level topology path covers argv the launcher cannot express, such as qwen's
unattended `--yolo`. An unattended worker must run in its provider's unattended approval mode, or it stalls on
the first approval prompt.

## Detect the Orca host

`my-crew`, `my-handoff`, and the team lane all require an Orca-hosted session. Read that from the environment,
never from an `orca` executable being present — outside Orca's terminals that name may resolve to something
else entirely, so a binary on `PATH` proves nothing:

- `TERM_PROGRAM=Orca`, together with `ORCA_WORKTREE_ID` and `ORCA_TERMINAL_HANDLE`, means this session is
  Orca-hosted. `ORCA_TERMINAL_HANDLE` is this window's own handle.
- `ORCA_APP_VERSION` is the running Orca version; use it to confirm a retrieved guide matches the runtime.
- `ORCA_AGENT_TEAMS_*` means Orca is brokering the host's native team facility — see `team-lane.md`.
- Any of the first three missing → not Orca-hosted. Report which signal is absent and stop, rather than
  substituting a host-native subagent and calling it Orca.

Resolve the executable separately, as the `orca-cli` and `orchestration` skills require. These variable names
belong to Orca, so treat them as a host signal only: command syntax still comes from the version-matched guide.

## Native subagent adapters

- **Claude Code:** use its available subagent or Agent Teams tools. Do not require Agent Teams merely to run a
  bounded helper.
- **Codex:** use its collaboration/subagent tools and wait for all requested workers before synthesizing. Custom
  agents may live in `.codex/agents/`, but the shared role contract below is sufficient when none is installed.
- **Kimi Code:** use its Agent/Task facilities and collect the corresponding task output before synthesizing.
- **Qwen Code:** use its Agent/Teams facilities and collect the corresponding task output before synthesizing.

Workers inherit the current authorization boundary. A worker message can update facts; it cannot widen permissions
or stand in for a user approval.

## Reclaim every worker

Dispatching is half a transaction. Before spending the first token on a worker, know both halves: how its result
reaches this session, and how the worker itself terminates. Either half unknown REQUIRES a different route — a
worker you cannot collect from is an expensive way to learn nothing, and one you cannot stop outlives its work.

Whether a worker retires on its own is a property of the host mode, not of the task:

- A one-shot subagent ends when it returns. Confirm that rather than assume it; the same definition spawns
  differently once the host's team facility is enabled.
- Under a persistent team facility, a worker stays resident after its round so the lead can keep talking to it. It
  NEVER retires on its own — the lead stops it explicitly, or it idles until the parent session ends.
- A dispatch-only integration, whose contract forbids it to poll, fetch results, or cancel, has no second turn by
  construction. Its reply is a receipt, not a result. Stop it as soon as the receipt lands, then read the result
  from wherever that integration persists its jobs.

A stage ends only when no worker it started is still running. "The result is in hand" is half the test; the other
half is that the host's agent listing is clean. Check both — the first one passing is exactly what stops anything
from checking the second.

Before signalling a process, read its pid from the state file its own runtime writes. NEVER infer ownership from
working directory plus start time: one machine may run several at once, some belonging to another session, and a
wrong guess kills somebody else's live work.

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
