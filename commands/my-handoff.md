---
name: my-handoff
description: Hand the current work to another agent in its own Orca window — packs the context into a handoff file, opens the window, delivers, and stops. Requires an Orca-hosted session.
argument-hint: "[task brief] [--to codex|kimi|claude|opencode] [--here|--tab|--worktree] [--watch]"
---

# /my-handoff

Hand off to another agent: **$ARGUMENTS**

A **full handoff** — ownership transfers and this session stops working the task. Not a cross-check:
`crosscheck` governs read-only second opinions where **Claude keeps every edit**; here the other agent
owns the code and you don't review its output. Naming the target is an explicit choice, so no quota gate
applies.

**Want to know when they finish, or to route their next task? That's `/my-crew`** — supervision needs a
Run/Task/Dispatch lifecycle, and creating one here would leave obligations nobody owns. Naming a model or
effort (`gpt-5.5`, `xhigh`) does *not* make a handoff supervised.

Nothing in the `my-*` build family calls this. It fires only when you type it.

- **Language.** Write the handoff file in the **session's configured language** — the same one you talk to the
  user in. The receiving window is configured the same way, and the file is a transcription of judgments already
  made in that language, so translating it inserts a distortion step for nobody's benefit. (Project artifacts
  are the other case: code, comments, commits, specs and docs still follow the project's conventions.)
- **Never guess `orca` flags.** They move between releases. Phase 4 loads the version-matched guide first.
- **Cross-window mechanics** — `~/.claude/references/my-workflow/multi-window.md`: the channels and how each one
  fails, and why every message must say who is speaking.

## 1. Probe the host

Is `ORCA_TERMINAL_HANDLE` set (and `ORCA_WORKTREE_ID` for the worktree address)?

- **Set** → continue. Confirm the runtime is up with `orca status --json`; if it isn't, `orca open --json`.
- **Unset** → **stop.** Say plainly that this session isn't running inside an Orca window, so there is no
  window to open. Offer the in-session alternative — `codex:codex-rescue` / `kimi:kimi-rescue` subagents,
  which are read-only and governed by `crosscheck` — and let the user pick. Don't fall back silently:
  a subagent is a different thing from a handoff, and the user asked for a handoff.

Resolve the executable per the `orca-cli` skill (`ORCA_CLI_COMMAND` → `orca-dev` → `orca-ide` → `orca`)
and reuse that one for every later command.

## 2. Target and placement

- **`--to`** — `codex` | `kimi` | `claude` | `opencode`. Not given → ask; don't assume.
- **`--here`** (default) — the **current checkout**, **split beside this window**
  (`terminal split --direction vertical` — `horizontal` stacks it *below* instead), so you can watch it
  work. Right when the work continues where you left off and the two agents won't collide on files.
  - **`--tab`** — same checkout, its own tab instead of a split. Right for something long you're handing
    off and *not* watching, or when this window is already too narrow to halve.
- **`--worktree`** — an **independent** worktree. Right when the task is a separate line of work, or when
  you'll keep editing here while they work.

**Start the agent non-interactively**, or the handoff stalls at its first approval prompt with nobody
watching: `codex --dangerously-bypass-approvals-and-sandbox`, `claude --dangerously-skip-permissions`,
`kimi --auto` (`--yolo` still asks questions).

Unlike `/my-crew`, nothing here needs to be *detectable* by Orca — you deliver text, not an injected
dispatch. So **any** agent can take a split, and the command carries whatever you write — env vars and
argv both: `KIMI_CODE_NO_AUTO_UPDATE=1 kimi --auto` works here and is impossible there.

## 3. Write the handoff file

`<cwd>/.claude/handoffs/<yyyy-mm-dd>-<slug>.md` — always local, never staged.

**The file isn't optional**, for two independent reasons. `terminal send` delivers into a TUI that submits on
newline, so a long brief gets truncated or fires early. And **a file is the only carrier every agent can read** —
Claude, Codex, Kimi and opencode share no message bus, so content that lives in a file survives a change of
target or channel untouched, while content living in a message has to be re-stated to move. What you send is one
short line pointing at this file; everything the other agent needs has to be *in* the file. It starts cold — no
CLAUDE.md of yours, no conversation, no idea what you already tried.

