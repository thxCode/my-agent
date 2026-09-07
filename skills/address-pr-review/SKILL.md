---
name: address-pr-review
description: "Read the review feedback already left on a pull request, triage each comment against the actual source (real bug vs. false positive), fix the real ones surgically, keep the git history clean by folding fixes into the right commit, and close the loop by replying to / resolving threads and updating the PR. This CONSUMES existing review comments and acts on them — it is the counterpart to skills that GENERATE a review (e.g. gitnexus-pr-review, /review). Examples: \"address the review comments on this PR\", \"the bot left review comments, fix the real ones\", \"how do I handle the feedback on PR #1\", \"apply the reviewer's suggestions and clean up the git log\", \"triage the Copilot review and reply to the wrong ones\"."
---

# Address PR review feedback

Take the review comments **already left** on a pull request and turn them into correct, minimal,
well-tracked changes. The hard part is not editing files — it is **deciding which comments are right**
and **landing the fixes without making the git history ugly**. Bot reviewers (Copilot, CodeRabbit, etc.)
produce confident-sounding comments that are sometimes wrong; never apply a comment without verifying it
against the source first.

## Workflow

### 1. Locate the PR

Resolve `owner` / `repo` and the PR number for the current branch:

```bash
git remote get-url origin          # parse <owner>/<repo> from this
git rev-parse --abbrev-ref HEAD    # current branch name
```

- If the user named a PR number, use it directly.
- Otherwise call `list_pull_requests` with `head: "<owner>:<branch>"`, `state: "open"` to find it.

Then read the PR and its CI state with `pull_request_read` (same `owner` / `repo` / `pullNumber`):
- `method: get` — title, state, reviewDecision, and `mergeableState` (step 6 picks the commit mode from it).
- `method: get_check_runs` (and `get_status`) — which CI checks are failing.

### 2. Read ALL three kinds of feedback

GitHub stores review feedback in three separate places. Looking at only one of them misses comments. All
three come from `pull_request_read` (same `owner` / `repo` / `pullNumber`):

- **① Top-level reviews** (`method: get_reviews`) — carries the state (APPROVED / CHANGES_REQUESTED /
  COMMENTED) and the summary body.
- **② Inline review comments** (`method: get_review_comments`) — the most actionable feedback, bound to a
  file + line. Returns review **threads** with `isResolved` / `isOutdated` **and each thread's node id
  (`PRRT_…`)** — the id a thread is resolved by.
- **③ Issue comments** (`method: get_comments`) — the PR conversation, not tied to any line.

**Page each of the three to exhaustion — they paginate independently, and 100 is a page size, not a
ceiling.** Ask for `perPage: 100`, then keep passing `after` while the response reports another page.
Stopping at the first page is the usual way comments go missing.

**④ And read the review *body* itself, not just the thread list.** Copilot folds low-confidence
findings into a `### Suppressed comments (N)` / `<details><summary>Suppressed comments</summary>`
block **inside** the review body: they create no thread, none of the three buckets returns them, and
`0 unresolved` cannot see them. They also accumulate across rounds — measured at 17 across 6 rounds on
one PR and 62 across 6 rounds on another. **Suppressed means low confidence, not low value**, so
triage each one exactly like an inline comment. A bot may also route findings into an issue comment or
leave them only in a CI run log, so the denominator is "what this bot emitted", never "what has a
thread".

State the count per bucket before triaging. Step 3's verdicts must add back up to those counts — that
sum is what makes a dropped page visible.

### 3. Triage — verify every comment against the source (the important step)

For each comment, **open the cited file/line and decide before touching anything**:

- **Real bug** → note the exact fix and which commit it belongs to.
- **False positive** → note why; you will reply on the PR instead of changing code.
- **Out of scope / opinion** → flag for the user, do not silently act.

Common false positives to watch for:
- Library-semantics claims (e.g. "this `merge`/`reduce` precedence is backwards") — confirm against the
  actual library docs/behavior; reversing a correct call *introduces* a bug.
- "This will crash on input X" — check whether input X is actually reachable / validated upstream.

While triaging, look for the **same root cause elsewhere** the reviewer missed (e.g. a rendering bug
flagged in two templates often exists in a third). Fix all instances for consistency, and say so.

