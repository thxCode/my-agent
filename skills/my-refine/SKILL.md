---
name: my-refine
description: Audit and streamline skills, agent contracts, and workflow references.
disable-model-invocation: true
---

# my-refine

Refine the prompt asset: **the user's current request**

Two jobs, in order: find **conflicts** (two places that disagree, or a rule sitting somewhere it can never fire
or can never be evaluated), then **prune** (cut a word, a phrase, a sentence — behaviour unchanged, tokens
down). Conflicts may change behaviour; prunes may not.

Prompt assets have no test suite, so Phase 6's mechanical checks are the completion criterion.

**Language.** Write asset edits in **English**; talk to the user in their configured language.

## Phase 1 — Scope and baseline

1. **Resolve the target.**
   - **Empty** → the whole family: `~/.agents/skills/my-*/SKILL.md`, `~/.agents/skills/my-workflow/references/**/*.md`,
     and `~/.claude/agents/*.md`. Read them **all in one pass** — a cross-file probe needs the whole set in view at
     once.
   - **A path** (a `skills/<name>/SKILL.md`, an agent, any file) → read it plus anything it points at. A single
     file has no cross-file surface: run Phase 3 in full, and from Phase 2 run only **Unenforced promise** and
     the pointer half of **Unreachable rule**. Say which probes are out of scope for this target.
2. **Baseline.** `git status --porcelain` — an unclean tree means the diff at the end won't be yours alone, so
   ask how to handle it first. Record `wc -c` for every file in scope; Phase 7 reports against it.

## Phase 2 — Conflict probes

Five probes. Each is a search you run, not an impression you form. Work them in order and record what each
returned, including the empty ones.

| Probe | The defect | How to run it |
| --- | --- | --- |
| **Unreachable rule** | A rule guarded by a condition its own load path already excluded | For each conditionally-loaded file, write down what the loader guarantees before it fires. Then grep that file for rules re-handling a case the guarantee rules out |
| **Unknowable gate** | A gate keyed on state the reader can't observe at the moment it reads | For each `only when` / `only if` / `after X only`, ask where its input comes from at that moment: conversation (may have been compacted away), disk, or git. Conversation-only across a session boundary → swap in an observable proxy |
| **Unenforced promise** | A declared field or claim whose consumers are narrower than the claim, or absent | Grep every custom annotation (`Gate:`, `Owns:`, `Blocked by:`, `Status:`) family-wide for who reads it. Compare each claim's scope against its consumers' |
| **Stale universal** | An absolute written before a newer branch existed | Identify the most recently added branch or mode. Grep the older text for `always`, `every`, `each`, `never`, `at a time`, `all modes`, and evaluate each against that new branch |
| **Incomplete enumeration** | A case list that fell behind its authoritative table | Find the authoritative enumeration (a mode table, a status ladder). Grep every other place enumerating the same set. Diff the member lists |

**A finding needs both ends.** Cite `file:line` for the rule *and* for what it contradicts. One end and a
feeling is an opinion — drop it.

## Phase 3 — Prune probes

Read `~/.agents/skills/my-workflow/references/skill-craft.md` and
`~/.agents/skills/my-workflow/references/prompt-hygiene.md`, then work both over every file in scope. In
particular, distinguish observable verification from generic verification rituals, and remove provider-specific
model or effort controls from shared assets.

The unit of change is **one word, one phrase, one sentence.** Rewriting a paragraph, restructuring phases, or
touching a user-confirmation gate is a different job than this one.

Every candidate cut clears the **burden of proof** in that file's *What to leave alone*: name what makes it
safe — is the reader holding the original right now? If you can't answer, keep the line and list it in Phase 4's
third column.

## Phase 4 — Report, and predict

Three lists, numbered separately:

1. **Conflicts** — each with both ends and the fix.
2. **Cuts** — each with the exact before and after text.
3. **Left alone** — each with the burden-of-proof reason it survived.

Then **predict the byte delta**. All three lists empty → report a **clean pass**: name every probe you ran and
what it returned, and stop here.

## Phase 5 — Confirm, then edit

Wait for confirmation — per item, or a batch approval covering a whole list. Then apply only what was approved.

Deleting an item from a numbered list shifts every ordinal after it: grep the whole file for cross-references
into that list (`item 3`, `items 2–4`, `Phase 2.5`) and fix them in the same pass. Prefer replacing a fragile
ordinal reference with the thing it names.

## Phase 6 — Verify mechanically

Every check runs. Report the actual output, not a claim about it.

```bash
# 1 — frontmatter parses as strict YAML and every directory-form skill has name + description
python3 -c "
import yaml,sys
for f in sys.argv[1:]:
    d=yaml.safe_load(open(f).read().split('---\n',2)[1]); assert isinstance(d,dict), f
    print('ok',f,list(d))
" <files>

# 2 — pointers resolve both ways: every referenced file exists, every reference file is cited at least once
# 3 — ordinals: no stale 'item N' / 'items N–M' left pointing at a renumbered list
# 4 — each fixed conflict: the old wording greps empty, the new wording is present
# 5 — untouched-by-design blocks (a tested bash snippet, a template) are byte-identical in `git diff`
# 6 — wc -c, before and after
# 7 — the shared validator passes for changed my-* skills; quick_validate.py passes for changed standard-only skills
# 8 — no legacy prompt placeholders, stale command paths, provider model names, generic reasoning rituals, or host-specific team tools remain in shared workflow files
```

## Phase 7 — Report

Give **predicted and actual** byte delta, both numbers. When the actual undershoots, say so plainly — the
predict-then-reconcile step is what keeps a small result from being written up as a large one.

Close with what you left alone and why. That list is the evidence the pass exercised judgement rather than
manufacturing findings.
