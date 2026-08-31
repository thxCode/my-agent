---
name: my-ship
description: Finalize and ship a branch — e2e, docs and ADRs, tidy history, open a PR. Target-optional.
argument-hint: "[spec/debug title or path, or nothing to ship the current branch] [--assist codex|kimi]"
---

# /my-ship

Finalize and ship the current branch: **$ARGUMENTS**

Tidy up after the build: validate end-to-end, keep the suite green, tidy the branch history, resync the
overview and docs, open a clean PR. **Target-optional** — a **target** (spec or debug artifact) drives
finalization and gets written back; with none, ship straight from the branch diff. Every change conforms to
project conventions (target **Code Style** & **Boundaries** when present, `CLAUDE.md`, existing test/doc structure).

- **Language.** Write target edits (e2e fix write-backs) in **English**; other artifacts (tests, overview,
  docs/ADRs, commits, PR body) follow the project's conventions; talk to the user in their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

## Phase 1 — Resolve the ship target

1. **Branch & base.** Confirm the current branch and its base (default branch — e.g. `main`; resolve via
   `git symbolic-ref refs/remotes/origin/HEAD` when unsure). `base..HEAD` is the **ship scope**.
2. **Attach a target (optional).** Resolve `$ARGUMENTS` per
   `~/.claude/references/my-workflow/resolve-target.md` — **target-optional; never block on a missing one, any
   branch can ship.** State the mode (**target-driven** vs **no-target**) in your first message.
3. **Run the full test suite; green before finalizing** — fix failures or surface them.
4. **Consistency scan (read-only) — target-driven only.** Two checks, both read-only:
   - **Doc vs doc.** Read the target's upstream statements against the completed task list; flag any built
     outcome that contradicts them (spec → Goals / Features / User Stories vs Implementation Plan; debug
     artifact → Root Cause / Background vs Fix Plan).
   - **Diff vs spec.** Run the `spec-reviewer` subagent over `base..HEAD`, seeded with the target and the diff
     only. The doc-vs-doc check can't see the code — this one catches what the branch actually shipped:
     requirements missing, scope nobody asked for, requirements implemented wrong.

   On confirmation, reconcile the upstream text (**modifying only the target**); code-level findings go to
   Phase 2's fix loop. **No target → skip both.**
5. **Compaction checkpoint** (ship usually follows a long build) — apply
   `~/.claude/references/my-workflow/compaction.md` (its `/my-ship` row and threshold).
6. **Kick off the ship-time cross-check (gated, background) — apply `crosscheck`.**
   Pre-flight `/<tool>:status`: adopt any review already in flight (e.g. after a compaction resume) —
   **never launch a second** — and barrier on any job `/my-build` left running. **De-dup:** if
   `/my-build` already reviewed exactly these commits and nothing has changed the diff, **don't spend
   now** — defer to the Phase 5 barrier, which reviews only what Phases 2–4 change (e2e fixes).
   Otherwise (no-target mode, or the branch was never reviewed) background **one** `/<tool>:review
   --scope branch --base <base>` (`/<tool>:adversarial-review <focus>` if the build was **Risk**-flagged),
   overlapping Phases 2–4; collect it at Phase 5. Neither tool available → skip and say so.

## Phase 2 — End-to-end tests (only if the project has an e2e surface)

Only if the project has an e2e surface — a project e2e skill, a bare e2e suite (make/npm/pytest target), or a
browser-drivable UI (`agent-skills:browser-testing-with-devtools`):

