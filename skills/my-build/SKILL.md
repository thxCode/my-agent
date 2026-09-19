---
name: my-build
description: Implement an approved spec or debug plan with TDD and focused commits.
---

# my-build

Build the target: **the user's current request**

Implement the **task list**. Output must conform to the target's **Code Style** and **Boundaries**, applicable
project instruction files, and surrounding code. **Verify before you commit.**

**Task list** = a spec's **Implementation Plan** / a debug artifact's **Fix Plan**.

- **Language.** Write target edits (idea write-ins, task check-offs) in **English**; for other artifacts (code,
  comments, commits, docs) follow the project's conventions; talk to the user in their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

## Phase 1 — Resolve the target

1. **Strip an optional `auto` or `team` token** from `the user's current request` first (they pick the run mode in Phase 2, not
   the target); the remainder is the selector. Resolve it per
   `~/.agents/skills/my-workflow/references/resolve-target.md`.
2. **Not planned → recommend the planner first, ask before proceeding.** Judge from **content**, not the
   `Status:` line:
   - **spec** not planned (Implementation Plan still `> TODO` / no `[ ]`; or Test Plan has `TODO` / any `<…>`) →
     recommend `my-plan`.
   - **debug artifact** not planned (Fix Plan empty/`TODO`; or Test Plan has placeholders) → recommend `my-debug`.

## Phase 2 — Set the baseline & route skills

1. Read the target's **Design Details** — its **task list** is your ordered work.
2. **Clean git baseline:** `git status --porcelain`; unrelated uncommitted changes → ask how to handle before
   per-task commits.
3. **Be on the target's working branch** (create from default branch if not). Prefix by source:

   | Target | Branch |
   | --- | --- |
   | Feature spec (`Type: Feature`) | `spec/<title>` |
   | Bug-fix spec (`Type: Bug fix`) | `fix/<title>` |
   | Debug artifact | `fix/<title>` (always) |

   (`<title>` = hyphenated title, without the date/issue prefix.)
