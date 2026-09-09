# Context checkpoint

Shared by `my-plan`, `my-debug`, `my-build`, `my-ship`, and `my-crew`. Claude, Codex, and Kimi expose different
context meters and reset/compaction controls, so this reference defines the durable state, not a host command.

## When to checkpoint

Checkpoint when the host reports substantial context pressure, or when the agent starts losing state, rereading
the same material, or confusing completed and pending work. Do not use fixed token/byte thresholds copied from
another host.

`my-build` is strict: if pressure appears with tasks still pending, write the checkpoint before continuing in a
fresh or compacted context. Auto/team mode does not bypass this requirement.

## Durable checkpoint

Write a local resume file under `.claude/handoffs/` containing:

- workflow skill and target artifact path;
- branch, base revision, and dirty-state ownership;
- completed and pending tasks/phases;
- accepted decisions, rejected alternatives, and unresolved questions;
- codebase facts that are expensive to rediscover, with paths;
- verification already run and the exact next action.

For `my-plan` and `my-debug`, the target artifact itself remains primary; the resume file should point to it rather
than duplicate its contents. For `my-build` and `my-ship`, git holds completed diffs and the resume file holds only
coordination state.

## Resume

Use the current host's documented compaction or fresh-session mechanism. Do not prescribe a model switch; apply
`model-routing.md` only if the next phase independently warrants another capability class. On resume, read the
target, git state, and resume file before taking action.

## Orca workers

A coordinator cannot assume a child preserved the right context. Ask the worker to write its own resume file,
read and verify that file, then use the version-matched Orca guide to refresh or replace the worker. Preserve the
Task/Dispatch contract when the live guide supports it; never infer completion from a reset terminal.
