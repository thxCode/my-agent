---
name: crosscheck
description: Get one independent read-only second opinion on a complex plan, diagnosis, or diff; do not auto-fix.
---

# Cross-check gate

A cross-check is one independent, read-only second voice. It is not routine linting, a write-capable delegation,
or a reason to hard-code another vendor's model into the workflow.

## 1. Gate the spend

Default to skip. Run one cross-check only when at least one condition holds:

- the change crosses packages, components, or a public interface;
- the design or root cause is novel, intermittent, or lacks an established repository pattern;
- the domain is high stakes: security, authorization, concurrency, migration/data loss, billing, or public API;
- the target artifact marks the work as risky; or
- the lead has low confidence or conflicting evidence.

Skip local, well-patterned, reversible work. Do not repeat a cross-check over unchanged evidence. Use at most one
turn per workflow stage; a deliberately requested diff review may use one bounded reviewer per isolated heavy
task, never concurrent calls to the same provider.

## 2. Choose an independent route

Honor an explicitly requested provider. Otherwise prefer an available provider different from the current lead.
Probe availability once per session and cache the result. If no independent provider is available, say so and
continue without blocking ordinary work.

Use the narrowest available route:

1. an installed read-only reviewer/rescue integration for that provider;
2. Orca `orchestration` with a supervised read-only Task and a different agent provider; or
3. a host-native read-only subagent only when independent context, rather than provider diversity, is sufficient.

Read `~/.agents/skills/my-workflow/references/agent-runtime.md` before using Orca or native subagents. Apply
`model-routing.md`: inherit defaults and request a capability class only when justified; never prescribe a model
name or assume shared model flags.

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
job on the same provider, collect or settle any existing one.

## 5. Reconcile and stop

- Preserve the second opinion's evidence boundaries and severity ordering.
- Agreement → proceed.
- Disagreement → investigate only the divergence, explain the reconciled verdict, and surface unresolved
  disagreement to the user.
- Spot-check branch-sized findings against the actual source and discard stale or false positives.
- Never auto-apply suggested fixes. Present material findings and ask which to accept when the workflow reserves
  that decision for the user. The current lead owns every resulting edit.
