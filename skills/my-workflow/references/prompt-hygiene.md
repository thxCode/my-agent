# Prompt hygiene

Use this reference when creating or refining a shared skill, agent contract, or workflow reference.

## Keep the reusable prefix stable

When a host caches prompt prefixes, exact prefix changes can discard the cache. Keep durable policy and stable
tool contracts in skill files; keep timestamps, run ids, branch state, and other changing values in the user
message or a referenced artifact. Avoid reordering equivalent tool or instruction blocks. During a live session,
apply `model-routing.md` before changing the model or reasoning setting.

This is a layout rule, not a promise that every provider implements the same cache. Provider-specific cache
controls belong in provider-specific integrations, not in the shared `my-*` skills.

## Remove inherited prompt patches

Flag instructions whose only purpose is to compensate for an older model:

- generic requests to verify repeatedly or be maximally thorough;
- mandatory private reasoning, scratchpad, or step-count templates;
- stale examples that teach an obsolete failure workaround;
- conflicting rules whose precedence is undefined;
- retired model, effort, or thinking controls;
- repeated context already available through a durable artifact.

Keep concrete verification commands, acceptance criteria, safety gates, and recovery checks. They constrain an
observable action or result rather than demanding extra reasoning for its own sake.

## Optimize against evidence

For a repeated workflow, measure representative success criteria, latency, and cost before changing capability
or effort. Prefer the smallest prompt and lowest effort that still meet the baseline. A cheaper run that skips
required evidence is not an optimization.
