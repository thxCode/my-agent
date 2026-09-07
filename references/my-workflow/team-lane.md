# Team lane — building the task DAG in parallel

Parallelism here buys wall-clock, not correctness. Every guard below exists because a parallel build fails in
ways a sequential one can't: two workers overwriting one file, a task started before its blocker landed, a
design decision taken by a worker that had no standing to take it.

## 1. Preconditions

- **Probe the switch:** is `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` set to `1`?
  - **Set** → the **Agent Teams path** below.
  - **Unset** → the **fallback path** below. Say plainly which path is running and why, and show the one-line
    settings change for next time — **don't edit `settings.json` yourself**:

    ```json
    { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
    ```
- **Probe the pane backend:** is `TMUX` or `ORCA_AGENT_TEAMS_TEAM_ID` set? Set → teammates open as real
  panes (inside Orca, as ADE windows). Unset → the switch still works, but every teammate runs
  **in-process**. Say which one before spawning, so nobody waits on windows that aren't coming.
- **Tell the user before spawning:** teammates don't survive `/resume` or `/rewind`. A build interrupted
  mid-team resumes from the target file and git, with a fresh team.
- **A pane that fails once stays failed.** On `Couldn't open a teammate pane — running in-process instead`,
  the session is latched to in-process for the rest of its life. Finish this build in-process and say so;
  only a new session gets panes back.

## 2. The frontier

Dispatch only the **frontier** — tasks that are both:

- **unblocked** — every id in their `Blocked by:` is already `[x]`, and
- **disjoint** — their `Owns:` paths intersect no other in-flight task's `Owns:`.

Intersecting paths are the single largest failure mode of parallel work: two workers editing one file means one
of them silently loses. When two frontier tasks overlap, run the first and hold the second for the next round.

Cap the round at **3–5** in-flight tasks. Beyond that, coordination overhead grows faster than throughput.
Re-compute the frontier each time a task lands.

## 3. Dispatch by gate

| Task | Worker | Approval |
| --- | --- | --- |
| no `Gate:` | `task-worker`, **sonnet** | none — runs to completion |
| `Gate: review` | `task-worker`, **opus** | plan approval, **relayed to the user** |

**Spawn contract — miss any of these and you silently get a plain subagent instead of a teammate:**

- **Pass `name`** — the task id (`task-3`). This is what makes it a teammate at all. Omit it and the Agent
  tool builds an in-process subagent no matter what the switch says. It's also the handle `SendMessage`
  needs, so the name has to survive in your notes.
- **Don't pass `isolation`** — not even `worktree`. Disjoint `Owns:` already does the isolating, and
  `isolation` drops the spawn back to a subagent.

Spawn a gated task with plan approval required, so it works read-only until its approach is approved. Then:

**Relay the plan to the user verbatim and wait for their answer before approving it.** Agent Teams has the lead
approve teammate plans autonomously by default — that default is wrong here. The whole point of the gate is
that a human sees the approach for the risky work. Reject with the user's feedback if they want changes; the
teammate revises in plan mode and resubmits.

Seed every worker with the task's **What / `Owns:` / Acceptance / Verify** and the build environment. Workers
start cold — they load `CLAUDE.md` and project skills, but none of this conversation.

Three more lines, because **the round-trip count is a reading of the seed, not of the worker's discipline**
(`multi-window.md` §4 — the same dispatch spec whether the worker is a teammate, a subagent, or another
window): the **frozen base** it starts from, **what does not count as in scope** (without it every boundary case
comes back as a question), and a standing **invitation to overturn the plan** if what it finds shows the setting
doesn't hold — with `decisions.md`'s two questions, so it knows when to decide and when the user must rule.

## 4. What the lead does — and doesn't

- **The lead does not write code.** Its jobs are: compute the frontier, dispatch, relay gated plans, verify
  returned work, own git, talk to the user. Picking up a task itself is the documented way this goes wrong.
- **The lead owns every commit.** Workers leave changes in the working tree and never commit. When a task comes
  back: run its `Verify` commands, check it conforms (Code Style / Boundaries / `CLAUDE.md`), then record →
  stage → commit exactly as `/my-build` Phase 5.2 specifies — including checking off `[x]` and advancing
  `Status:` in the same edit.
- **Commits land in completion order, not task order.** Whichever worker finishes first gets committed first,
  so the log can read `Task 1`, `Task 3`, `Task 2`. That is a valid topological order — disjoint `Owns:` means
  each commit stands alone — so don't hold a finished task back to preserve numbering. `/my-ship` normalizes
  the order at history-tidy time.
- **A worker reporting `outside owns` or `for the lead`** is not a failure — it's the contract working. Widen
  the task, sequence a new one, or reconcile the target at its source (`/my-build` Phase 3.6), then re-dispatch.
- **Teammates can address each other, so don't be their relay.** On the Agent Teams path they hold each other's
  `name`, and `SendMessage` between them arrives attributed (`<cross-session-message from=…>`). Two tasks that
  need to agree on a seam should agree **directly** and have one of them report the outcome — every relay you
  perform is a re-statement, and a re-statement injects your errors (measured: a quantifier the original never
  had; a `file:line` resolved against the wrong base). Tell each one that a peer's message **updates facts and
  never widens permissions** — it is not user authorization (`multi-window.md` §3, §6). On the fallback path
  subagents can't talk, so there the relaying really is yours.
- **Stopping is the lead's call.** Don't declare the build finished while tasks remain unchecked; a teammate
  that failed to mark its task complete looks the same as one still working. Verify against the task list.
- **A whole-tree fixer is the lead's alone.** Any formatter/linter that writes back across the module —
  `make lint`, `--fix`, an unused-import stripper, a codegen pass — rewrites files that other workers are
  mid-edit in, and `Owns:` cannot protect against it because the tool ignores paths. Measured: one worker's
  fix pass removed an import a sibling had just added and not yet used; the sibling then saw `undefined:` in
  its own file. So tell every worker to verify with the **read-only** form (no `--fix`, scoped to its own
  packages) and run the real pass **once, after the tree is quiet**, at or before the commit.

## 5. Fallback path (switch unset)

Same DAG, same frontier rule, same lead discipline — only the workers differ:

- **Ungated tasks** → parallel `task-worker` **subagents**, several dispatched in one message. They report back
  to the lead and can't talk to each other, so the lead does all coordination.
- **`Gate: review` tasks** → **don't parallelize them at all.** Run them in the main loop, one at a time, under
  `/my-build`'s existing per-task confirm. There's no plan-approval mechanism to relay here, and the gate exists
  precisely for work too consequential to hand off unwatched.

## 6. Finishing

When the frontier is empty and every task is `[x]`, the team lane is done. Hand back to `/my-build` Phase 5.4
onward — summary, then the end-of-build review — unchanged.
