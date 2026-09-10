---
name: my-workflow
description: Route software work to the appropriate my-* workflow stage or specialized lane.
---

# my-workflow

Use this skill when the user asks to use the personal workflow, names a `my-*` stage, or asks for an end-to-end
engineering workflow rather than one isolated action.

## Choose one entry lane

- Report that cannot be reproduced locally → `my-triage`.
- Confirmed local bug that does not need a tracked spec → `my-debug`.
- Feature, tracked bug, or GitHub issue that needs a durable proposal → `my-spec`, then `my-plan`.
- Planned spec or debug artifact ready to implement → `my-build`.
- Built branch ready for final validation and PR preparation → `my-ship`.
- Vulnerability report → `my-advisory`; its disclosure rules override the ordinary lanes.
- Full ownership transfer to another agent/window → `my-handoff`.
- Supervised multi-agent work or a task DAG → `my-crew`.
- Audit the workflow assets themselves → `my-refine`.

Read and follow the selected sibling skill's `SKILL.md`. Do not make the user restate context already present in
the conversation or in the workflow artifact. At a stage boundary, offer the next stage and continue in the same
turn when the user has already authorized end-to-end or unattended execution.

## Explicit-only entries

`my-advisory`, `my-debug`, `my-refine`, `my-spec`, and `my-triage` preserve their original user-only invocation
policy. If this router was selected implicitly, do not read or enter one of those skills unless the user already
invoked that skill explicitly through the current host. Recommend the host's explicit skill syntax and stop at
that boundary. Once explicitly started, the selected workflow may follow its documented downstream transitions.

## Runtime boundary

Before delegating or opening another agent window, read
`~/.agents/skills/my-workflow/references/agent-runtime.md`. It defines the portable boundary between
Claude, Codex, Kimi, and Orca. For ordinary single-agent work, stay in the current session.
