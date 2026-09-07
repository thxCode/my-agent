# Compaction checkpoint

Shared by `/my-plan`, `/my-debug`, `/my-build`, `/my-ship`, and `/my-crew` — whose case is the last section.
`/compact` is user-only **from inside a window**: you emit the block and ask, and the user runs it.

## When it fires

You can't read the token count **from inside the window** — a parent window watching a child can, see the last
section. Judge from proxies — **either signal is enough**:

- the context looks large (many/large files read, tool output piled up), or
- it feels fuzzy: losing track of state, re-reading things you already read, unsure which tasks are done.

Neither fires → skip and continue. Thresholds by command: `/my-build` ~>500K, `/my-ship` ~>250K.

## What to do

Emit one copyable block in **English** and ask the user to run it before continuing:

```
/compact <focus>
```

Then resume — every command in the family re-resolves its target from disk, so the work picks up cleanly from
Phase 1. The target file and git hold the state; the conversation doesn't need to.

`/my-build` is the strict case: when a signal fires with tasks still pending, require the compaction in **every**
run mode. A bloated or fuzzy context degrades every remaining task, and neither auto-chain nor team gets to skip it.

## Focus per command

| Command | Keeps | Drops |
| --- | --- | --- |
| `/my-plan` | target spec path; finalized Implementation Plan (tasks + acceptance) + Test Plan; reusable codebase landings (files / functions / patterns, with paths); flagged Risks → Mitigations; next step `/my-build <title>` | exploration and grep transcripts; superseded drafts |
| `/my-debug` | artifact path; Root Cause; Fix Plan (tasks + acceptance) + Test Plan; reusable codebase landings (paths); next step `/my-build <title>` | verbose debugging transcripts |
| `/my-build` | target path; done (`[x]`) vs pending tasks; current branch; run mode; key decisions and patterns; open questions / risks | diffs and tool output of committed tasks — git holds them now |
| `/my-ship` | branch + target path (if any); base branch; ship mode; which finalization phases are done; key decisions / open questions | diffs and tool output of committed work |

## Handing off after a compaction

`/my-plan` and `/my-debug` end by offering the next step. When that offer is **compact, then build**, the block
is three lines in order — compact first, switch model second, then build:

```
/compact <focus>
/model opus
/my-build <title>
```

Switching right after compaction keeps the model-switch re-read minimal (prompt caches are per-model). Suggest
`/model sonnet` instead when the plan is fully specified and low-risk, or the fix is small and well-patterned.

## A parent window compacting a child window

For `/my-crew` and any fan-out. A worker cannot compact itself — `/compact` is user-only, and the worker can't
issue it — but `orca terminal send --enter` **writes into that window's input box**, so a parent can send both
`/compact` and `/clear`. Which one is not a preference:

⇒ **`/clear` + a resume file is strictly stronger than `/compact`: it moves the compressed result out of a
context nobody can inspect and onto disk, where the parent can read it.** A `/compact` focus stays inside the
child — the parent cannot see what survived, so nobody ever learns whether the compression was right. A resume
file is readable, checkable, and still there after `/clear`.

Three steps, in order:

1. **P0 message** (see `multi-window.md` §1): "stop what you're doing. Write your compaction focus to
   `<absolute path>/HANDOFF-<task>-resume.md` — header four questions, per `multi-window.md` §5 — then reply one
   line: `focus written`."
2. **Read that file and verify it. Never trust the reply.** Check: is the base SHA in it; are done vs. pending
   separable; is the next step one executable command. Anything missing → a second P0 to fill it.
3. **Send `/clear`, then send `read <path> and continue` as a separate message** — `/clear` discards whatever
   follows it in the same turn.

### The measurable trigger — the parent can read the child's transcript size

A parent reads it directly:

```bash
wc -c ~/.claude/projects/<cwd-slug>/<session-id>.jsonl
```

**Identify the child's transcript by a string only that window has seen** — the handoff path you sent it — never
by recency:

```bash
grep -l '<the handoff path you sent it>' ~/.claude/projects/<cwd-slug>/*.jsonl
```

`ls -t *.jsonl | head -1` gets you the **most recently active** session, and one cwd-slug directory holds dozens
(measured trap). Record the session id in `STATUS.md` at dispatch time and the lookup happens once.

**Calibrate before you trust a number, and don't copy one from anywhere** — including from here. The byte count
is real and monotone, but it is an **upper bound on context, not a measure of it**: the transcript accumulates
full tool output that was never in the context window and keeps everything an earlier compaction already dropped
(measured: a session at 813 KB of transcript whose live context was a fraction of that). One pairing calibrates
it — ask the child for its `/context` reading once, `wc -c` its transcript in the same minute, and write the
ratio into `STATUS.md`. Then a threshold like "half the window" becomes a byte count you can watch without
asking anyone.
