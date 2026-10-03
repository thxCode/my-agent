# Writing style — 80% of the way to ASD-STE100

Shared by every `my-*` skill. Apply it to everything a human reads during a run: the
conversation with the user (questions, options, presentations, reviews, summaries), specs,
plans, debug artifacts, triage ledgers and comments, handoffs and handbacks, PR titles and
bodies, and advisory text.

ASD-STE100 is the controlled language written for aerospace maintenance documentation —
text a tired, non-native reader must not misread. Andrej Karpathy's tip: ask a language
model for "80% of the way to ASD-STE100"; full compliance is too stringent, and the
softened form is already far more readable. This file fixes what the 80% keeps and what
it drops.

## The 80% — binding

- One idea per sentence. Short sentences; split anything past ~20 words.
- Active voice. Imperative for instructions — "Run the tests", not "the tests should be run".
- Condition before instruction — "If the suite fails, stop", not "Stop if the suite fails".
- One word, one meaning. The same thing keeps the same name through the whole document.
- The plain word over the ornate one. No filler, no stacked hedges, no metaphor in
  instructions.
- Procedures as numbered steps, one action per step; statements as short bullets.

## The 20% — free

Full STE100 binds an approved dictionary and stricter sentence forms. Keep the ordinary
technical lexicon: domain terms, code identifiers, project and product names stay as they
are. The constraint is on sentence shape, not on vocabulary.

## Language comes first

This rule never picks a language. The skill's Language bullet and the user's interaction
context decide that — a Chinese conversation stays Chinese. STE100 is an English
specification; in any other language, carry the structure, not the lexicon: short
sentences, one idea each, active voice, plain words, condition before instruction.

Before: “需要注意的是，这个迁移可能会潜在地影响到使用旧接口的调用方，因此需要谨慎处理。”

After: “这个迁移可能影响到旧接口的调用方。合并前请检查每个调用点。”

## What it does not touch

- Code and code comments — project conventions rule there.
- Commit message format — `my-build` pins the template; the free-text lines still follow
  this style.
- Verbatim evidence — quotes, logs, and reporter text stay byte-exact (`my-triage`'s
  *Reported* section, archived round output).
- `my-triage`'s reporter-mirror rule — comment prose keeps mirroring the reporter's
  language; this style applies inside whichever language that is.
- Fixed templates and the placeholder text inside them — `my-advisory`'s appendix, the
  spec and triage-ledger skeletons. Their shape is pinned by their consumers.

This family's own instruction text follows the same sentence-shape discipline;
`my-refine`'s style probe audits for it.

## Before / after

Before: "It should be noted that the migration might potentially break existing consumers
of the legacy endpoint, so appropriate care should be taken."

After: "The migration can break callers of the legacy endpoint. Check every call site
before you merge."
