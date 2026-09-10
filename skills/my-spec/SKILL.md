---
name: my-spec
description: Write a durable spec for a feature, tracked bug, or GitHub issue before implementation.
disable-model-invocation: true
---

# my-spec

Start spec-driven development for: **the user's current request**

Work the phases **in order** — each gates the next, no skipping ahead. Ask the user only when the judgment is
genuinely pivotal; infer the rest from context.

- **Language.** Write every field of the spec in **English**; talk to the user in their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

## Phase 1 — Gather context

**`the user's current request` is a GitHub issue?** (a bare number, `#123`, `owner/repo#123`, or an issue URL) — resolve and
read it with its comments per `~/.agents/skills/my-workflow/references/resolve-issue.md`, then condense the body and
the substantive comments into **one requirement: what to build or fix, and why**, plus any concrete acceptance
hints the thread already carries. That distilled requirement is what the rest of this skill works on. Don't
classify feature vs. bug here — Phase 2 does that. Carry the issue number forward; Phase 5.3 keys the filename
on it.

Build enough understanding to write a grounded spec (following the Source-lookup order):

- **Project** — an `overview` skill if available; else `README.md`, applicable instruction files, `docs/**/*.md`.
- **Code** — the **GitNexus MCP tools** if available (`query` / `context` / `explain` for a symbol or a flow,
  `route_map` / `tool_map` for an entry-point inventory), else `grep`/`find`. GitNexus returns nothing (index
  missing/stale) → **ask permission**, then `gitnexus-cli` → `analyze --index-only` (`--embeddings` only on the
  default branch; omit on a feature branch to preserve default-branch embeddings), and retry.
- **Broad sweeps** (at the `grep`/`find` tier) — multi-file inventories,
  usage surveys, naming-convention scans → delegate to the host's native read-only explorer, conclusions only
  (keeps the main context lean); pivotal files you still read yourself.
- **External libs/frameworks** not in the dependency tree — **DeepWiki**; JS-rendered doc DeepWiki can't reach →
  `crawl4ai-search`. Documenting existing UI → a screenshot of the current screen (`crawl4ai-search`) is good
  grounding.

## Phase 2 — Judge intent, then route

Classify `the user's current request`: a **Feature** (build new / change behavior) or a **Bug fix** (something is broken)?
Infer it; anything not clearly a bug takes the Feature path.

### 2A. Feature path

1. **User stories first.** Ask the user for their stories (Story 1, Story 2, …); offer drafts from `the user's current request` +
   context to make it easy, but let the user provide/confirm.
2. **Stories too thin → refine** (story portion only, pick one):

   | Skill | When |
   | --- | --- |
   | `agent-skills:interview-me` | underlying intent unclear / not in context (extract it, one question at a time) |
   | `agent-skills:idea-refine` | idea present but vague (sharpen & stress-test) |
   | `auto-research` | motivation depends on external facts (competitive analysis, prior art, sizing). Offer the discovered `auto-research` skill, then fold its digest into Motivation + stories' "so that `<benefit>`"; its gaps → Open Questions. One page settles it → `crawl4ai-search` or the host's ordinary web reader |

   Stories already concrete → skip refinement.
3. Carry the **finalized user stories** into Phase 3 (they pre-fill area #5 and anchor the rest).

### 2B. Bug-fix path

**For a bug that warrants a versioned, tracked spec.** A **quick, local** fix should use `my-debug` instead
(lightweight artifact under `.claude/debugs/` → `my-build`).

1. **Stay strictly read-only** while investigating — no edits until Phase 5.
2. Find the root cause: `gitnexus-debugging` if available, else `agent-skills:debugging-and-error-recovery`.
3. Carry the **root-cause analysis + reproduction** into Phase 3. For a bug, Phase 3 reframes: objective = fix
   the root cause; acceptance = the bug no longer reproduces + a regression guard; user story = the repro scenario.

## Phase 3 — Clarify the five areas

**Read `~/.agents/skills/my-workflow/references/decisions.md` before the first question and work every fork through
it** — it is what keeps this phase from agreeing its way into the option that's cheapest to build and most
expensive to own.

Nail all five before writing — **skip any already answered by Phase 2; don't re-ask.** Rule: spec-before-code —
pin *what* & *why* now, leave *how* to `my-plan`.

1. **Objective & target users**
2. **Core features & acceptance criteria**
3. **Tech-stack preferences & constraints**
4. **Known boundaries** — what must always be done, what must be asked first, what must never be done
5. **User stories** — carry forward from Phase 2 (bug: the repro scenario); don't re-collect

## Phase 4 — Write the spec

Fill the KEP-style template below — it *is* the coverage checklist; address every section. Leave
**Implementation Plan** and **Test Plan** as placeholders (`my-plan` completes them); no other leftover
placeholders.

Two metadata lines under the title:
- **`Status:`** — lifecycle trace; initial `Specified`, then `Planned`, next `Building` and `Built`, finally `Shipped`.
- **`Type:`** — the Phase 2 classification (`Feature` / `Bug fix`); `my-build` reads it to pick the branch prefix.

```markdown
# Spec: <Title>

Status: Specified
Type: <Feature | Bug fix>

## Summary
<One release-note-style paragraph: what we're building/fixing and why.>

## Motivation
### Goals
<Objective, target users, measurable/testable success criteria. For a bug: the root cause and fixed behavior.>
### Non-Goals
<Explicitly out of scope.>

## Proposal
<The desired outcome, no implementation details.>

### User Stories
#### Story 1
As a <user>, I want <capability>, so that <benefit>.
#### Story 2
<…>

### Core Features & Acceptance Criteria
<Each feature with concrete, testable acceptance criteria.>

### Notes / Constraints / Caveats
<Tech-stack preferences and constraints.>

### Boundaries
- **Always:** <…>
- **Ask first:** <…>
- **Never:** <…>

### Risks and Mitigations
<Key risks, each as `Risk → Mitigation`.>

## Design Details
### Commands
<Full executable build / test / lint / dev commands.>
### Project Structure
<Directory layout with short descriptions.>
### Code Style
<One real code snippet + key conventions.>
### Implementation Plan
> TODO — completed by `my-plan`.
### Test Plan
> TODO — completed by `my-plan`.

## Alternatives
<Other approaches considered, and why not.>

## Open Questions
<Anything unresolved that needs human input.>
```

## Phase 5 — Save, then offer to plan

1. Derive a short, **hyphen-separated** title (e.g. `user-auth-flow`).
2. **Ask how to track the spec** — this picks its directory:
   - **Commit (default)** → `specs/` — versioned; task check-offs ride `my-build`'s commits.
   - **Local only** → `.claude/specs/` — on disk, never committed; downstream `my-*` won't stage it. `.claude/`
     is usually gitignored; if this project doesn't ignore it, suggest adding it.
3. **Filename prefix** so specs sort sensibly:
   - **Issue-initiated** (Phase 1 resolved `the user's current request` to an issue) → `<dir>/<issue-number>-<title>.md`;
     also record the issue link in the spec (Summary or Motivation).
   - **Otherwise** → today's date (`date +%Y-%m-%d`) → `<dir>/<yyyy-mm-dd>-<title>.md`.
4. **Present the drafted spec and its filename; wait for confirmation** — your approval to write.
5. Save to `<dir>/<prefix>-<title>.md` (create the dir if missing). **File already exists → don't overwrite
   silently** — ask: overwrite, pick a new title, or switch to `my-plan` on the existing one. Confirm the path.
6. **Ask whether to run `my-plan` now.** If yes, continue into `my-plan` with this spec.
