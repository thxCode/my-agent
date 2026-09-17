# Filing an issue

Read by any `my-*` stage that finds a problem while testing or verifying — `my-build`, `my-crew`, `my-ship`.
This is the **producing** side; `resolve-issue.md` is the consuming side.

The thing this page exists to stop is not a sloppy issue. It is a **well-written issue about a problem nobody
has**.

## The loop

```
we infer a possible failure
  → we write a test that triggers it
    → the test goes red
      → we file an issue
        → we fix it
          → the test goes green
```

Every step is correct. The red is real, the fix is real. **No step in the loop ever touched a user's
behaviour**, so the only thing that was invented is the problem — and that is why it is hard to see from
inside. A loop that closes cleanly feels like work done.

## An issue stands on one of three things

| | What it means |
| --- | --- |
| **Measured** | A run produced it. Readings, exit codes, log lines — something a second person could obtain. |
| **Reported** | Somebody hit it. A user, a colleague, an operator. |
| **Irreversible** | It has not happened, but if it does, nothing recovers: data lost, an object that cannot be deleted, a credential leaked. |

Have one of those → file it, and say which.

## Have none of them? Then it is an inference, and inferences pass three gates

An inference can be perfectly sourced and still not be worth an issue. These are not "fix it or don't" — they
decide **what shape the answer may take**.

**Gate A — Would anyone have a reason to configure this?**

Write out the configuration required to trigger it. If it takes a combination nobody with working knowledge of
the system would assemble, the answer is documentation, not code. State the combination in the issue so the
next reader can judge it too.

**Gate B — Does the fix ask the user to restate something they already know?**

A field that asks which engine a pool serves, which cluster a workload targets, what a component is for — that
adds no information the operator did not already have from whoever configured it. It adds **a second copy that
can disagree with reality**, and then a new problem: what to do when the copy is wrong. If the fix has this
shape, the answer is documentation or a warning, not schema.

**Gate C — Would anyone but us have written this test?**

If the test case was constructed from the inference, its red proves *the inference holds in the code*. It does
not prove the situation occurs. A case whose inputs only we would assemble is a **synthetic scenario**: it may
stay in the suite, but its going red does not by itself become an issue.

> Failing a gate does not mean the problem is unreal. It means the answer belongs in prose, a warning or a
> stamp — **not in an API**. An API commitment is the most expensive answer available and the hardest to
> withdraw.

## What the body must carry

Every issue names its provenance in the body, in one line near the top:

```
Provenance: measured | reported | inferred
```

**Measured** → the reproduction, precise enough that a second person gets the same reading:

- the exact commands, in order, with the flags
- the versions that matter (image tag, chart version, upstream release)
- the shape of the environment — "a three-node cluster, no accelerators" — **never** addresses, IDs,
  hostnames or machine types
- **what the failure looks like**, and what a pass would have looked like. A reading has no meaning without
  the other branch.

**Reported** → who, when, and what they were doing. Link the thread.

**Inferred** → the source of the inference (the code path, the upstream file and line, the table), **and one
line per gate**: who would configure this, what the fix would ask of the user, and whether any test exercising
it is synthetic.

## Inside a build or a crew run

A stage that finds something mid-flight has one more decision: file now, or finish first.

- **File now** if the finding blocks the current work, or if leaving it unfiled means losing the reproduction.
- **Finish first** if it is adjacent. A finding written up two hours later with a clean reproduction beats one
  filed immediately with "saw this once".

Either way: ⛔ **do not fold an unrelated finding into the current change as a drive-by fix.** It arrives
without its own review, and the issue that would have recorded why never gets written.

## The check that catches most of it

Before opening the issue, answer this in one sentence, out loud:

> **Who is worse off today because this is not fixed?**

If the answer names a real position someone occupies — an operator running this, a user hitting that — file
it. If the answer is a hypothetical person doing something nobody does, the finding belongs in a comment
beside the code, where the next person to touch it will read it.
