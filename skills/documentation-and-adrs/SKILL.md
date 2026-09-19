---
name: documentation-and-adrs
description: Record why a decision was made, in the project's existing form; ADRs are superseded, never edited.
---

# Documentation and ADRs

Distilled from [`documentation-and-adrs`](https://github.com/addyosmani/agent-skills/tree/main/skills/documentation-and-adrs)
(MIT, Copyright (c) 2025 Addy Osmani); see `CREDITS.md`.

Read by `my-ship` once a change is judged architecturally significant. The code already records *what* it
does; what gets lost is *why this and not the alternative*, and that is the only thing worth writing down.

## Match the existing convention before inventing one

Look for what the project already does — `docs/adr/`, `docs/decisions/`, a `DECISIONS.md`, a wiki, long-form
commit messages. Adopt its location, filename pattern, numbering, and section headings exactly, even where
you would have structured it differently. A second convention beside the first means neither is where the
next person looks.

Nothing there at all? `docs/adr/NNNN-kebab-title.md` with sequential numbering is a safe default, and say in
your report that you established it.

## What earns an ADR

A decision earns one when reversing it later would be expensive, and when a competent reader would otherwise
ask "why on earth is it like this": choosing between real alternatives with a real trade-off, adopting or
dropping a dependency that shapes the design, a boundary or data-ownership decision, a deliberate departure
from a project norm.

A decision does not earn one merely because it was hard to make. If the alternative would be obviously worse
to anyone reading the code, the code is the documentation.

## The sections that carry the weight

Context, Decision, Alternatives, Consequences — and the last two are where the value is.

**Alternatives** names each option actually considered and why it lost, in one or two lines. An ADR listing
only the winner reads as advocacy and tells a future reader nothing about whether the reasoning still holds.

**Consequences** states what this costs, not just what it buys. Include the ones you accepted knowingly; an
ADR with no downsides section was not a decision, it was a preference.

Date it and state its status. Keep it short enough to read in full — an ADR nobody finishes is worth less
than three honest paragraphs.

## Supersede, never rewrite

A decision that no longer holds gets a new ADR that references the old one, and the old one's status changes
to superseded with a pointer forward. Editing the original destroys the record of what was believed at the
time, which is the entire reason the file exists. Deleting it is worse: the next person re-derives the
rejected option from scratch.

## Comments explain why, the code explains what

In-line, write down what the code cannot say for itself: why a non-obvious approach was chosen, which
external constraint forces this shape, what breaks if the order changes, the bug a guard exists to prevent.

A comment restating the line beneath it is maintenance debt — it will drift out of sync and then actively
mislead. Where a comment is about a known accepted limit rather than a rationale, use the `shortcut:` marker
from `~/.agents/skills/my-workflow/references/review-doctrine.md` so it lands in the ledger instead.
