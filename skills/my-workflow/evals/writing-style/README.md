# Eval — the writing style against a known draft

`validate_shared_skills.py` checks that the assets are well formed. It cannot tell you whether
`references/writing-style.md` makes an agent's prose better or worse. This is the instrument that can.

## Run it

Start a session that has not seen this directory. Give the writer the style reference and the
fixture, nothing else:

```text
Apply ~/.agents/skills/my-workflow/references/writing-style.md to the two texts below and rewrite them.
<contents of fixture.md>
```

The session must be fresh. A writer that has already read `expected.md` is grading its own memory.

Then open `expected.md` and grade against it.

## What it measures

Five planted defects and three decoys. The decoys are the point. A writer that rewrites everything
scores full marks on the planted set, so the pass condition is fixing the planted **and** leaving the
decoys alone. One decoy is Chinese prose: translating it to English is the regression the style's
language guarantee exists to prevent, and it is the highest-severity failure this eval can produce.

A disagreement with the key is a claim about the key until you have read the reasoning and can say
which is wrong. A fixture whose answer key is wrong is worse than no fixture.

## Its limits, stated plainly

One short text, in two languages, graded by reading. It will not detect a small regression, and
running it twice can give two answers because the thing under test is stochastic. Treat a failure as
a real signal and a pass as weak evidence. To make a pass mean more, add a fixture rather than
re-running this one — a second register, or a text whose right answer is `already clean`, which is
the case a style-enforcing writer fails by manufacturing defects.