Present a short triage table (id · location · verdict · action) before editing.

### 4. Fix the real issues — surgically

- Match the surrounding style and existing idioms (e.g. reuse a helper/pattern the file already uses).
- Touch only what the comment requires; no drive-by refactors.
- Add or adjust a focused test that locks in the fix, especially for logic bugs.

### 5. Verify

Run the project's own checks before committing — tests, linters, and a render/dry-run when the change is
in templates/manifests:

```bash
go test ./<pkg>/...            # or the repo's test command
<repo lint command>            # e.g. make lint
helm template ... | grep ...   # for chart/manifest changes, prove the rendered output is valid
```

**Re-run the project's code generation on every round it has one — the test suite is not that check.**
⛔ Don't gate this on "did I rebase this round": that is conversation state, unknowable after a resume or a
compaction, **and it has no tree-observable substitute** — a rebased branch and a merely-behind branch have the
same fork point, so any `first^` vs `merge-base` comparison returns equal in both cases (measured: it printed
`SAME` for both). Running the generator *is* the check, and it costs one command.

"The text merged cleanly" and "the generated output is still correct" are two independent facts. Measured: a PR
rebased onto a new base returned `EXIT=0` from `git merge-tree --write-tree` — no conflicts anywhere — while
re-running generation from the new HEAD drifted **four** files (a `.proto`, a CRD, an openapi doc, an
applyconfiguration). Nothing reports that: it is not a merge conflict, so the only gate that speaks up is CI's
generated-artifact check, and by then the PR is pushed.

```bash
make generate            # or whatever the repo's codegen target is
git status --porcelain   # must come back empty
```

And this is not a two-window problem: a plain single-window rebase produces the same drift.

### 6. Land the fixes — fixup by default, fold only when history is being rewritten anyway

One fact decides the mode: **does this round rewrite history regardless?**

| Signal | Mode |
| --- | --- |
| The user asked to rebase onto the latest base, or the branch was already rebased this round | **fold** |
| Step 1's `mergeableState` is `DIRTY` (conflicts) or `BEHIND` (a protection rule demands up-to-date) | **fold** |
| Otherwise — the norm, since this skill usually runs after `/my-ship` | **fixup** |

State which mode you picked and why before committing; the user can override.

Either mode needs the fix's owning commit: `git log --oneline <base>..HEAD`, then `git blame <file>` /
`git log --oneline -- <file>`.

**Resolve `<base>` freshly every time, and again after any rebase** — never reuse the ref from an earlier
command in this session. After a rebase the merge-base has moved: a stale one leaves `--autosquash` unable to
find its targets, or drags commits that aren't yours into the rewrite range.

```bash
git fetch origin <base-branch>
git merge-base HEAD FETCH_HEAD          # this round's <base>
git ls-remote origin <base-branch>      # the remote's actual tip
```

`refs/remotes/*` is a **cache, not the remote** — judge what the remote currently holds with `ls-remote` (or a
fresh fetch), never from a tracking ref that may be hours old.

**fixup — leave the fixups standing.** One per owning commit:

```bash
git commit --fixup=<target-sha> -- <files>
```

No rebase, so the push fast-forwards. An incremental reviewer (CodeRabbit, Copilot, GitHub's own
"changes since your last review") diffs against the commits it already saw — rewriting those throws the
baseline away and re-reviews the whole PR.

**fold — squash them in.** Interactive rebase prompts are unavailable in this harness, so drive it
non-interactively with a no-op sequence editor:

```bash
# branch is a single commit, or all fixes belong to the tip:
git add -A && git commit --amend --no-edit
# fixes belong to specific earlier commits:
git commit --fixup=<target-sha> -- <files>
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>
```

Avoid a noisy standalone "address review comments" commit unless the user wants the review trail in history.

### 7. Re-read, then reply and resolve — before pushing

**Re-read all three buckets first** — step 2's calls, paged to exhaustion again — and diff the result
against what you triaged. Fixing takes time, and the PR moved while you worked. Three things surface:

- **New comments** — a reviewer or bot added them since step 2. Triage them (step 3); if real, loop back
  through steps 4–6 before replying to anything.
- **Threads someone else already resolved** — leave them alone: no reply, no re-resolve.
- **Comments the first pass never saw** — it stopped a page short. Triage these too.

