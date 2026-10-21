---
name: crosscheck
description: Get one independent read-only second opinion on a complex plan, diagnosis, or diff; do not auto-fix.
---

# Cross-check gate

A cross-check is one independent, read-only second voice. It is not routine linting, a write-capable delegation,
or a reason to hard-code another vendor's model into the workflow.

## 1. Gate the spend

Read and apply [Jev decision routing](../my-workflow/references/decision-routing.md).
Check disclosure restrictions before classifying or dispatching; an embargo disables external Jev calls and cross-checks.

Default to skip. Run one cross-check only when at least one condition holds:

- the change crosses packages, components, or a public interface;
- the design or root cause is novel, intermittent, or lacks an established repository pattern;
- the domain is high stakes: security, authorization, concurrency, migration/data loss, billing, or public API;
- the target artifact marks the work as risky; or
- the lead has low confidence or conflicting evidence; or
- the user explicitly requested an independent review.

If a trigger is already established, proceed without classification. Jev cannot veto an explicit review request or confirmed trigger.
For uncertain novelty, complexity, or risk, use one Jev `choice` over `run`, `skip`, and `needs_lead`.
Supply raw evidence and the trigger list above. Accept `run` or `skip` only at `confidence >= 0.8`.
Otherwise, or if Jev is off or unavailable, the lead applies this same gate. Reuse the result while evidence is unchanged.

Skip local, well-patterned, reversible work unless the user requested review. Do not repeat a cross-check over
unchanged evidence. Use at most one turn per workflow stage; a deliberately requested diff review may use one
bounded reviewer per isolated heavy task. `auto-research` may run one consolidated pass per new findings batch
and one final report pass under its own cost gate. Never make concurrent calls to the same provider.

## 2. Dispatch through `my-crew`

Before the first dispatch in each workflow stage, ask which coding agent should perform the review.
Offer only tools whose launch route is available, plus the choice to skip review. Do not preselect the current tool implicitly.
If the user already selected a tool for this stage, use it without asking again.
Reuse that choice for the stage's later reviews. At the next stage, ask again unless the user selected it for later stages too.
Keep the choice in the existing checkpoint across compaction; if it is lost, ask rather than infer it.

Apply `my-crew`'s review lane with that selection. Use the selected tool's configured default model unless the user specified one.
Resolve and report the actual model before dispatch, including when the selected tool is the lead's tool.
Honor a user-specified model or named subagent. If the selection or its actual model cannot be resolved or launched, report that.
Do not silently substitute a tool, model, or named subagent. Return without blocking ordinary work.

When Orca orchestration is reachable, `my-crew` uses a supervised read-only Task in a separate agent window.
Otherwise it uses the current host's native read-only subagent only if that route can honor the selected tool and model.
The native route has an independent context but may not have a separate terminal window.
Do not use an installed bridge plugin as a review route.

Read `~/.agents/skills/my-workflow/references/agent-runtime.md` before dispatch. Apply `model-routing.md`'s reviewer rules.

## 3. Select the review shape

- Design with no diff → critique the proposal and surface risks/test scenarios.
- Diagnosis with no fix → independently localize from symptom and reproduction.
- One bounded factual question → foreground read-only query.
- Real diff → defect review against the frozen diff.
- Real diff whose approach needs challenging → adversarial review focused on that approach.

Do not use a diff reviewer before a diff exists. Frame every route as review, diagnosis, or research and explicitly
forbid edits, staging, commits, pushes, and external mutations.

## 4. Preserve independence

Seed the worker with raw evidence: symptom plus reproduction, frozen diff, or the pre-existing design text. Do
not include the lead's finished conclusion. State grounding requirements, the base revision, and what counts as
fact versus inference.

Run in the background only when the lead has independent work to do; otherwise wait. Before starting another
job on the same provider, collect or settle any existing one. Settled REQUIRES both halves: the result in hand
and the worker no longer running.

## 5. Reconcile and stop

- Preserve the second opinion's evidence boundaries and severity ordering.
- Agreement → proceed.
- Disagreement → investigate only the divergence, explain the reconciled verdict, and surface unresolved
  disagreement to the user.
- Spot-check branch-sized findings against the actual source and discard stale or false positives.
- Never auto-apply suggested fixes. Present material findings and ask which to accept when the workflow reserves
  that decision for the user. The current lead owns every resulting edit.
- The stage is not done while a worker this cross-check started is still alive. Reclaim it per `agent-runtime.md`
  before handing the stage on, whichever `my-crew` route produced the second opinion.
