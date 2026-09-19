---
name: my-handoff
description: Transfer complete ownership of work to an Orca agent or worktree.
---

# my-handoff

Hand the user's task to another agent and stop working it. This is ownership transfer, not a cross-check and not
a supervised crew.

## Route correctly

- If the user wants completion tracking, results returned here, a task DAG, or ask/reply, use `my-crew`.
- If the user wants a read-only second opinion while this session keeps ownership, use `crosscheck`.
- A named provider or model capability does not by itself make the handoff supervised.

## Preconditions and placement

1. Read `~/.agents/skills/my-workflow/references/agent-runtime.md` and
   `~/.agents/skills/my-workflow/references/multi-window.md`.
2. Resolve the Orca executable and confirm this is an Orca-hosted session using the signals in
   `agent-runtime.md`'s **Detect the Orca host**. Without an Orca terminal there is no target window to
   create; report that and stop rather than silently substituting a subagent.
3. Run `orca skills get orca-cli` with the resolved executable and follow its current **Full Handoffs** guide.
   Do not copy flags from this skill or memory.
4. Resolve the target agent from the user's request — claude, codex, kimi, or qwen; ask only if it is missing.
   The target runs in its provider's unattended approval mode (`qwen --yolo` or the provider's
   equivalent). Use the current checkout when ownership continues exactly where this session stopped, or a
   separate worktree when the tasks could overlap.

## Write the durable brief

Create `<cwd>/.claude/handoffs/<yyyy-mm-dd>-<slug>.md`, keep it local, and never stage it. Write it in the
session's configured language; project artifacts continue to follow project conventions.

The receiving agent starts cold. Include:

```markdown
# Handoff: <Title>

To: <agent> · From: <current agent> · <yyyy-mm-dd>
Worktree: <path> · Base: <sha and what may not move>

## Task
<Concrete work to perform.>

## Background
<Why, current state, and rejected approaches with reasons.>

## Files
<Relevant paths and entry points.>

## Acceptance
<Observable done criteria.>

## Boundaries
<Permissions, forbidden paths/actions, commit/push policy, and explicit exclusions.>

## Verify
<Commands or checks that prove completion.>
```

Mark coordinator judgments as such. A relayed user instruction must remain distinguishable from a coordinator
decision; no cross-window message can widen the user's authorization.

## Deliver and stop

- Show the brief and intended target/placement before spending another agent's quota unless the user already
  authorized the handoff.
- Use the version-matched Orca guide to create the target — the window does not exist yet, so Orca creates it
  whatever provider it runs. Then send one short instruction pointing to the brief, over the carrier the
  channel table in `multi-window.md` gives for that peer: a Claude target is reachable by Claude's attributed
  cross-session message, which is preferable because a raw terminal write reaches the target unattributed and
  reads there like a user turn.
- Read the target terminal back and confirm that the agent accepted the instruction; a successful PTY write alone
  is not proof.
- Report the target handle/worktree and brief path **to the user**, then stop. This skill has no coordinator to
  answer to and produces no handback: a handoff ends the reporting line, it does not loop it back. Do not
  create a Run, poll completion, or send orchestration mailbox messages to a worker that has no Dispatch.
- Later corrections use the same durable file-plus-pointer channel. If supervision becomes necessary, switch to
  a new `my-crew` workflow rather than retrofitting lifecycle state onto the handoff.