1. **Ask whether to run e2e now.** No → Phase 3.
2. **Route by the surface:**
   - **Project e2e skill** (in the project's `.claude/skills/`) → run it **in the main loop** as it is designed —
     such skills may orchestrate their own subagents and gate mutating steps on user confirmation, so never wrap
     one in a subagent; its own frontmatter pins its model.
   - **Otherwise** → delegate to the `test-worker` subagent (sonnet — mechanical execution, off the main
     context): pass a bare suite command + expected outcome, or the browser scenario list; it returns pass/fail
     + evidence and never edits files.
3. **Each failure:** fix it here in the main loop and cover at the cheapest layer (prefer unit over e2e);
   **target-driven → also write the fix back into the target.** Then prune obsolete e2e cases.

## Phase 3 — Overview (only if an overview skill is available)

1. Judge whether the build made the overview stale.
2. If so, **confirm with the user**, then update it to reflect reality.

## Phase 4 — Docs & ADRs

Is the change **architecturally significant** (new/changed public API, new dependency, altered data flow)?
- **Yes** → `agent-skills:documentation-and-adrs` to identify and complete the doc/ADR updates.
- **No** → quick inline check: did this make any doc stale? Update it if so; else say so and move on. No ADR.

## Phase 5 — Confirm, tidy history & commit

**Barrier first — cross-check (apply `crosscheck`), before touching history.** Collect the
ship review kicked off in Phase 1 (`/<tool>:status` → `/<tool>:result`). If it was deferred there but
Phases 2–4 changed the diff (e2e fixes / new commits), run **one** review now over that changed scope.
Spot-check findings against source (Step 7); **STOP and ask the user which to fix** (never auto-apply);
fold accepted fixes in **now**, so step 5's history-tidy squashes them into their logical commit.
Nothing warranted (de-dup skip, no changes, or neither tool available) → say so and continue.

1. **Any code changed in Phases 2–4 → re-run the full suite** (green before committing).
2. **Mark the target's terminal state — target-driven only, before any PR exists** (write in **English**):
   - Advance `Status:` (carried from `/my-build`'s `Built`) to `Shipped`; add the line if a legacy target lacks it.
   - **No PR link.** A committed spec (`specs/`) must read `Shipped` before the PR opens (PR captures it); never
     backfill a link (a pointless extra commit).
   - A local target (`.claude/specs/` or `.claude/debugs/`) takes the same edit on disk but is **never staged**.

   **No target → skip.**
3. Present everything changed (target if any, tests, overview, docs) for **review**.
4. On confirmation, **commit** the finalization changes (group logically; stage only what you changed;
   descriptive messages). Stage the `Status: Shipped` edit **only if the target is committed (`specs/`)**.
   **Nothing stageable → skip the commit and say so.**
5. **Tidy the branch history — evaluate on every ship, before pushing.** A build lands one commit per task; ship
   adds finalization commits. Fold the *noise* so the PR reads as a clean, linear story:
   - Inspect first: `git log --oneline <base>..HEAD`.
   - **Fold noise into its logical owner**, tidying messages — WIP / fixup / typo / ship micro-commits belong
     squashed into the commit they fix. **Preserve the per-task narrative** — do **not** flatten the whole branch
     into one commit (that destroys the story `/my-build` recorded). Target-driven → also check the target reads
     cleanly.
   - **Propose the rewritten history, wait for confirmation.** On approval, execute non-interactively
     (interactive rebase is unavailable here):
     ```bash
     # single commit, or all fixes belong to the tip:
     git add -A && git commit --amend --no-edit
     # fixes belong to specific earlier commits:
     git commit --fixup=<target-sha> -- <files>
     GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>
     ```
   - Use `git blame <file>` / `git log --oneline -- <file>` to find which commit a fix belongs to.
   - **Normalize task order — only when the `Task N of` trailers aren't ascending.** A parallel (`team`) build
     commits in *completion* order, so the log can read `Task 1`, `Task 3`, `Task 2`. Every ordering is valid
     (parallel tasks own disjoint paths), but the PR should read in the plan's order. Reorder by the trailer
     once folding is done — that same disjointness is what makes it conflict-free:
     ```bash
     TODO=$(mktemp)
     git log --reverse --format='%h' <base>..HEAD | while read h; do
       n=$(git log -1 --format=%B "$h" | sed -n 's/^Task \([0-9]*\) of .*/\1/p')
       echo "${n:-9999} pick $h $(git log -1 --format=%s "$h")"
     done | sort -n -s | cut -d' ' -f2- > "$TODO"
     GIT_SEQUENCE_EDITOR="cp $TODO" git rebase -i <base>
     ```
     Commits with no trailer (ship's own finalization commits) sort last, keeping their relative order.
     **A conflict here means `Owns:` overlapped and the tasks were never truly independent** — `git rebase
     --abort`, keep completion order, and surface it: that overlap is a worse finding than the ordering.
6. **Ask whether to push the branch and open a PR.** If yes, push and create it.
   - **PR body — write to the repo's PR template when it has one.** Find it:
     ```bash
     git ls-files | grep -i pull_request_template
     ```
     - **Found** → its headings **verbatim and in order**, every one filled, its machinery kept
       (`/kind` lines, the issue-linking line, a fenced `release-note` block). A section with nothing to
       say gets an explicit `NONE`. Complex content as **bullets** — concise, forceful.
     - **None** → fall back to the default body below.
     - **The issue link — pick the verb by what the PR actually finished.** GitHub auto-closes only on
       `Fix(es|ed)` / `Close(s|d)` / `Resolve(s|d)`. Use one **only when the PR fully resolves the
       issue**; when it merely advances one, take a non-closing verb — whichever the template teaches
       (`Addresses`, `Relates`, `Part of`), else a plain `Addresses #<n>`. `Fixes` on partial work
       closes what isn't done, and reopening loses the thread's triage.
   - **Match the house style** — a template names the sections, not how this project fills them. Read the
     latest merged PR (`gh pr list --state merged -L 1 --json body -q '.[0].body'`) for how much detail a
     reviewer expects and which `/kind` labels are real.
   - **Content mapped into the body:** spec → Summary + completed task list; debug artifact → Background + Root
     Cause + completed Fix Plan; no target → derive from the tidied commit log + `base..HEAD` diff.
   - **Already pushed + step 5 rewrote history → force-push (outward-facing, confirm first):**
     `git fetch origin <branch>`, then `git rev-list --left-right --oneline HEAD...FETCH_HEAD` (any `>` lines =
     remote-only commits → STOP and surface). Push with `--force-with-lease` pinned to the fetched SHA — never a
     bare `--force`.
7. **Refresh the GitNexus knowledge graph** (only if the project uses GitNexus). Invoke `gitnexus-cli` to run
   `analyze --index-only`, syncing the graph to the shipped code (add `--embeddings` **only on the default
   branch**; on a feature branch — where ship normally runs — omit it to preserve the default-branch embeddings,
   which regenerate once the PR merges). Run unconditionally — no permission prompt. `--index-only` is a pure
   index pass: no skill generation, no `CLAUDE.md` / `AGENTS.md` touch.
8. Summarize what shipped and anything left for the user.
