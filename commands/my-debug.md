---
name: my-debug
description: Root-cause a bug and write a fix plan to .claude/debugs/, then hand off to /my-build. The lightweight local lane for a bug that needs no tracked spec.
argument-hint: "[bug description, error, or repro] [--assist codex|kimi]"
disable-model-invocation: true
---

# /my-debug

Diagnose and plan a fix for: **$ARGUMENTS**

Like `/my-plan`, this command **only writes one artifact** — a debug doc under `.claude/debugs/` — then hands to
`/my-build`. Stay read-only otherwise (only Phase 5 writes).

**Lane vs `/my-spec`.** `/my-debug` is the **lightweight, local** bug lane (throwaway artifact → build). A bug
that deserves a **versioned, tracked** spec goes through `/my-spec`'s Bug-fix path instead.

- **Language.** Write the artifact in **English**; talk to the user in their configured language.
- **Source lookup.** Read/trace source: **GitNexus** (if available) → **DeepWiki** → `grep`/`find`.

## Artifact — `.claude/debugs/<yyyy-mm-dd>-<title>.md`

- Always **local**, never staged.
- **`Status:`** — lifecycle trace; initial `Diagnosed`, then `Building` and `Built`, finally `Shipped`.
- Branch (in `/my-build`): always **`fix/<title>`**.

```markdown
# Debug: <Title>

Status: Diagnosed
Type: Bug fix

## Background
<Symptom, error text, environment, affected code/paths. The "what & where".>

## Reproduction / PoC
<The failing test or repro script that proves the bug — the concrete trigger.>

## Root Cause
<The confirmed underlying cause (not the symptom). If a cross-check ran, record which toolchain and its verdict.>

## Fix Plan
<Ordered `[ ]` tasks, vertically sliced, each with acceptance criteria + verification steps.
This IS /my-build's task list.>

## Test Plan
<Regression guard (fails without the fix, passes with it) + verification steps.>
```

## Entry — root cause supplied (`/my-triage` handoff)

`$ARGUMENTS` may name an existing `.claude/debugs/` artifact that **already** carries a filled **Root Cause**
*and* a `Local guard feasible:` line. That pair is a `/my-triage` handoff: the cause was locked from the
reporter's remote evidence, its *Reproduction / PoC* reads `Not reproducible locally — remote evidence:
<ledger path>, round-<k>/<file>`, and *Fix Plan* / *Test Plan* are `TODO`. Read the artifact and the ledger
round files it cites, then **start at Phase 3**, seeding any cross-check from the ledger's archived rounds
rather than a local reproduction, which by construction does not exist. Phase 4 takes Background / PoC /
Root Cause from the artifact, and Phase 5 fills that same file in place rather than opening a new one.

- **Both markers, or the ordinary entry.** An empty Root Cause, a Root Cause with no `Local guard feasible:`
  line, or a bug that merely arrived from an issue → Phase 1, and Phase 2 reproduces first as usual.
- **`Local guard feasible:` shapes the Test Plan; shipping never waits on hardware.** `yes, via <mechanism>`
  → that mechanism is the regression guard and the fix ships on it. `no — needs <hardware>` → the Test Plan
  records the gap and names the confirmation that would close it; `/my-triage` offers that hardware round as
  advisory, so the fix ships either way.

## Phase 1 — Frame the bug (read-only)

- Collect the symptom / error / repro hints from `$ARGUMENTS` and context.
- **Kick off the adversarial diagnosis early (gated, background) — apply `crosscheck`.** If the
  framing already shows complexity (multi-component, intermittent, high-risk, or an obviously
  non-obvious cause), background a **read-only** rescue subagent (`codex:codex-rescue` or
  `kimi:kimi-rescue`, per the selected toolchain) for an independent root-cause diagnosis **seeded
  from the symptom + reproduction only** — never your hypothesis, so it stays an independent second
  voice. It runs while you investigate in Phase 2; collect it in Phase 3.
  Borderline / looks simple → don't spend yet, decide in Phase 3.

## Phase 2 — Find the root cause

| Available | Use |
| --- | --- |
| `gitnexus-debugging` | invoke it first |
| otherwise | `agent-skills:debugging-and-error-recovery` |

**Reproduce reliably first, then localize.** Fix the underlying cause, not where it manifests.

## Phase 3 — Adversarial cross-check (complexity-gated)

- **Trigger:** the bug is **complex** — multi-component, intermittent, non-obvious root cause, or high-risk.
- **Barrier & reconcile — apply `crosscheck`.** Collect the diagnosis kicked off in Phase 1
  (`/<tool>:status` → `/<tool>:result`). If none was launched but Phase 2 revealed complexity, run one
  now (the rescue subagent — `codex:codex-rescue` or `kimi:kimi-rescue` — read-only, seeded from
  symptom + repro). Reconcile its verdict against yours per the skill (Step 7): lock the Root Cause
  only once you agree or can explain the divergence; surface any unresolved disagreement to the user.
  **Record its verdict in the artifact's Root Cause.**
- **Simple bug / neither tool available:** skip and note it.
- **Entered through the handoff:** Phases 1 and 2 never ran, so neither trigger above is observable. Use one
  that is — run a cross-check when the ledger's *Verdict* rests on **fewer than two** archived citations, or
  when *Ruled Out* is empty. Seed it from the archived rounds, and treat its verdict as an **annotation**: it
  records agreement or divergence beneath the Root Cause and never overwrites it. The cause was locked from
  evidence this cross-check cannot see, so a disagreement is a question for the user, not a rewrite.

## Phase 4 — Write the artifact

- **Background / PoC / Root Cause** from Phases 1–3.
- **Fix Plan** — ordered `[ ]` tasks, sliced **vertically** (one complete path per task), each carrying
  acceptance criteria + verification steps; order so every step leaves the system working.
- **Pin the build/test environment** — **local or remote** (if remote, its access method); **confirm with the
  user** (it decides how every command runs). A read-only smoke check is fine (write nothing to the tree).
- **Test Plan** — a regression guard that fails without the fix and passes with it, plus verification steps.

## Phase 5 — Present, confirm, write

1. Present the drafted artifact for **human review**.
2. **Wait for explicit confirmation** — the one pivotal question of this command.
3. Write `.claude/debugs/<yyyy-mm-dd>-<title>.md` (`date +%Y-%m-%d`; create the dir; **never stage it**). Confirm
   the saved path. **Entered through the handoff above → write back to the artifact you were given**, at its own
   path, filling *Fix Plan* and *Test Plan* in place. A second file would carry an empty Root Cause and no
   `Local guard feasible:` line, so re-entering on it would take the ordinary path and ask for the local
   reproduction that by construction does not exist.
4. **Offer the next step** (user may decline both):
   - **Compact, then build** — emit the three-line block per
     `~/.claude/references/my-workflow/compaction.md` (its `/my-debug` focus row).
   - **Build now** — continue into `/my-build` with this artifact as its target, keeping the current model.