**Say who is speaking, inside the file.** Delivered into an input box, your line arrives as a **user turn** in
that session: the target cannot tell your judgment from the user's. So mark your own rulings as yours, and when
the brief relays a user instruction, carry its coordinates — the session transcript path plus `line=` / `type=`
/ `ts=` — because the receiver's check is the transcript, not your quotation marks (`multi-window.md` §3).

```markdown
# Handoff: <Title>

To: <agent> · From: Claude Code · <yyyy-mm-dd>
Worktree: <path> · Base: <sha the work starts from, and what may not move under it>

## Task
<What to do, in one paragraph. Concrete enough to start without asking anyone.>

## Background
<Why this is being done, what's already built, which approaches were tried and rejected — and why.
This is the part that can't be recovered from the repo.>

## Files
<Entry points and relevant paths with line numbers.>

## Acceptance
<Verifiable done criteria.>

## Boundaries
<What not to touch: paths, branches, whether it may commit or push.
And what does **not** count as in scope — the line that saves a round-trip per boundary case.>

## Verify
<The commands that prove it works.>
```

## 4. Load the Orca guide

```text
orca skills get orca-cli
```

Read **Full Handoffs** (and **Terminals** for `--here`). That guide is version-matched to the binary that
will run your commands — follow it rather than anything remembered from a previous session.

## 5. Confirm, then deliver

**Show the user the handoff file and the exact commands before running them.** Opening a window and
handing work to another agent spends someone else's quota and isn't undoable. Wait for a yes.

Then follow the guide: open the window (`--here` → split the active terminal; `--tab` → a terminal in the
active worktree; `--worktree` → an independent worktree with `--no-parent`), wait for TUI readiness, and
send **one line** — read `<handoff path>` and execute it.

**Then read the terminal back and confirm the prompt actually landed.** `send` returning
`accepted: true` means the bytes reached the PTY, not that the TUI took them — an agent CLI still
painting its banner drops them silently, and `wait --for tui-idle` reporting satisfied does **not** rule
that out (measured, not theoretical): it narrows the window, the read-back is what proves delivery. Read
**from the top** — `terminal read --terminal <h> --cursor 0 --limit 40` — because the default tail read
returns the blank last line of a full-screen TUI and reads exactly like a TUI that never painted. An empty
input box, or a "no session yet" line, means it was lost: **wait again and resend** — you delivered
free-form text, so sending it again is the whole fix (`/my-crew` must rebuild instead — its payload is a
dispatch bound to one attempt). Skip this check and a handoff looks delivered while nothing ever started.

## 6. Stop

Report the window/terminal handle and the handoff path, then **stop**.

**Nothing will tell you when they finish.** There is no callback into this session — the handle is the
only way back in, and only if someone goes looking. Say that plainly, so nobody sits waiting on a
notification that isn't coming.

A full handoff doesn't monitor:
per the Orca guide, `orchestration task-create` / `dispatch --inject` / `check --wait` are for supervised
coordination and record coordinator-owned state that nobody here owns.

⛔ **And `orchestration send` is not a back channel to a handed-off agent.** It is inbox mail delivered on
that agent's **next** `orchestration check` — a call a handoff target has no reason to ever make, since it
holds no Dispatch. So a follow-up sent this way is **queued and never read** — it sits in
`orchestration inbox` until someone goes looking. If you need to add or correct something after handing
off, **deliver it the same way you delivered the brief**: append to the handoff file and `terminal send`
one line pointing at it, then read the terminal back to confirm it landed. (Inside `/my-crew`, `send`
works only while a worker is still inside its dispatch lifecycle — see
`~/.claude/references/my-workflow/settled-worker.md`.)

**`--watch`** means supervision was wanted after all — that's **`/my-crew`**, which owns the Run and the
completion loop. Say so and switch commands; don't half-build monitoring here.
