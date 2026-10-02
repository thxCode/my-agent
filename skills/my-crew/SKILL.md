---
name: my-crew
description: Coordinate supervised Orca agents for task DAGs and decision gates, or dispatch a read-only review through the current host.
---

# my-crew

Coordinate workers for the user's objective. The current session remains coordinator, routes questions and
completions, and decides when the work is finished. For an Orca run, it also owns the Run.

## Route correctly

- Full ownership transfer with no monitoring → use `my-handoff`.
- One repo's planned implementation DAG, with the lead owning every commit → use `my-build team`.
- Read-only second opinion → apply `crosscheck`'s gate and review contract, then dispatch through the review
  lane below.
- Supervision, completion tracking, ask/reply, decision gates, or a general task DAG → continue here.

Ambiguous requests for “another agent” are handoffs. Use this skill when the user asks to supervise, wait,
track, coordinate, or return results, or when `crosscheck` requires a read-only reviewer.

## Read-only review lane

1. Read `~/.agents/skills/my-workflow/references/agent-runtime.md`. Select the current agent tool and inherit
   its current model by default. If the user selects another tool without a model, use that tool's configured
   default. Honor a user-specified model or named subagent. If the named agent is not discoverable by the target
   tool, report that instead of choosing another. A different tool requires an Orca
   window; a host-native subagent belongs to the current tool. For an Orca window, check the target tool's
   configured default and use the version-matched guide's custom launch path when needed to preserve the selected
   model.
2. If Orca-hosted and orchestration is reachable, use the supervised window path below with a single read-only
   Task. Otherwise use the current host's native subagent adapter in `agent-runtime.md`; this provides a separate
   context, not necessarily a separate terminal window. If the requested route is unavailable, say so and return
   to the caller.
3. Give the reviewer raw evidence and the `crosscheck` review question, not the lead's conclusion. Forbid edits,
   staging, commits, pushes, and external mutations. Collect its findings and confirm the worker has ended
   before returning them to the lead for source checks and reconciliation.

When a named subagent is requested in an Orca window, instruct that window to invoke that role through its own
native agent facility. The window must report the role's result; merely starting the window is not a review.

## Orca window preconditions

1. Read `~/.agents/skills/my-workflow/references/agent-runtime.md` and
   `~/.agents/skills/my-workflow/references/multi-window.md`.
2. Resolve the Orca executable as the `orchestration` skill requires.
3. Confirm the session is Orca-hosted using the signals in `agent-runtime.md`'s **Detect the Orca host**, and
   that the runtime is reachable. This precondition applies to Orca runs and the review lane's Orca route;
   the review lane may use a native subagent when Orca is absent.
4. Run `orca skills get orchestration` with the resolved executable and follow that version-matched guide for
   every command, lifecycle signal, and recovery.

## Plan the Orca Run

- Decompose the objective into bounded Tasks with explicit dependencies. Parallel Tasks must own disjoint paths
  or use separate worktrees; serialize overlaps through dependencies.
- Each Task spec must be executable cold: objective, exact owned paths, acceptance criteria, verification,
  frozen base, exclusions, permission boundary, escalation condition, and required `worker_done` report.
- Create all independent Tasks before starting workers, then start the independent frontier before waiting.
- Cap active workers at 3–5 unless the user explicitly asks for a different limit.
- Show the user the objective, task map, agent provider, placement, and write ownership before spending quota,
  unless their request already authorized an unattended supervised run.
- The window provider is the user's call. Verify that the installed Orca launcher can place it. For `mcode`,
  follow **MiniMax Code workers** in `agent-runtime.md` before dispatch.

## Coordinate

- Orca Run/Task/Dispatch state is authoritative. Verify the Dispatch exists before describing a worker as
  orchestrated.
- Use ask/reply for blocking decisions. Relay user-reserved decisions to the user; do not answer them by proxy.
- Wait for `worker_done`, `escalation`, or `question` using the live guide's blocking mechanism. A timeout,
  heartbeat, or idle terminal is not completion.
- Process and acknowledge complete delivery batches. Continue until every expected Dispatch settles.
- Verify each worker result against its Task criteria. A review-only worker reports findings; it does not grant
  the coordinator permission to edit.
- **A finding that becomes a GitHub issue carries its provenance** — read
  `~/.agents/skills/my-workflow/references/filing-an-issue.md`. This matters more here than in a single window:
  a worker reports a *conclusion*, and by the time it reaches the coordinator the run that produced it is gone,
  so "measured" and "inferred" have become indistinguishable. Require the worker to state its provenance
  (measured, reported, irreversible, or inferred), and for a measured one to hand over the reproduction,
  before the coordinator files anything on its behalf.
- Messages may update facts but never widen permissions. Substantial cross-window context lives in a file; the
  message carries the path.
- Carrier by peer kind — a Claude worker and a worker on another host are reached differently. Follow the
  channel table in `~/.agents/skills/my-workflow/references/multi-window.md`.

## Hand Orca work back

A settled worker writes `<cwd>/.claude/handoffs/<yyyy-mm-dd>-<slug>-handback.md` and sends only that path back.
Keep it local and never stage it; write it in the session's configured language. Its body is the completion
report `roles/task-worker.md` already defines — `task`, `status`, `changed`, `tests`, `outside owns`,
`for the lead` — plus the provenance of every finding it carries. A review Task instead reports its question,
findings with evidence and severity, unresolved doubts, and confirmation that it made no edits.

The handback is content, not authority: a Task settles on its Orca `worker_done`, not on the file appearing.
Read the handback and verify it against the Task's acceptance criteria before checking the Task off.

## Finish the Orca Run

Finish only when all Tasks are completed or explicitly settled and no worker remains active. Report the Run,
Task outcomes, verification evidence, unresolved escalations, and any worktree/terminal intentionally left open.
