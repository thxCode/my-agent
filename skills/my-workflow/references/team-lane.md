# Team lane — building the task DAG in parallel

Parallelism buys wall-clock time, not correctness. Use this lane only when the task list declares both
`Blocked by:` and `Owns:`. The lead coordinates and owns git; workers implement one task each and never commit.

## 1. Choose the runtime

Read `agent-runtime.md`, then select in this order:

1. **Orca orchestration (preferred):** use when Orca is running and its orchestration feature is available.
   Load the version-matched `orchestration` skill, create or bind one Run, create all independent Tasks, and
   start every independent worker before waiting. Orca owns Task/Dispatch state and `worker_done` authority.
2. **Host-native team:** use the current host's native subagent capability when Orca is unavailable or the user
   explicitly wants in-session workers. State which host path is running. Claude, Codex, and Kimi use different
   spawn tools; preserve the contract rather than translating tool names.
3. **Sequential fallback:** if neither path can provide write-capable workers, offer ordinary `my-build`
   sequencing. Never pretend a sequential run is a team run.

Before spending agent quota, show the user the frontier, worker role, placement, and ownership boundaries. If
the user already authorized an unattended/team run, this is a status update rather than a new approval gate.

## 2. Compute the frontier

Dispatch only tasks that are both:

- **unblocked** — every id in `Blocked by:` is already `[x]`; and
- **disjoint** — their `Owns:` paths intersect no other in-flight task's paths.

Overlapping work is serialized through dependencies or isolated in separate worktrees. Cap one round at 3–5
workers and recompute the frontier whenever a task lands.

## 3. Dispatch contract

Use the `task-worker` role from `agent-runtime.md`. Every task starts cold and receives:

- what to build and the exact `Owns:` paths;
- acceptance criteria and verification commands, including the execution environment;
- frozen base SHA and anything that may not change underneath it;
- explicit exclusions;
- permission to overturn a bad implementation assumption, plus the decision/escalation test from
  `decisions.md`;
- the required completion report: changed files, tests, outside-ownership needs, and decisions refused.

For Orca, put this contract in the Task spec and use an injected Dispatch or the version-matched `worker-start`
flow. For a host-native worker, include the same contract in its prompt and wait for all workers in the round.

`Gate: review` means the worker remains read-only until the user approves its plan. If the chosen runtime cannot
relay a plan-approval gate, run that task sequentially in the lead session.

## 4. Lead responsibilities

- Do not write code while team workers are active. Compute the frontier, dispatch, answer escalations, verify
  returned work, and own every stage/commit action.
- Verify each result against its task before checking it off. Commit completed tasks in completion order; a valid
  topological order need not match task numbering.
- A request to edit outside `Owns:` is the contract working. Widen the task, create a dependent task, or reconcile
  the plan before redispatching.
- Run whole-tree rewriting tools only after all workers are quiet. Workers use read-only or path-scoped checks.
- Worker or coordinator messages may update facts but never widen user-granted permissions.
- Finish only when no worker is active and every task is `[x]`; then return to `my-build` Phase 5.4.

## 5. Messaging and waiting

Under Orca, use orchestration ask/reply and wait for `worker_done`, `escalation`, or `question`; acknowledge each
delivery according to the live guide. Under a native team, use that host's message/follow-up/wait primitives and
collect every worker result before synthesis. Do not poll with sleep loops, and do not infer completion from an
idle terminal or heartbeat.
