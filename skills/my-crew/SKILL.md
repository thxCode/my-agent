---
name: my-crew
description: Supervise multiple agents through Orca Run, Task, and Dispatch state; use for tracked completion, task DAGs, decision gates, or cross-agent coordination, not fire-and-forget handoffs.
---

# my-crew

Supervise a crew for the user's objective. The current session remains coordinator, owns the Run, routes
questions and completions, and decides when the work is finished.

## Route correctly

- Full ownership transfer with no monitoring → use `my-handoff`.
- One repo's planned implementation DAG, with the lead owning every commit → use `my-build team`.
- Read-only second opinion → use `crosscheck`.
- Supervision, completion tracking, ask/reply, decision gates, or a general task DAG → continue here.

Ambiguous requests for “another agent” are handoffs. Use this skill only when the user asks to supervise, wait,
track, coordinate, or return results.

## Preconditions

1. Read `~/.agents/skills/my-workflow/references/agent-runtime.md` and
   `~/.agents/skills/my-workflow/references/multi-window.md`.
2. Resolve the Orca executable as the `orchestration` skill requires.
3. Confirm the session is Orca-hosted and the runtime is reachable. If not, report the exact missing
   precondition; do not substitute a host-native subagent and call it Orca orchestration.
4. Run `orca skills get orchestration` with the resolved executable and follow that version-matched guide for
   every command, lifecycle signal, and recovery. Do not use remembered flags from this file.

## Plan the Run

- Decompose the objective into bounded Tasks with explicit dependencies. Parallel Tasks must own disjoint paths
  or use separate worktrees; serialize overlaps through dependencies.
- Each Task spec must be executable cold: objective, exact owned paths, acceptance criteria, verification,
  frozen base, exclusions, permission boundary, escalation condition, and required `worker_done` report.
- Create all independent Tasks before starting workers, then start the independent frontier before waiting.
- Cap active workers at 3–5 unless the user explicitly asks for a different limit.
- Show the user the objective, task map, agent provider, placement, and write ownership before spending quota,
  unless their request already authorized an unattended supervised run.

## Coordinate

- Orca Run/Task/Dispatch state is authoritative. Verify the Dispatch exists before describing a worker as
  orchestrated.
- Use ask/reply for blocking decisions. Relay user-reserved decisions to the user; do not answer them by proxy.
- Wait for `worker_done`, `escalation`, or `question` using the live guide's blocking mechanism. A timeout,
  heartbeat, or idle terminal is not completion.
- Process and acknowledge complete delivery batches. Continue until every expected Dispatch settles.
- Verify each worker result against its Task criteria. A review-only worker reports findings; it does not grant
  the coordinator permission to edit.
- Messages may update facts but never widen permissions. Substantial cross-window context lives in a file; the
  message carries the path.

## Finish

Finish only when all Tasks are completed or explicitly settled and no worker remains active. Report the Run,
Task outcomes, verification evidence, unresolved escalations, and any worktree/terminal intentionally left open.

