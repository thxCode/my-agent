# Program records and handbacks

Read this reference when starting, resuming, or closing a `my-loop` program. Keep the records compact enough for
a new coordinator to read before acting. The examples show fields, not fixed project conventions. Write every
record and handback per `~/.agents/skills/my-workflow/references/writing-style.md` (80% ASD-STE100).

## `STANDARD.md`: the task-specific contract

Write once at kickoff and amend when a decision changes the contract. The coordinator is its only writer.
Record a replacement ruling in `HISTORY.md` before changing a rule; do not silently rewrite authorization.

```markdown
# Standard: <program>

## Source and outcome
- Report: <absolute path or SOURCE.md; content hash or snapshot location>
- Repository and target branch: <paths and branch>
- Goal and completion evidence: <observable predicates>
- Provisional then frozen spec coordinates and dependency tranches: <stable IDs and ordering rule>
- PoC gate: <PLAN and RESULT paths, checks, acceptance authority, consequence of inconclusive results>

## Ownership and files
- Program directory: <absolute path>
- Coordinator writes: STANDARD.md, STATUS.md, HISTORY.md, live report, HANDOFF.md
- Worker writes: its HANDBACK files, SUMMARY.md, raw evidence, assigned branch and repository spec
- Artifacts that are local only: <paths>; repository spec location: <path convention>
- Worker provider and placement: <chosen provider, supervised runtime, worktree rule>

## Authorization and human gates
- Coordinator may approve: <spec draft / plan / build and ship gates / e2e / history rewrite / push and PR /
  review replies / merge, each explicit>
- Worker may mutate externally: <exact actions or none>
- User-reserved decisions: <actions and review triggers>
- Review budget: <number; default four effective feedback rounds>
- Expected review sources: <which sources must finish on the current head; waiver authority>
- Resource, spending, cleanup, and concurrency limits: <concrete limits and owners>

## Project rules and overrides
- Applicable instructions and stage skills: <paths>
- Overrides of a stage's default confirmation or placement rule: <rule, source of user authorization, reason>
- Validation and evidence requirements: <checks>
```

An authorization entry grants only the named action inside the named program. If no entry grants merge, the
coordinator presents a concrete merge candidate to the user. A worker cannot grant authority by reporting a
decision. Keep host-specific commands and project infrastructure settings here, not in the shared skill.

## `STATUS.md`: current state and next action

Use fixed sections so a replacement coordinator can find the same facts. Every active row names its next owner;
every negative assertion says how it was checked. Remove stale phase detail after archiving it in `HISTORY.md`.

```markdown
# Status: <program>

## Current phase and next action
<One current statement; next actor, action, and gate.>

## Resources
| Need | PoC or spec unlocked | Availability and evidence | Provider | Limit and cleanup | Next action |
| --- | --- | --- | --- | --- | --- |

## PoC
| Check | Required resource | Result and evidence | Impacted specs | Next gate |
| --- | --- | --- | --- | --- |

## Decisions
| ID | Question or ruling | State | Owner or next gate |
| --- | --- | --- | --- |

## Specs and tranches
| ID | Outcome | Depends on | Stage | Worker/branch/PR | Next gate |
| --- | --- | --- | --- | --- | --- |

## Pending after merge
| PR and merged head | Check, review, or summary | Observed state | Affected work | Owner and next check |
| --- | --- | --- | --- | --- |

## Issues and risks
| ID | Provenance | Closure criterion | Source | Assigned to | State and next action |
| --- | --- | --- | --- | --- | --- |

## Active windows and worktrees
| Task | Runtime handle | Worktree/branch | Owned by | State and next gate |
| --- | --- | --- | --- | --- |

## Needs user
<Exact reviewable question, options, recommended choice, and blocked dependent work; or None.>
```

An issue's `Assigned to` is never blank. Use a stable local ID until an external issue exists, then retain the
local ID as an alias. Distinguish measured, reported, and inferred findings. Do not mark a task complete from a
handback alone; compare the actual target, diff, tests, PR, and runtime completion record.

Resource rows describe access and limits, never credential values. Update a row when a resource is granted,
unavailable, consumed, or cleaned up. A PoC row has `pass`, `fail`, or `inconclusive`; an inconclusive result
names the missing evidence and blocks the affected spec until explicitly resolved.

## `HISTORY.md`: append-only evidence

Append one event per completed gate, ruling, issue assignment, merge, or correction. Never erase a failed or
voided run; explain why it does or does not support the conclusion. Corrections point to the old entry.

```markdown
## <date or sequence> <coordinate>: <event>

- Previous state: <the STATUS statement being superseded>
- Result and decision maker: <what happened, who ruled, and authorization source>
- Evidence: <artifact paths, exact branch/commit/PR, commands and observed results>
- Deviation or uncertainty: <what differs from the plan, or None>
- Synced: <STATUS, report conclusion, issue owner, next HANDOFF; explain omissions>
```

