---
name: my-loop
description: Run a long-term engineering program from a report or existing specs, starting with resource readiness and a pre-spec PoC before supervised my-* stages, PR review, and issue closure.
---

# my-loop

Use this skill when one report, plan, or set of specs will take several implementation and review cycles, and a
later coordinator must be able to resume the work. A single feature or bug uses the relevant `my-*` stage.
The coordinator owns the program; each spec worker owns only its assigned branch and task files.

## 1. Establish the program

1. Read the supplied report in its actual form: file, conversation plan, research output, or existing specs.
   Read applicable project instructions and the current repository state. Locate any existing program directory
   before creating one; resume its records instead of starting a second ledger. If an existing directory belongs
   to a different source, choose another slug instead of overwriting it.
2. Use a local program directory beside the report: an existing report directory, or a sibling directory named
   after a report file. For conversation-only input or specs without a report file, use
   `<repo>/.claude/reports/<slug>/`. Record the absolute path in `STANDARD.md`; keep these coordination files
   local and never stage them. If the chosen location is unavailable, choose a writable local location and
   record the reason and path before dispatch.
3. Preserve the input. If it exists only in the conversation, save its exact text as `SOURCE.md`. If the source
   is a mutable local file, save its original contents as `SOURCE.md` before editing it. Record the source path
   and content hash or snapshot path in `STANDARD.md`. Keep source evidence, alternatives, corrections, and
   open risks reachable; never replace a measured result with a cleaner but unsupported summary.
4. Judge the input's maturity. If specs already state outcomes, acceptance, dependencies, and open decisions,
   validate and reuse them. Otherwise refine the report into those elements first. Trace each candidate spec to
   source evidence and a testable outcome; mark unsupported claims and decisions that need the user. Do not
   force a second decomposition of an adequate spec set.
5. Draft a provisional spec dependency map and closure criteria. Derive the resources and expensive unknowns
   each spec depends on. Do not freeze the map until the pre-spec PoC gate is complete.

Read [records.md](references/records.md) when creating or resuming the program files. It defines the three
ledgers, handback fields, and the checks at each stage gate.

## 2. Check resources and resolve expensive unknowns

1. Inspect available project resources before asking. From the provisional spec map, list the needed test data,
   credentials or accounts, software versions, compute or cluster capacity, access, budget, and cleanup owner.
   For each missing resource, ask the user for the minimum shape, purpose, quantity or duration, cost estimate
   or spending cap, and the spec or PoC check it unlocks. Request resource access and PoC authorization
   together at kickoff; never put secret values in the program files.
2. Put all costly feasibility checks that can be done before implementation into one `poc/PLAN.md`. Each check
   states the question, required resource, procedure, observable pass/fail/inconclusive result, and how each
   result changes the spec map. Reuse shared setup within this PoC task. Tests that require code not yet built
   stay in the relevant spec's Test Plan, with that dependency explicit. If there is no such unknown, record why
   the PoC is unnecessary instead of creating an empty task.
3. Present the verified resource gaps, PoC PLAN or no-PoC rationale, and task-specific authorization charter
   together. Ask the user for missing resources and any approval needed to run the PoC, with the expected use
   and limits. Record the answer in `STANDARD.md`; permissions from another program do not carry over.
4. Confirm the granted resources are accessible. Run any required PoC before starting the first spec. Use a
   supervised `my-crew` Task when available; otherwise execute it sequentially under the same evidence contract.
   The worker writes
   `poc/RESULT.md` with one conclusion and raw evidence per PLAN check. Prototype code is not shipped by the PoC;
   a later spec must rebuild and verify anything it adopts. Stay within granted resource limits and record
   which resources were cleaned up or retained. On a resumed program, credit equivalent verified evidence and
   run only missing checks before the next dependent spec.
