# A settled worker — what still reaches it, and what doesn't

Read when a `worker_done` has landed and you want that worker to do one more thing, or when a wait on a
worker that already reported is running long. `/my-crew` Phase 5 and Phase 6 point here.

A worker that reported `worker_done` **ended that turn.** It idles at its agent prompt — the process is
usually still alive, but its Dispatch lifecycle is over and it never calls `orchestration check` again.
That one fact decides everything below.

## `orchestration send` no longer reaches it

`orchestration send --to dispatch:<id>` is **structured inbox mail, not prompt injection.** A worker
receives it on its **next** `orchestration check` — a call this one will never make. So the follow-up
queues forever, retrievable with `orchestration inbox` but read by nobody, and **you will diagnose the
silence as "still working" and wait indefinitely.**

The tell: `worker-read --dispatch <id> --json` returns
`status: {"worker":"succeeded","terminal":"running","liveness":"live"}`. **`terminal: running` and
`liveness: live` do NOT mean an agent is listening** — the terminal is up, its dispatch lifecycle is over.

## Orca will not re-supervise that handle

`worker-start --terminal <handle>` fails twice, in this order:

1. `terminal_worktree_mismatch` — it infers `--worktree current`. Pass the terminal's own worktree as the
   full `id:<repo-id>::<path>` selector, exactly as the `/my-crew` Phase 4 rebuild does.
2. `agent_unconfigured: Terminal <handle> is not running a recognized agent` — Orca declining to supervise
   that terminal. **Not** proof the agent died.

## Look before you rebuild

`terminal read --terminal <h> --cursor 0 --limit 40` — from the top, for the reason Phase 4 gives: a tail
read of a full-screen TUI returns a blank last line either way.

### An idle agent prompt → send it directly

The agent is alive, and a direct instruction outranks its finished dispatch. `terminal send` the follow-up
and read it back, exactly as `/my-handoff` delivers a brief. You keep the agent's whole conversation
context.

The cost: that work is **user-owned, not dispatched** — no Task, no `worker_done`, and `/my-crew` Phase
7's `task-list` will never show it. Record the outcome yourself with `task-update`, and never reuse the
settled Dispatch's IDs.

### A shell prompt, or `command not found` → rebuild against a new Task

The agent really is gone. Go through the low-level path, so the launch carries its non-interactive argv:

```bash
orca orchestration task-create --spec "<the follow-up, restated in full>"
orca terminal create --worktree id:<full_worktree_id> --command '<agent> <non-interactive argv>'
orca terminal wait --terminal <new_handle> --for tui-idle --timeout-ms 180000
orca orchestration worker-start --task <new_task> \
    --worktree id:<full_worktree_id> --terminal <new_handle>
```

`worker-start --agent <x>` is shorter but carries no argv, so that agent stalls at its first approval
prompt. An existing worktree does **not** rerun setup, and the previous worker's files are still on disk.

You lose that agent's conversation context, so **the spec must restate the follow-up in full** — write it
as *"verify each item is applied; apply it if it is not"* so it is idempotent and does not redo landed
work.

## Prevention

If you know a follow-up round is coming, transfer the terminal **in the same breath as processing
`worker_done`** — `worker-start --task <next> --terminal <handle>` while the dispatch lifecycle is still
open. That is the only path that keeps both the agent and its supervision.
