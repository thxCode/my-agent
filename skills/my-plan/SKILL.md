---
name: my-plan
description: Break a spec into a tracer-bullet task DAG with blocking edges and owned paths, and fill its Test Plan. Writes back the spec only.
---

# my-plan

Refine the plan inside a spec: **the user's current request**

This skill **only ever writes back the one spec file** — no other edits. Stay read-only otherwise.

- **Language.** Write the spec in **English**; talk to the user in their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

## Phase 1 — Resolve the spec

Resolve `the user's current request` per `~/.agents/skills/my-workflow/references/resolve-target.md` (specs only — `specs/` committed
or `.claude/specs/` local).

## Phase 2 — Re-ground (read-only)

1. Re-read the spec end-to-end.
2. Re-ground the design in the real codebase: the **GitNexus MCP tools** if available (`query` / `context` /
   `explain`, and `impact` / `api_impact` before touching a shared symbol), else `grep`/`find`. External
   libs/frameworks not in the dependency tree → **DeepWiki**; a JS-rendered doc DeepWiki can't reach →
   `crawl4ai-search`. **Frontend** spec → a screenshot of the current rendered screen (`crawl4ai-search`, PNG to
   the scratchpad) keeps this phase read-only on project files. Broad sweeps (at the `grep`/`find` tier) —
   multi-file inventories, usage surveys, naming-convention scans → delegate to the host's native read-only
   explorer, conclusions only (keeps the main context lean); pivotal files you still read yourself.
3. **Learn the build/package system** — `Makefile` / build scripts, `package.json` scripts, CI config, any
   **overview** / **development** docs: exactly how it builds, tests, lints, packages. This grounds **Commands**
   in Phase 3 (what the project actually uses, not guesses). Reading only.
4. **Kick off a design cross-check (gated, background) — apply `crosscheck`.** As early as
   the re-read lets you, if the gate authorizes (novel / high-stakes / Risk-flagged design), background a
   **read-only** independent worker selected by `crosscheck`, seeded from the spec's **existing Proposal / Goals / Design Details** (the raw design
   intent, *not* your refinements) to red-team the approach and surface design risks + test scenarios.
   It runs while you re-ground (items 2–3) and draft Phase 3 — an independent second voice, one turn,
   no wait. Gate skips (or neither tool available) → note it and move on. Collect it at Phase 4.

## Phase 3 — Plan the implementation (Design Details)

**Work every design fork through `~/.agents/skills/my-workflow/references/decisions.md`** — recommendation first,
maintenance bill priced, one decision at a time. The forks here carry the largest bills in the whole workflow.

Deepen the spec's **Design Details**:

- Sharpen **Commands / Project Structure / Code Style** with concrete specifics grounded in the codebase and the
  build system from Phase 2. In **Commands**, also pin the build/test **environment** — **local or remote** (if
  remote, the access method: host / SSH / kubectl context / container) — and **confirm it with the user**
  (pivotal: it decides how every command runs). A **read-only smoke check** (invoke build/test once to confirm
  the environment is reachable) is fine — write no code, keep artifacts out of the tree.
- **Fill the Implementation Plan** (replace its TODO) as a **task DAG** — see the task shape below.
- **Prefactor first.** "Make the change easy, then make the easy change." Where a small structural change makes
  the feature tasks simpler, order it as its own task ahead of everything it serves.
- **Flag risks as you plan** — **compatibility** (breaking changes, version skew, migrations) or **reliability**
  (data loss, races, failure modes). **Raise with the user before locking in**; if agreed, record in **Risks and
  Mitigations** as `Risk → Mitigation`.
- **Reconcile upstream when planning contradicts it.** A **Goal / Feature / User Story** infeasible or wrong
  against the real code → don't plan around it; raise it, then fix the upstream statement at its source. Never
  leave a stale Goal/Feature above the plan.

### The task shape

Every task is a **tracer bullet** — a narrow but *complete* path through every layer it touches (schema, API,
UI, tests), demoable on its own, sized to fit one fresh context window. Not a horizontal slice of one layer.

