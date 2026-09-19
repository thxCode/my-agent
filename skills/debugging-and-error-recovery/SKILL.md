---
name: debugging-and-error-recovery
description: Find a bug's root cause from a reproduction rather than a guess; reproduce, localize, reduce, fix, guard.
---

# Debugging and error recovery

Distilled from [`debugging-and-error-recovery`](https://github.com/addyosmani/agent-skills/tree/main/skills/debugging-and-error-recovery)
(MIT, Copyright (c) 2025 Addy Osmani) and [`diagnosing-bugs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs)
(MIT, Copyright (c) 2026 Matt Pocock); see `CREDITS.md`.

The fallback root-cause method for `my-debug` and `my-spec` when `gitnexus-debugging` is not available. It
buys one thing: a fix aimed at the cause rather than at the symptom that got reported.

## The gate: a red-capable command first

Name **one command you have already run** that fails because of this bug, and show its invocation and output.
Reading code to build a theory before that command exists is the failure this whole method prevents — you
will find something that looks wrong, fix it, and never learn whether it was the bug.

The command has to be deterministic (same result on repeat), fast enough to run many times, and runnable by
an agent without a human in the loop. Cannot get one? That is the finding. Report it and stop; an
intermittent failure needs `my-triage`'s evidence ledger, not this.

## Localize, by bisection over whatever varies

The failing command is now an oracle, so stop reading and start halving. Bisect over whichever axis is
cheapest to split: `git bisect` over history when it used to work, input size when a large payload fails,
the module graph when neither applies. Each step must leave you with strictly less code that can be at fault.

**Reduce before you diagnose.** Strip the reproduction until every remaining line is load-bearing. A
five-line reproduction usually names its own cause; a five-hundred-line one hides it.

## Rank hypotheses before testing any of them

Write down **three to five** candidate causes before you test the first. Generating one at a time anchors you
on whichever plausible idea arrived first, and the rest of the session becomes a search for its confirmation.

Each candidate states a prediction that could falsify it: *if X is the cause, then changing Y makes the
failure disappear*. A candidate you cannot phrase that way is a hunch — sharpen it or drop it.

## Fix the cause, at the layer that owns it

Before editing, find every caller of the function you are about to change. A guard in the one shared function
is both the smaller diff and the real fix; patching only the path the report names leaves every sibling
caller broken and the next report on its way.

Suspect the fix is a symptom patch? Ask what has to be true for this bug to exist. If the answer is "the
caller passed something the callee never promised to handle", the contract is the bug.

## Guard, then verify end to end

The regression test goes in **before** the fix and must fail for the reported reason — a test that passes
against the broken code guards nothing. Then: the specific test, the full suite for regressions, and the
build.

Tag any temporary debug output with one unique prefix so cleanup is a single search. Leaving instrumentation
behind is how a debugging session becomes a review finding.
