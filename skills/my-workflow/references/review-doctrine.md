# Review doctrine — what a finding must carry, and what the pass costs

Distilled from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[mattpocock/skills](https://github.com/mattpocock/skills) and
[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (all MIT); see `CREDITS.md` for what
came from where.

Governs the **Standards** axis of `my-build`'s end-of-build review and `my-ship`'s branch review. The Spec
axis has its own contract in `roles/spec-reviewer.md`; that the two run in separate contexts and are never
merged or re-ranked is `my-build`'s rule, not this file's.

Nothing here restates a neighbour: the smell catalog is `smells.md`, the spend gate for an independent second
opinion is `crosscheck`, capability classes are `model-routing.md`, and overturning a written decision is
`decisions.md`.

## The project outranks this file

Run what the project already wrote before running anything here, and let it suppress this baseline where the
two disagree. In descending authority: a review skill the project ships itself (a `design-review` or
equivalent under its `.claude/skills/`), then `CODING_STANDARDS.md` / `CONTRIBUTING.md` / the target's **Code
Style**, then its ADRs, then this doctrine. A project-specific rule naming the project's own components beats
a general principle about components.

**Skip anything tooling already enforces.** A finding a linter, formatter, type checker, or CI job would have
raised is spend with no yield — the gate already exists and the author will see it. When you catch a
*mechanical* rule that no tool enforces (a banned API, an import shape, a file-location rule), the finding is
that the check is missing, not that the line is wrong.

An ADR that forbids the thing you want to propose is a decision, not an oversight. Surface it only when the
friction is real enough to warrant reopening the ADR, and say that is what you are asking for.

## A finding names its replacement

One line per finding: `<file>:L<n>: <tag> <what>. <replacement>.`

- `bug:` — it produces a wrong result or crashes. Replacement: the corrected behaviour.
- `delete:` — dead code, unused flexibility, a speculative feature. Replacement: nothing.
- `stdlib:` — hand-rolled thing the standard library ships. Name the function.
- `native:` — a dependency or code doing what the platform already does. Name the feature.
- `yagni:` — an abstraction with one implementation, config nobody sets, a layer with one caller.
- `shrink:` — same logic, fewer lines. Show the shorter form.

Four of the six do not typecheck as a finding without a concrete replacement: naming the replacement is what
separates a review from a misgiving. Compare

    L12-38: this EmailValidator class might be more complex than necessary, have you considered
            whether all these rules are needed at this stage?

with

    L12-38: stdlib: 27-line validator class. "@" in the address, one line; the confirmation mail is
            the real validation.

The first costs the author a research project. The second costs them a decision.

Rank by leverage, worst first. One structural problem and ten nits means the structural problem IS the review.

## Split the reviewers by evidence, not by topic

Topical axes — correctness, readability, security, performance — all read the same bytes, so they find the
same things and miss the same things. Split by what each reviewer is allowed to look at instead:

| Reviewer | Sees | Finds what the others cannot |
| --- | --- | --- |
| Conventions | the project's own standards files and review skill | breaches of rules this repository actually wrote down |
| Diff-only | the diff, and nothing else | defects visible in the change itself, unbiased by why it was made |
| History | `git log` and `git blame` on the touched lines | a fix that re-breaks what an earlier commit deliberately fixed |
| Prior review | earlier pull requests touching these files, and their comments | a point already argued and settled, being relitigated or repeated |
| Comments | the code comments in the modified files | a change that contradicts guidance written beside the code |

Pick the subset the change earns. Conventions and Diff-only are the floor; History and Prior review pay for
themselves on a file with a long past, and not on a new one.

**No reviewer spawns another reviewer.** Say so in the brief. Without that line a reviewer can rediscover the
review and fan out again; upstream has seen one pass reach fifty-plus agents. Keep each reviewer's report
under 400 words.

## Find with judgment, verify with a cheap pass

Finding and confirming are different jobs, and the second one has no design judgment in it — which makes it
the narrow role `model-routing.md` allows a `fast` worker to take. Run every candidate finding through it
before anything reaches the user.

The verifier scores 0-100 for whether the defect is real, and only 80 and above survives. It must be able to
state a **failure scenario** — concrete inputs or state, leading to a wrong output or a crash. A finding that
cannot be given one is an opinion wearing a severity label.

Drop these without spending a verification on them:

- a problem that predates the diff, or lives on a line the change did not touch;
- anything a linter, type checker, compiler, or CI job would catch;
- a rule the code explicitly silences with an ignore comment, unless the silencing is itself the finding;
- a behaviour change that is plainly part of what the change set out to do;
- a nit a senior engineer would not raise out loud.

Two stages beat one long pass on both axes: the finder can range wide because false positives are cheap, and
the survivor set is small enough to read.

## A clean axis is a result

"No findings" is an outcome, not a failed review. Say it plainly and stop.

Two signals that the pass has gone wrong in opposite directions:

- **Theatre.** Across two or more rounds where the finder surfaced substantial candidates, nothing survived
  verification. You are validating, not reviewing. Stop and report that instead.
- **Grinding.** There is no convergence guarantee. Do not re-run until it comes back clean; it will not. A
  pass produces a list of leads, and the ones with a cited rule or a failure scenario behind them are the
  work.

## What the pass costs

A diff that touches two files or fewer, stays under 50 lines, and goes nowhere near authentication, payments,
data access, or configuration earns the floor and nothing beyond it — Conventions and Diff-only, no further
reviewers. Anything else, fan out.

Size is itself a finding. Around 300 changed lines is reviewable as one logical change; past roughly 1000,
the right report is "split this", because a review nobody can hold in their head approves by exhaustion.

## Deliberate shortcuts leave a marker

The build lane requires the simplest thing that satisfies acceptance, which means every build deliberately
declines to handle something. Unrecorded, those decisions become indistinguishable from oversights within a
month.

When a change accepts a known ceiling — a global lock, a linear scan where an index belongs, a naive
heuristic — leave a comment naming both the ceiling and what would justify revisiting it:

    # shortcut: global lock, per-account locks if throughput matters

Harvest them with `command grep -rnE '(#|//|--) ?shortcut:'`, anchored on the comment prefix so prose about
the convention stays out of the ledger. A marker naming a ceiling but no trigger is the one that rots; report
those separately.

**The Standards axis runs that harvest over the change under review and reports what it added**, so a ceiling
accepted this round is visible at the one gate still able to question it. A marker nobody ever collects is
the deferral it was meant to prevent.

This is the counterweight to `yagni:` and `delete:`, not an exception to them — a shortcut with a trigger is
a decision, and one without is a deferral nobody owns.