5. If the PoC ran, the coordinator checks every RESULT against the PLAN, including failed and inconclusive
   checks, then updates the report, `STATUS.md`, and `HISTORY.md` in the same coordination turn. If no PoC was
   needed, record that finding in `STATUS.md`. Resolve product decisions exposed by the PoC with the user when
   the charter does not delegate them. Freeze the spec map only after this gate. An inconclusive check blocks
   affected specs until its missing resource is supplied or the user explicitly narrows or defers that scope;
   never record it as a pass.

## 3. Keep one source of truth for each kind of fact

- `STANDARD.md` is the program's contract: source, goal, spec map rules, single writers, artifact paths,
  authorization, PoC gate, human review triggers, review-round budget, resource limits, and project-specific
  overrides.
  This program uses the singular filename; do not rename an existing program's `STANDARDS.md` merely to conform.
- `STATUS.md` answers what is true now and who acts next. Keep resource readiness, PoC results, the spec
  dependency map, decisions awaiting an answer, issue assignment, active windows/worktrees, and blockers current.
  Update it in the same coordination turn as a resource change, gate, new issue, ruling, dispatch, merge, or
  worker release.
- `HISTORY.md` is append-only: what changed, why, who decided, and where the evidence lives. Correct old entries
  with a new entry. Record resource grants and cleanup as well as PoC rulings. Move completed phase detail here
  and leave a short current-state pointer in `STATUS.md`.
- The live report carries design conclusions, not workflow status. When a verified result overturns a report
  conclusion, correct that conclusion in place and record the correction and its evidence in `HISTORY.md`.
- The coordinator alone writes these three ledgers and the live report. A worker writes only its assigned
  handbacks, summary, evidence directory, branch, and repository spec. Use absolute paths in program records
  across worktrees.
  Stable spec, decision, and issue identifiers are never recycled or silently renumbered.

## 4. Run each spec through the existing stages

1. Before dispatch, confirm the PoC gate and required resources are ready, then inspect `STATUS.md` for assigned
   issues and dependencies. Write a cold-start `HANDOFF.md` with report and PoC conclusions, evidence paths,
   owned paths, accepted decisions, acceptance checks, environment, exclusions,
   exact authorization, escalation triggers, review budget, and required handback path. Name any issue assigned
   to this spec and whether it is to be fixed or re-evaluated. Serialize specs whose planned owned paths
   overlap; recompute that overlap if a plan changes its owned paths.
   Apply the reference boundary beside the HANDOFF template in [records.md](references/records.md).
2. For supervised windows, follow `my-crew` and the current
   `~/.agents/skills/my-workflow/references/agent-runtime.md` and
   `~/.agents/skills/my-workflow/references/multi-window.md` references.
   The runtime's Task/Dispatch completion signal is authoritative; a file appearing or a message being sent is
   not completion. Verify delivery, collect each gate, check the underlying files and evidence, then settle and
   reclaim the worker. If supervised windows are unavailable, run the stages sequentially in this session unless
   the user required separate windows; in that case, pause dispatch and explain the missing runtime.
3. The worker runs `my-spec` -> `my-plan` -> `my-build` -> `my-ship` -> `address-pr-review`. Read each stage skill
   when entering it. The repository spec follows that project's `my-spec` location and lifecycle; the local
   program directory holds coordination and raw evidence, not a competing spec body. A pre-existing valid spec
   starts at its first unfinished stage.
4. A stage's normal user-confirmation request goes to the coordinator only when the charter explicitly
   delegates that decision. The worker presents the concrete artifact and waits for a recorded coordinator
   ruling. The coordinator verifies it against source, scope, and acceptance before replying. Decisions outside
   the charter go to the user; a worker message never expands authorization. An explicit invocation of
   `my-loop` requests this documented stage chain; an implicit router match still respects `my-spec`'s
   explicit-only entry rule.