```markdown
- [ ] **T2 · Login tracer bullet**
      Blocked by: T1
      Owns: `src/auth/login/**`, `tests/auth/login/**`
      Gate: review
      Acceptance: <concrete, testable>
      Verify: <the exact command>
```

- **`Blocked by:`** — the task ids that must land before this one can start, or `None`. These edges are what
  turn a linear stack into a DAG; `my-build` reads them to decide what can run at the same time. An edge that
  isn't a genuine dependency costs real parallelism — don't add one for narrative order.
- **`Owns:`** — the paths this task exclusively touches, as globs (globs age better than line numbers). Two
  tasks whose `Owns:` intersect can never run in parallel, so draw them disjoint wherever the work allows.
- **`Gate: review`** — mark **only** tasks that fire a `crosscheck` Step 1 trigger: Risk-flagged, a PoC/spike,
  or touching exported/shared symbols. No mark means the task can be dispatched to a parallel worker
  unattended. Don't invent new criteria; reuse that gate.
- **`Acceptance` / `Verify`** — what "done" means, and the command that proves it. A worker building this task
  cold has only these two lines to judge itself by.

Order so every task leaves the system working, with **checkpoints** between phases.

**De-risk first (PoC).** For items with uncertain feasibility or a Risk flag, confirm the environment (see
Commands), then order a small PoC / spike as the first task(s), `Gate: review` marked. Validating the riskiest
assumptions early keeps the spec from churning late (→ small `my-ship` history fold). `my-build` runs these
first.

**Wide refactors are the exception to tracer bullets.** A **wide refactor** is one mechanical change — rename a
column, retype a shared symbol — whose **blast radius** fans across the codebase, so a single edit breaks
thousands of call sites and no vertical slice can land green. Sequence it as **expand–contract** instead:

1. **Expand** — add the new form beside the old, so nothing breaks. One task, blocks all the rest.
2. **Migrate** — move call sites over in batches sized by blast radius (per package, per directory). Each batch
   is its own task, `Blocked by:` the expand, with the batch's paths as its `Owns:`. CI stays green batch to
   batch because the old form still exists — and disjoint `Owns:` means the batches parallelize.
3. **Contract** — delete the old form once no caller remains. `Blocked by:` every migrate batch.

## Phase 4 — Fill the Test Plan (KEP format)

**Barrier first — collect the design cross-check (if one was kicked off in Phase 2).** Per
`crosscheck`: collect through the selected route's status/result mechanism; fold the tool's design-risk findings
into **Design Details / Risks** (Phase 3) and its test-scenario suggestions into the Test Plan below.
Lock the plan only once reconciled; surface any unresolved disagreement to the user. Never
auto-apply — present and ask.

Replace the `Test Plan` placeholder with the structure below. **Fill every field with concrete items or
`None` — leave no `<…>` placeholders.**

```markdown
### Test Plan
[ ] I/we understand the owners of the involved components may require updates to existing tests to make this
code solid enough prior to committing the changes necessary to implement this enhancement.

#### Prerequisite testing updates
<Any base test work required before implementation.>

#### Unit tests
<Every added unit of code should have unit-test coverage. Per-package targets:>
- `<package>`: `<date>` - `<coverage %>`

#### Integration tests
<Integration scenarios; add concrete test names after the implementation PR merges.>

#### e2e tests
<End-to-end scenarios, or a justification for why e2e isn't needed.>
```

## Phase 5 — Review & write back

1. Present the proposed spec changes (enriched Design Details + filled Test Plan) for **human review**. Put two
   questions to the user alongside the diff — they are what make the DAG trustworthy:
   - **Is the granularity right?** Any task too coarse to fit one context window, or so fine the overhead
     outweighs it?
   - **Are the blocking edges real?** Does each `Blocked by:` name a genuine dependency, or just narrative
     order? A false edge silently serializes work that could have run in parallel.
2. **Wait for explicit confirmation** — the one pivotal question of this skill.
3. On approval, write the changes back and **set `Status:` to `Planned`** (add it under the title if missing).
   **Modify no other file.**
4. Confirm the saved path. **Consistency check:** read Goals / Features / User Stories against the Implementation
   Plan you just wrote; reconcile any upstream statement the plan now contradicts. The spec must read cleanly
   top-to-bottom — clear, logical, self-consistent.
5. **Offer the next step** (user may decline both and stop):
   - **Compact, then build** — context heavy / want a clean slate. Emit the three-line block per
     `~/.agents/skills/my-workflow/references/compaction.md`.
   - **Build now** — continue straight into `my-build` with this spec, keeping the current model (switching
     without compacting re-reads the full context — only suggest it if the user asks).
   - Either way, mention `team` when the DAG has parallelizable tasks (two or more unblocked tasks with
     disjoint `Owns:`): `my-build <title> team` builds them concurrently.
