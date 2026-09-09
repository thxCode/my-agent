# Skill craft — what to cut, and what to leave alone

Read by `my-refine`. Also worth reading by hand before writing a new skill or reference.

A skill exists to wrangle determinism out of a stochastic system. **Predictability** — the agent taking the
same *process* every run — is the root virtue, and every rule below serves it. Distilled from
[`writing-great-skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills);
its `GLOSSARY.md` carries the full treatment.

## What to cut

Each is *what it is* → *what to do*. Check every line against all six.

- **No-op** — a line the model already obeys by default, so you pay load to say nothing. → Delete. The test is
  behavioural, not aesthetic: **relative to the default, what does this line change?** A weak leading word
  (*be thorough* to an already-thorough agent) is a no-op; the fix is a stronger word, not a longer sentence.
- **Duplication** — the same meaning in more than one place. → Collapse to one authoritative home. It costs
  maintenance, costs tokens, and inflates the meaning's prominence past its real rank. **Test it against
  *What to leave alone* below before cutting** — several shapes look like duplication and aren't.
- **Sediment** — stale layers that settled because adding felt safe and removing felt risky. → Delete. This is
  the default fate of any asset without a pruning pass.
- **Sprawl** — simply too long, even when every line is live and unique. → Push reference down behind a
  pointer, or split by branch, so each path carries only what it needs.
- **Negation** — steering by prohibition drags the banned behaviour into context and makes it *more* available.
  *Don't think of an elephant* names the elephant. → State the target behaviour instead, so the banned one is
  never spoken. Keep a prohibition only as a hard guardrail you can't phrase positively — and pair it with what
  to do instead.
- **Lost relevance** — the line no longer bears on what the asset does, or describes a world that has moved. →
  Delete.

## Where a line belongs

Three rungs, ranked by how immediately the agent needs the material: an **in-file step** (an ordered action),
**in-file reference** (a rule or fact consulted on demand), and **disclosed reference** (a separate file behind
a pointer). Push down whatever you can; the top rung has to stay legible.

A **branch** — a distinct path a run can take — is the disclosure test: inline what every branch needs, disclose
what only some branches reach. A pointer's **wording**, not its target, decides how reliably the agent follows
it; if must-read material is being missed, sharpen the wording before pulling it back inline.

**Co-location** decides what sits *beside* a line once it lands: a concept's definition, rules, and caveats
under one heading, so reading one part brings its neighbours.

## Leading words

A **leading word** is a compact concept already in the model's pretraining that the agent thinks *with* while
running the asset — *tracer bullet*, *fog of war*, *frontier*, *red*. Repeated as a token (never re-explained as
a sentence) it accumulates a distributed definition and anchors a whole region of behaviour in the fewest
tokens. Prefer a pretrained word to a coined one: a made-up term recruits no priors, so you spend in definition
what an existing word gives free.

Hunt for passages that collapse into one: a triad spelled out at three sites, a paragraph gesturing at a single
idea. You win twice — fewer tokens, and a sharper hook.

## What to leave alone

**Burden of proof: a cut has to state what makes it safe.** Three shapes read as duplication and earn their
place — keep them, and say why in the report.

- **Restated at the point of action.** A rule repeated where it is actually executed, whose definition sits
  phases earlier, is co-location. It's a real duplicate only when the reader is **holding the original right
  now** — same file, or a reference loaded in the same phase.
- **Two sides of one contract.** The same fact told to two audiences — the dispatcher and the worker, the
  caller and the callee — is one meaning with two readers.
- **A defensive check.** Unreachable on the happy path but reachable when a run is interrupted. Not dead.

## A clean pass is a result

An asset pruned recently *should* come back clean. A pass that manufactures findings to look productive is the
failure this section exists to prevent.
