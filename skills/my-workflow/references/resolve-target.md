# Resolving a my-* target

Shared by `my-plan`, `my-build`, `my-ship`. A **target** is a **spec** (`specs/` committed, or
`.claude/specs/` local) or a **debug artifact** (`.claude/debugs/`, always local).

## Which directories

| Skill | Searches |
| --- | --- |
| `my-plan` | `specs/`, `.claude/specs/` (specs only — debug artifacts belong to `my-debug`) |
| `my-build`, `my-ship` | `specs/`, `.claude/specs/`, `.claude/debugs/` |

## Resolution

From the selector (`the user's current request` minus any mode token such as `auto` / `team`):

- **path / full filename** → use as-is.
- **bare title** → match `<dir>/*-<title>.md` (prefixed by date or issue number); also accept legacy
  `<dir>/<title>.md`. Several match → list them and ask.
- **empty** → exactly one target across the searched dirs → use it; else list and ask.

## Missing file

- `my-plan`, `my-build` → **stop and hand back** to `my-spec` (or `my-debug` for a bug) to initialize it.
  Offer the correct skill and continue only when the user has already authorized the next workflow stage.
  Requirements come from the target, never from invention.
- `my-ship` → **target-optional; never block.** Only when the selector *explicitly names* a target that
  doesn't exist, offer (don't force) `my-spec` / `my-debug`, or ship as-is on the user's say-so. Bare/empty
  with none found → **no-target mode**, ship from the branch diff.

## Status is a trace, not a gate

`Status:` records lifecycle (`Specified` → `Planned` → `Building` → `Built` → `Shipped`; debug artifacts start
at `Diagnosed`). Judge the target's real state from its **content** — does the Implementation Plan / Fix Plan
carry `[ ]` tasks, does the Test Plan still hold `TODO` or `<…>` placeholders. Content contradicts the line →
trust content and fix the line in passing.

## Tracking mode

Derived from the directory, and it governs staging for the rest of the skill:

- `specs/` → **committed**: target edits are staged with the work.
- `.claude/specs/`, `.claude/debugs/` → **local**: target edits land on disk but are **never staged**.

## Security mode

A target carrying a `Disclosure:` header line belongs to `my-advisory`. Read that skill's **Boundaries** and
the phase matching yours before continuing: `embargoed` governs what may be written into a branch name, a commit
message, a PR body, or anything sent to an external tool.
