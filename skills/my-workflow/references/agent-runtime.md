# Agent runtime — portable delegation and Orca boundary

The `my-*` skills use the current CLI host's capabilities. Installation and discovery differences live in
[host-adapters.md](host-adapters.md). Describe roles and outcomes in workflow text; do not hard-code one
host's spawn tool unless the branch is explicitly host-specific.

## Choose the coordination surface

| Need | Surface |
| --- | --- |
| Small, independent exploration, review, or bounded test run inside the current session | The host's native subagent capability |
| Adversarial review when Orca orchestration is reachable | `my-crew` supervised read-only window |
| Adversarial review otherwise | `my-crew` using the current host's native read-only subagent |
| Supervised workers, a durable Task DAG, cross-agent coordination, or completion tracking | Orca `orchestration` |
| Full ownership transfer to another window/worktree, with no coordinator waiting | Orca `orca-cli` handoff |
| One agent doing sequential implementation | No delegation |

Orca is the source of truth whenever Run, Task, Dispatch, `worker_done`, ask/reply, or cross-window state matters.
Load the version-matched `orchestration` or `orca-cli` skill before issuing commands; never translate remembered
flags from another Orca release. Orca windows may host any CLI agent the installed launchers configure.

## MiniMax Code workers

Orca does not auto-detect `mcode`. Use the live guide's custom launch path to start `mcode`. Other agents use
the live Orca guide's standard launch flow.

`mcode` buffers multi-line paste input as an unsubmitted draft (`Long draft · Enter send`). In bracketed paste
mode, a trailing Enter in `orca terminal send --text ... --enter` can be absorbed into the draft buffer.

To ensure `mcode` starts its turn:

- Put detailed context into a file and send a single-line path pointer (`multi-window.md`). A single-line prompt
  does not trigger draft mode and submits reliably.
- For a fresh worker, pass the prompt directly on the command line: `--command 'mcode "<prompt>"'`.
- If you send multi-line text to an existing terminal, check the terminal with `terminal read`. If the text
  remains in the input box, send a standalone Enter: `orca terminal send --terminal <handle> --enter`.

## Worktree workspace trust gates

A newly created worktree changes the working directory. Both Kimi Code and Antigravity (`agy`) prompt for
folder trust in an unregistered directory:

- **Kimi Code:** prompts `Trust this folder?` with `Trust this folder` selected by default.
  Neither `kimi -y` nor `kimi --auto` bypasses this modal.
- **Antigravity (`agy`):** prompts `Do you trust the contents of this project?` with `Yes, I trust this folder`
  selected by default. `--dangerously-skip-permissions` does not bypass this prompt.
- **Orca:** does not auto-trust new worktree folders for launched CLIs.

When dispatching an agent in a fresh worktree, inspect the screen with `terminal read --screen`. If a trust
prompt appears, send a standalone Enter: `orca terminal send --terminal <handle> --enter`. Then wait for
readiness with `terminal wait --for tui-idle`.

## Detect the Orca host

Orca runs, `my-handoff`, and the team lane's Orca path require an Orca-hosted session. Read that from the environment,
never from an `orca` executable being present — outside Orca's terminals that name may resolve to something
else entirely, so a binary on `PATH` proves nothing:

- `TERM_PROGRAM=Orca`, together with `ORCA_WORKTREE_ID` and `ORCA_TERMINAL_HANDLE`, means this session is
  Orca-hosted. `ORCA_TERMINAL_HANDLE` is this window's own handle.
- `ORCA_APP_VERSION` is the running Orca version; use it to confirm a retrieved guide matches the runtime.
- `ORCA_AGENT_TEAMS_*` means Orca is brokering the host's native team facility — see `team-lane.md`.
- Any of the first three missing → not Orca-hosted. Use a native subagent only for a route that explicitly
  permits one, such as `my-crew`'s review lane; never call it Orca orchestration.

Resolve the executable separately, as the `orca-cli` and `orchestration` skills require. These variable names
belong to Orca, so treat them as a host signal only: command syntax still comes from the version-matched guide.

## Native subagent adapters

- **Claude Code:** use its available subagent or Agent Teams tools. Do not require Agent Teams merely to run a
  bounded helper.
- **Codex:** use its collaboration/subagent tools and wait for all requested workers before synthesizing. Custom
  agents may live in `~/.codex/agents/`, but the shared role contract below is sufficient when none is installed.
- **Kimi Code:** use its Agent/Task facilities and collect the corresponding task output before synthesizing.
- **Qwen Code:** use its Agent/Teams facilities and collect the corresponding task output before synthesizing.
- **OMP:** use its `task` agent facility and collect the task output before synthesizing. A named agent must be
  discoverable in OMP's task-agent catalog; its skill catalog is a separate discovery surface.
- **MiniMax Code (`mcode`):** use the native subagent tools exposed by the active runtime and collect their
  results before synthesizing. Verify that a requested named role is discoverable; shared skills do not
  install native roles. If the tools or required collection/termination controls are absent, report that
  limitation and use only a fallback the selected workflow permits.
- **ZCode (`zcode`):** use the active runtime's `Agent` tool. For background agents, collect results through
  `TaskOutput` and stop unfinished work through `TaskStop`. Verify these tools are exposed and the requested
  role is supported before dispatch; the shared skill catalog does not install native agent roles.
- **Antigravity (`agy`):** use `invoke_subagent` to dispatch named or defined subagents, communicate via
  `send_message`, and monitor or stop workers with `manage_subagents`. Subagents execute in the background
  with reactive wakeup; do not poll for completion. Verify named roles exist in `~/.agents/agents/` or declare
  custom roles via `define_subagent`.

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
the native-agent prompt or Orca Task spec. The files in `~/.agents/agents/` are thin adapters to these same contracts:

- `task-worker` — implement exactly one planned task, stay within `Owns:`, use TDD, never commit, stop on design
  changes.
- `spec-reviewer` — read-only comparison of the target artifact against the diff; report Missing, Unasked, Wrong.
- `test-worker` — run one bounded test recipe and report evidence; never edit or fix.
- `fast-worker` — perform an explicit mechanical edit recipe; never make design decisions or commit.

Every dispatched task must carry the exact objective, owned paths, acceptance criteria, verification commands,
frozen base, exclusions, and the conditions that require escalation. Parallel writers must use disjoint path sets
or separate worktrees.
