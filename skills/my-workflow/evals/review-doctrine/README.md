# Eval — the Standards axis against a known diff

`validate_shared_skills.py` checks that the assets are well formed. It cannot tell you whether an edit to
`references/review-doctrine.md` made the review better or worse. This is the instrument that can.

## Run it

Start a session that has not seen this directory, and give the reviewer the diff and the doctrine, nothing
else:

```text
Apply ~/.agents/skills/my-workflow/references/review-doctrine.md to this diff and report findings.
<contents of fixture.diff>
```

The session must be fresh. A reviewer that has already read `expected.md` is grading its own memory, and a
reviewer that watched the diff being written is anchored on why each line is there.

Then open `expected.md` and grade against it.

## What it measures

Five planted defects and three decoys. The decoys are the point. Recall alone is trivial to game — a
reviewer that reports everything scores full marks on the planted set — so the pass condition is recall
**and** silence on the decoys.

This mirrors the rule the doctrine and `AGENTS.md` both state about gates: feed the instrument an input it
must reject before believing it on real work. That cuts both ways, and the first run proved it. One planted
"decoy" turned out to be a real defect, argued better than the key had been written; the key was corrected
rather than the verdict. **A fixture whose answer key is wrong is worse than no fixture**, so treat a
disagreement as a claim about the key until you have read the reasoning and can say which is wrong.

## Its limits, stated plainly

One diff, in one language, graded by reading. It will not detect a small regression, it has no baseline to
compare against, and running it twice can give two answers because the thing under test is stochastic.

It also exercises only part of the doctrine. A bare diff carries no standards file, no git history and no
prior pull request, so the Conventions, History and Prior review reviewers have nothing to read — a run
should say so rather than quietly skip them, and that admission is itself worth checking for.

Treat a failure as a real signal and a pass as weak evidence. To make a pass mean more, add a fixture rather
than re-running this one — a second language, or a diff whose right answer is `clean`, which is the case a
review that manufactures findings fails and this fixture cannot catch.