Then, two buckets, two behaviors:
- **Fixed** → reply explaining the fix, then **resolve** the thread.
- **Not fixed** (false positive, intentionally kept, or deferred) → reply with the reasoning and
  **leave the thread open** so a human reviewer sees it and decides. Never resolve what you did not change.

The re-read just handed you every thread's id (`PRRT_…`) and its comments — no extra lookup needed.

- **Reply:** `add_reply_to_pull_request_comment` with `commentId` (the comment's databaseId) and `body`.
- **Resolve** (only the fixed ones): `pull_request_review_write` with `method: resolve_thread` and
  `threadId` (the `PRRT_…` id).

Word each reply to the fix itself, not to a push that hasn't happened — if the push stops on remote-only
commits, the replies are still true.

**Scan every reply body for an accidental closing keyword before posting it.** GitHub closes on
`close|fix|resolve` co-occurring with `#N`, and **it does not read negation** — "does **not** close #12" closes
#12. The trap hunts exactly the replies this step produces, because "this does not fully fix #12" is both the
honest wording and the trigger:

```bash
grep -icE '(close[sd]?|fix(e[sd])?|resolve[sd]?)[[:space:]]+#[0-9]' <<<"$body"   # must print 0
```

Rephrase to a non-closing verb (`addresses #12`, `part of #12`) or drop the `#`; never rely on the negation.

Re-read the threads you touched and confirm the end state: fixed → resolved, not-fixed → open.

Two traps in that confirmation, both measured:

- ⛔ **`resolvedBy.login` cannot tell you *who* resolved a thread.** Anything done through `gh` runs on
  the user's credentials, so "the user clicked it" and "I clicked it" are the same value. Attribution
  can only come from **your own operation log**, and that log has to (a) discriminate — grep the
  **success output** (`OK resolved <tid>`), never the script text, since the resolve list and the
  leave-open list sit in the same file — and (b) survive: write it under `~`, never `/tmp` (measured:
  darwin cleared `/tmp` mid-session), because a compacted tool result is not on disk either.
- ⛔ **A thread's state and its own text contradict each other, in both directions.** A batch resolve
  erases the "leaving this open" reply you just wrote (the loop cannot read its own replies), and a
  silent fix leaves "real, and not yet fixed" standing on a correctly-resolved thread. The check is
  mechanical: compare `isResolved` against **your own last reply on that thread** — one pass finds
  both; looking at state alone, or text alone, finds neither. (Measured: 7 candidates on one PR, 5
  real.) **Discipline fails in front of a batch operation, because a batch is exactly where the
  discipline is not present.**

### 8. Push the fixes — confirm first

Replying first is deliberate: pushing marks the affected lines' comments as outdated, and GitHub collapses
outdated threads out of sight — a reply landing after that is far easier to miss.

Updating the PR is outward-facing: **confirm with the user before pushing**, and guard against clobbering
remote work first — in either mode:

```bash
git fetch origin <branch>
git rev-list --left-right --oneline HEAD...FETCH_HEAD   # ">" lines = commits only on remote — STOP and investigate
```

Then push by the mode step 6 picked:

```bash
# fixup — the branch only grew, so it fast-forwards:
git push origin HEAD:<branch>
# fold — history was rewritten, so it needs a lease-guarded force:
git push --force-with-lease=<branch>:<expected-remote-sha> origin HEAD:<branch>
```

- Always `--force-with-lease` pinned to the SHA you just fetched, never a bare `--force`.
- If `>` lines appear, the remote has commits the local branch lacks — surface it, do not overwrite.
- A remote ruleset may warn `Commits must have verified signatures ... violation: <sha>` when the
  rewritten commit is unsigned. The push can still succeed, but a signed-commits merge rule may later
  block the merge — flag it to the user (it's their git signing config, not something to fix silently).

## Output

End with: what was fixed (and where), what was rejected as a false positive (and why), the resulting
git history, and any items deferred to the user. Be explicit about anything not yet pushed.

After a **fixup** run, name the fixups still standing and where they get folded: a repo that squash-merges
absorbs them at merge, so nothing more is needed; a repo that rebase- or merge-commits needs them folded
before merge — `/my-ship` step 5 does exactly that, or by hand with
`GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>`.