## Worker files

The coordinator writes `poc/PLAN.md` and `poc/HANDOFF.md`. The PLAN is one pre-spec task with a row for each
costly unknown, and is presented with the resource request at kickoff. Its HANDOFF names the PLAN checks,
granted resources and limits, owned paths, raw evidence location, and escalation conditions. The worker writes
`poc/RESULT.md` and `poc/raw/` evidence. The coordinator verifies each row before freezing the spec map.

```markdown
# PoC plan: <program>

| Check | Question and source | Resource and procedure | Pass | Fail | Inconclusive | Spec decision |
| --- | --- | --- | --- | --- | --- | --- |
```

```markdown
# PoC result: <program>

| Check | Outcome | Observed evidence | Effect on specs |
| --- | --- | --- | --- |

Resources used and disposition: <actual usage, cleaned or retained, owner and expiry>
```

The coordinator writes `spec-<ID>/HANDOFF.md` before dispatch. The worker writes a new
`spec-<ID>/HANDBACK-<sequence>-<gate>.md` at each gate and `spec-<ID>/SUMMARY.md` after merge, including a
user-initiated merge. Never overwrite an earlier handback. Keep the spec body in the repository's `my-spec`
location. For a standalone issue or validation batch, use the same shape under its own stable coordinate.

Before writing a handoff, read and apply [spec-content.md](../../my-workflow/references/spec-content.md)
for the boundary between program-local records and repository artifacts.

```markdown
# Handoff: <coordinate and outcome>

To: <worker> | From: <coordinator> | Program: <absolute path>
Worktree: <absolute path> | Branch/base: <branch and SHA>
Source: <report sections, applicable PoC check IDs/results/evidence, recorded decisions>
Repository references: read and apply ~/.agents/skills/my-workflow/references/spec-content.md before writing repository artifacts.
Assigned issues: <IDs, closure criteria, fix or re-evaluate>
Stages: <first unfinished stage through permitted last stage>
Owns: <paths> | Excludes: <paths and actions>
Acceptance and verify: <observable outcomes and commands>
Authorization and review budget: <exact charter excerpt>
Escalate: <human gate, scope change, conflicting evidence, blocker, budget limit>
New issue notice: <immediate channel to coordinator, independent of stage gates>
Handback: <absolute directory and required gate>
```

```markdown
# Handback: <coordinate and gate>

Status: <complete / blocked / ruling needed>
Changed: <paths, commit SHA, PR and current head>
Verified: <commands, environment shape, results, raw evidence paths>
Findings and issues: <IDs, provenance, closure criterion, assigned owner>
Outside owns or plan: <difference or None>
For coordinator: <specific ruling or check needed>
Next: <action and owner>
```

```markdown
# Summary: <coordinate>

Delivered: <spec, PR, merge commit, behavior and docs>
Verified: <tests and evidence, including failed or voided runs>
Departures: <spec or plan changes and rulings>
Residuals: <issue ID, owner, closure criterion or deferral trigger>
Pending after merge: <check or review, current state, owner and next check; or None>
Report changes: <claims confirmed, overturned, or still uncertain>
```

## Gate checks

- Before the first spec: compare the provisional spec map with the resource inventory and PoC PLAN. Confirm
  that granted resources match the request, then verify each RESULT row against its criterion, controls where
  applicable, and raw evidence. Record resource readiness, accepted conclusions, report corrections, and the
  frozen spec map.
- Before dispatch: confirm the source and charter, next spec dependencies, assigned issues, owned paths, base,
  and a completion channel. Verify the worker can read the absolute program path.
- At a stage handback: read the artifact and compare it with the stage's acceptance and actual repository or
  runtime state. Run the shared spec content audit on any spec produced or changed before accepting the gate;
  then update `STATUS.md` and append `HISTORY.md` in the same coordination turn.
- Before a coordinator merge: read the current PR head and all required check conclusions, review state,
  completed current-head review from expected sources, thread state, and charter. A green summary or the
  worker's claim is insufficient.
- After any verified merge, including one reported by the user: record the actual head and merge commit.
  Reconcile the PR and latest handback now, then match each `SUMMARY.md` residual to a `STATUS.md` owner and each
  report-changing conclusion to the live report when the summary arrives. Record pending, skipped, or canceled
  checks, unfinished reviews, and a missing summary with an owner and next check. Hand off the next ready spec
  without waiting for unrelated late CI or summary work. Route later failures or findings to an assigned issue
  or follow-up, and release owned workers after handback and cleanup.
- At takeover and final closure: compare ledger rows with actual branches, PRs, issues, and runtime handles.
  Test the lookup against a known current or historical issue or worker before trusting a zero-hit audit. Do not
  close a program with an unassigned issue or an unverified final matrix row.