4. **Run mode:**

   | Mode | When | Stops |
   | --- | --- | --- |
   | **Team** (parallel) | the task list carries `Blocked by:` / `Owns:`, **and** either the `team` token was passed or the session is Orca-hosted | gated tasks + compaction (5.3) + final review (5.5) |
   | **Auto-chain** | session in an unattended-capable permission mode (`acceptEdits`/`bypassPermissions` or the host's equivalent), **or** `auto` token passed | only compaction (5.3) + final review (5.5) |
   | **Per-task confirm** (default) | every other case | pauses before each commit |

   State the chosen run mode **and** the tracking mode in your first message.

   **Team mode → read `~/.agents/skills/my-workflow/references/team-lane.md` now and follow it in place of Phase 3's
   one-task-at-a-time sequencing.** Everything else in this skill still applies. `team` passed but the task
   list has no `Blocked by:` / `Owns:` → don't improvise a DAG: say so, recommend `my-plan` to annotate it,
   and offer per-task confirm instead.

   **Orca-hosted and the DAG is already annotated?** Detect the host with **Detect the Orca host** in
   `agent-runtime.md`. If two or more tasks are unblocked with disjoint `Owns:`, offer Team without waiting for
   the token — the workers are a command away and sequencing them wastes wall-clock. Offer, do not assume: the
   user still approves the frontier and placement before you spend their quota.
5. **Backbone (inline discipline):** **tracer bullets**, never big-bang; drive with TDD (RED →
   GREEN → keep suite green; loop in Phase 3). **PoC/spike front-loaded?** (risky items ordered first) build it first;
   if it overturns a Goal/Feature/design, reconcile the target **now** at its source (Phase 3's write-back) while churn is
   cheap — keeps `my-ship`'s history folding small.
6. **Extra skills by task nature:**

   | Task nature | Skill |
   | --- | --- |
   | Refactor (rename/extract/split/move) | `gitnexus-refactoring` **first** (if available) |
   | API / interface design | `api-and-interface-design` |
   | Risk item (flagged in target) | `crosscheck` — its spend gate already names a risk-flagged target |
   | Frontend / UI | `frontend-ui-engineering` |
   | Rendered screenshot (render/responsive/component shot) | `crawl4ai-search` |
   | Interactive UI debug (clicks/console/network) | `browser-testing` |
7. **Confirm the build/test environment before the loop.** Read the environment the target pinned in
   **Commands** — **local or remote** (if remote, its access method); if unpinned (older/unplanned target), ask.
   **Smoke-check** the build/test commands run in that environment before starting — a broken environment found
   mid-build is expensive to unwind.

## Phase 3 — Build the next task (loop)

Do **one** pending task from the task list:

1. Read its acceptance criteria; load relevant existing code, patterns, types. On the **first** task, if
   `Status:` is still `Planned` (spec) / `Diagnosed` (debug), flip it to `Building` — saved with the task in 5.2.
2. **TDD:** failing test (RED) → minimum to pass (GREEN) → full suite (regressions) → build.
3. **Conform:** follow Code Style & Boundaries plus applicable project instructions; match surrounding code; run lint/format (from
   Commands).
4. **Simplicity & readability discipline (continuous, while coding — never overrides project instructions):**
   - **Decision ladder before writing** (from [`ponytail`](https://github.com/DietrichGebert/ponytail), MIT;
     see `CREDITS.md`) — need this at all? → codebase already has it? → standard library? →
     native platform feature? → an installed dependency covers it? → can it be one line? → *then* minimal
     working code. **Deletion over addition; boring over clever.** Climb it after you understand the change,
     never instead: the smallest diff in the wrong place is a second bug.
   - **Simplify anti-patterns** — deep nesting → guard clauses / extract; long function → split by
     responsibility; nested ternary → if/else; generic names → descriptive; duplicated logic → shared function;
     dead code → remove after confirming.
   - **Never simplify away** — input validation, data-loss-preventing error handling, security, accessibility,
     explicitly requested features.
   - **Heavy/at-scale simplification** → raise it as a finding in the Phase 5 review instead of widening the
     task; `~/.agents/skills/my-workflow/references/review-doctrine.md` gives the finding form.
   - **Accepting a known ceiling** (a global lock, a linear scan, a naive heuristic) → leave the `shortcut:`
     marker that same file defines, naming the ceiling and what would justify revisiting it.
5. **Unclear spec detail → ask the user** (don't guess). For a bounded factual question you may
   delegate it to the read-only independent worker selected by `crosscheck` — apply
   `crosscheck` (read-only, foreground, one tightly-scoped question). Keep this to **one bounded
   question**; the per-task heavy **defect review** belongs to Phase 4's heavy-review step, not here.
6. **Build changes the target?** (a new idea, or a finding that overturns a Goal / Feature / User Story / Risk)
   — confirm, then write it back **at the source** (fix the upstream statement, not just the task line). Then
   continue against the reconciled target. A **design-level** problem (the design itself overturned, not a
   task detail) → beyond the write-back, recommend returning to `my-plan` to re-plan. If stronger reasoning is
   warranted, apply `~/.agents/skills/my-workflow/references/model-routing.md`; never prescribe a vendor model name.
   **Whether the overturn is yours to make or the user's to rule on** — the two questions in
   `~/.agents/skills/my-workflow/references/decisions.md`, "Overturning a decision that is already written down".
7. **Where a finding goes — and it is usually not a new todo issue.** Ask **what would close it**:

   | Its close condition | Where it goes |
   | --- | --- |
   | "these specific lines in this file become X" | an issue, or a new task |
   | "someone makes that judgment again" | **not an issue** — it is a *property*: write it into the target (Notes / Constraints / Risks) where the next reader meets it |
   | "this task does it in passing" | file nothing — **widen this task's acceptance** |

   **Where the finding came from decides what shape its answer may take** — read
   `~/.agents/skills/my-workflow/references/filing-an-issue.md` before opening one. A finding that was
   *measured*, *reported*, or *irreversible* has earned an issue. One that was *inferred* has to say who would
   configure it, whether the fix asks the user to restate what they already know, and whether the test that
   caught it is one only we would have written. Failing those does not make it unreal — it moves the answer
   to prose, a warning or a stamp, and away from an API. The provenance line goes in the issue body, because
   the next reader cannot recover it from the title.

   An issue that should never have existed and a real gap are **identical in an issue list** — one title and one
   number each — so the list can never tell you later which it was. Measured: 39+ issues opened across one
   program, one of which concluded that "the remaining ~35 sites are prose, mechanically undecidable" — that is
   a property, not a gap. And a deferral you do record must state **what does not count as filling it**, or the
   next adjacent change closes it — a gap that only says what is missing lets whoever fills it pick the
   acceptance criterion, and the cheapest filler is usually the one that discriminates nothing.

   **A conditional deferral needs an action on both branches.** "If it turns out to be real, file an issue"
   specifies only the positive branch, so a negative finding triggers nothing — and a negative conclusion
   produces no commit, no file, no PR, which makes it the single easiest conclusion to lose. The record then
   still reads "not verified", indistinguishable from never having looked, and it goes on inviting someone to
   redo the work. The negative branch's action is to **write the conclusion back** ("checked, does not hold,
   because X") in the same step as reporting it — there is no later trigger.

## Phase 4 — Review & impact analysis

Depth matches the task's risk:

1. **Routine → inline self-review** on four axes: correctness (meets acceptance, edge cases), readability,
   convention conformance (Code Style / Boundaries / project instructions / surrounding code), security.
2. **Heavy → independent review.** When the task changed **exported/shared symbols**, is
   **Risk**-flagged, or is a **large change**: run **one** read-only review over the task's working-copy
   diff (uncommitted until Phase 5) — select the route per `crosscheck`. Collect it **before committing this task** and reconcile per `crosscheck` (spot-check findings, **STOP and ask which to fix**, never
   auto-apply). This per-task heavy review is the **exception** to crosscheck's one-turn-per-stage ceiling
   — one review per heavy task, never concurrent. At the same threshold, if `gitnexus-impact-analysis` is
   available, run one round on the changed symbols (what depends on them, what could break).
3. Problems surfaced → address (the current lead fixes them; never auto-apply the tool's suggestions) → re-verify
   (back to Phase 3).

## Phase 5 — Confirm, commit, continue

1. **Gate by run mode** once reviewed & verified:
   - **Per-task confirm** → present the task and **wait for confirmation** before committing.
   - **Auto-chain / Team** → skip the pause; commit and continue.
2. **Record → stage → commit**, in order:
   - **Record:** check off `[x]` in the task list **and advance `Status:` in the same edit** — `Building` while
     tasks remain, `Built` when this was the last.
   - **Stage:** stage only this task's files. Stage the target edit **only if committed (`specs/`)**; a **local**
     target (`.claude/specs/` or `.claude/debugs/`) is updated on disk but **never staged**.
   - **Commit with `-s`** (let `-s` append `Signed-off-by:`; never hand-write it):

     ```
     <type>(optional scope): <title in lowercase>

     - <change, one simple point per bullet>
     - ...

     Task <task index> of <target name>.
     ```
     - `type` ∈ `fix|feat|build|chore|ci|docs|style|refactor|perf|test`.
     - `<task index>` = the task's ordinal; `<target name>` = the hyphenated spec/debug title (e.g.
       `Task 3 of user-auth-flow`).
3. **Compaction checkpoint** (tasks still pending) — apply
   `~/.agents/skills/my-workflow/references/compaction.md`.
4. Back to Phase 3 for the next task. All done (`Status: Built`) → **summarize:** tasks completed, tests added,
   commits made, anything skipped / flagged / left for the user.
5. **End-of-build review** (all modes):
   1. **Pin the scope, fail fast.** Resolve the base and confirm `git diff <base>...HEAD` is non-empty (working
      tree if still uncommitted). A bad ref or empty diff fails here, not inside three reviewers. Team mode →
      shut teammates down first, so nothing is still writing while the reviewers read.
   2. **User review** — present an overall diff overview; ask whether anything needs adjustment (yes → Phase 3,
      then back here).
   3. **Run the two axes in parallel** — separate contexts, so neither pollutes the other:
      - **Standards** — apply `~/.agents/skills/my-workflow/references/review-doctrine.md` over the build.
        It sets which reviewers to split out, what a finding must carry, and the verification pass every
        candidate clears before you see it; `smells.md` is the catalog it draws on.
      - **Spec** — the `spec-reviewer` subagent, seeded with the **target and the diff only** — never your own
        conclusions about the build. It answers the one question the five axes never ask: did we build what was
        ordered?
   4. **Kick off the cross-check (gated, background) — apply `crosscheck`.** Confirm through the selected
      route that no earlier review is still in flight, then background **one** branch review over the whole
      build diff. **Once, never per task.** It runs while the two axes do.
      Gate skip / neither tool available → note it and skip.
   5. **Barrier & address findings.** Collect all three, using the selected route's status/result mechanism for
      the cross-check. Report **Standards and Spec side by side under their own headings — never merged, never
      re-ranked across axes.** A change can pass one axis and fail the other; merging lets the clean axis mask
      the failing one. Fold the cross-check's findings into whichever axis they belong to. Spot-check large
      findings against source (per `crosscheck`), then **STOP and ask the user which to fix** (never
      auto-apply), fix the real issues, and re-verify (Phase 3) before finalizing.
6. **Ask whether to run `my-ship` now.** If yes, continue into `my-ship` with this target.
