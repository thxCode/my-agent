# Model routing — capability classes, not vendor names

Shared workflow instructions never prescribe a concrete model name or a vendor-specific model-switch command.
Model catalogs, aliases, and supported reasoning controls differ across Claude, Codex, and Kimi and change over
time.

## Defaults

- Inherit the current session's model and reasoning setting.
- Do not switch models merely because a workflow changes phase or compacts context.
- Keep the model and reasoning setting stable during a live session when the host's prompt cache keys include
  them. Change either at a natural cache boundary, such as a fresh session or compaction, unless the current
  capability is genuinely insufficient.
- If the user explicitly selected a model, preserve it unless it cannot perform the required task; explain the
  incompatibility before proposing a change.

## Capability classes

When a different capability would materially help, recommend one class and let the current host resolve it from
its live model catalog:

- **fast:** mechanical edits, bounded searches, and deterministic test execution;
- **balanced:** ordinary implementation, planning, and review;
- **strongest:** ambiguous architecture, non-obvious debugging, security, migrations, or a decision with a large
  blast radius.

State why the class is needed. Never encode a provider model name or alias in a shared workflow. Never assume
that model-selection commands, reasoning effort, or thinking controls have equivalent syntax or semantics across
hosts.

## Calibrate, do not guess

Choose reasoning effort from task evidence: low for bounded mechanical work, ordinary/default for routine work,
and higher only when ambiguity, risk, or failed verification justifies it. For repeated workloads, compare
representative outcomes across supported settings and keep the least expensive setting that meets the acceptance
criteria. Do not treat maximum effort as a universal quality setting.

## Workers

Native subagents inherit the parent model by default. Use a cheaper/faster worker only for a narrow role whose
contract removes design judgment. Orca worker creation chooses the agent provider and placement; any model choice
is resolved by that provider's current configuration, not by the shared Task spec.
