# Answer key — `fixture.md`

Do not read this before running the rewrite. It is the grader, not the brief.

## Planted, and the rewrite must fix all five

| # | Where | The defect |
| --- | --- | --- |
| P1 | reply, first sentence | Three ideas in one sentence, plus the "It should be noted that" filler. Split into one idea per sentence; delete the opener |
| P2 | "The tests should be re-run before the branch is committed by you." | Passive instruction. Flip to imperative: "Re-run the tests before you commit the branch." |
| P3 | "The push should be aborted if the suite fails." | Condition trailing its instruction, passive voice. "If the suite fails, abort the push." |
| P4 | "We might potentially need to utilize" | Stacked hedges plus an ornate word. "We may need to use" — the `` `resolve` `` identifier stays |
| P5 | spec summary | One passive multi-idea sentence. "in an automatic fashion", "at the point in time when", "in order to ensure", and "under any circumstances" are filler. Split into short active sentences |

A fix counts only if the defect is gone, not softened. "The tests should ideally be re-run" does not
settle P2.

## Decoys, and the rewrite must touch none of them

| # | Where | Why touching it is a failure |
| --- | --- | --- |
| D1 | the `` `resolve` `` identifier, "idempotent" | The 20% frees the lexicon. Renaming the identifier, or glossing "idempotent" as "repeatable", loses meaning the style never asked to lose |
| D2 | the CI log quote | Verbatim evidence stays byte-exact. Any cleanup of the quote breaks the evidence rule |
| D3 | the Chinese sentence | Language comes first: the style never switches a language. Translating it to English is the highest-severity failure this eval can produce |

D3 is the one that tests a rule nothing else here tests. Smoothing the Chinese inside Chinese is
allowed; producing English is not.

## Verdict

- All five planted defects fixed, no decoy touched: **pass**.
- Any decoy touched: **fail**, whatever else the rewrite improved. D3 translated: fail, and record it
  as the language guarantee breaking, not as a style slip.
- Rewrites legitimately differ. Grade the defect list, not the wording.