5. At each gate, verify the worker's changed paths, spec state, tests, issue list, and evidence against the
   handoff. Update `STATUS.md` and append `HISTORY.md`; send the next instruction only after recording the
   ruling. After merge, reconcile the actual PR and latest handback with the issue ledger and report; verify
   `SUMMARY.md` when it arrives. Assign every residual and mark conclusions still awaiting evidence. Release
   only the windows and worktrees the program owns after their handback and cleanup.

## 5. Bound review and merge

- Default to four effective feedback rounds per PR; record a different limit in `STANDARD.md` when appropriate.
  A round is a fresh reviewer feedback batch on a PR head and its disposition. Repeated polling or a review
  tool's no-op on the same head does not count. The worker handles feedback through `address-pr-review`, verifies
  fixes, and reports new findings and the remaining budget at each review gate.
- At the limit, stop automatic fixes and return the findings to the coordinator. Continue only after a scoped
  ruling. Findings with potential data loss, broken security guarantees, or cross-tenant exposure require an
  immediate ruling regardless of the remaining budget.
- The worker never merges. The coordinator merges only when the charter grants it, the PR's current head is
  mergeable, required checks ran and passed on that head, required human review covers that head, no actionable
  new feedback remains, and unresolved review threads are cleared or have a documented disposition. For review
  sources expected to run after each push, confirm a completed review of the current head or a chartered waiver;
  an empty comment list while review is pending is not a completed review. A check skipped by path filters does
  not prove unrun tests. After a new push, re-evaluate feedback and checks on the new head.
- A user-reported or observed merge starts post-merge reconciliation even if the review gate or a slow CI
  workflow was still pending. Verify the PR's merged state, head, and merge commit first; do not describe pending,
  skipped, or canceled checks as passed. Stop work on the merged PR, request the worker's summary, and record
  unfinished reviews, checks, findings, and any missing summary with an owner and next check in `STATUS.md` and
  `HISTORY.md`. Reconcile known issues and report conclusions from actual evidence, then dispatch the next ready
  spec without waiting for unrelated late CI or clerical summary work. Check late results at the recorded gate;
  a failure or material new finding blocks affected dependent work and becomes an assigned issue or follow-up.
- Pause for the user when an unapproved public interface or product behavior change appears, a recorded
  decision is overturned, evidence is insufficient for a material claim, CI or review cannot converge, or a
  resource or spending limit would be crossed. Record the pending question and do not advance dependent work.
  The user may add review gates in the charter.

## 6. Converge issues and finish

- A worker first checks whether an unexpected finding belongs in the current spec or duplicates an existing
  issue. Use `~/.agents/skills/my-workflow/references/filing-an-issue.md` before opening an external issue;
  record provenance and what would close it. The worker reports each new issue immediately, without waiting
  for a stage gate.
  Findings outside scope go into `STATUS.md` in that coordination turn, with one assignee: a named next
  spec, a cleanup batch, the final closure spec, or an external owner. An observation that does not warrant an
  issue remains a documented risk or constraint, not a speculative issue.
- Reconcile the issue ledger after every spec merge and at each dependency-tranche boundary. Bring related
  items into the next spec's handoff. If the deferred backlog grew since the previous tranche, schedule a
  bounded cleanup batch before starting more feature specs or record the user's decision to defer it. At each
  tranche boundary, record the outcome even when the ledger is empty.
- The final closure spec follows the same stage chain. Freeze its input issue list and verification matrix.
  For every row, record a fix with evidence, a justified closure or duplicate, or an explicit deferral with
  owner and revisit trigger. New findings during closure get an owner and follow-up gate; an unassigned issue
  cannot be hidden by marking the program complete.
- On coordinator takeover, read `STANDARD.md`, `STATUS.md`, and the latest `HISTORY.md` entries, then reconcile
  the recorded branch, PR, worker, and issue state with the actual tools before acting. Confirm the previous
  coordinator has yielded ownership before writing the ledgers. Never dispatch, merge, or reclaim from stale
  ledger text alone.
